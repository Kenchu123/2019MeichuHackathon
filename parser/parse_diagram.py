from pprint import pprint
import math

import matplotlib.pyplot as plt
from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfpage import PDFTextExtractionNotAllowed
from pdfminer.pdfinterp import PDFResourceManager
from pdfminer.pdfinterp import PDFPageInterpreter
from pdfminer.pdfdevice import PDFDevice
from pdfminer.layout import LAParams
from pdfminer.converter import PDFPageAggregator
from pdfminer.layout import LAParams, LTTextBox, LTTextLine, LTFigure, LTImage, LTTextBoxHorizontal, LTAnno


def in_range(box, range):
    x0, y0, x1, y1 = box
    b_x0, b_y0, b_x1, b_y1 = range
    return x0 >= b_x0 and y0 >= b_y0 and x1 <= b_x1 and y1 <= b_y1


def get_text(filename, page_number, range=(0, 0, 612, 792), detect_vertical=True):
    with open(filename, 'rb') as fp:
        # Create a PDF resource manager object that stores shared resources.
        rsrcmgr = PDFResourceManager()
        # Create a PDF page aggregator object.
        laparams = LAParams(detect_vertical=detect_vertical)
        device = PDFPageAggregator(rsrcmgr, laparams=laparams)
        # Create a PDF interpreter object.
        interpreter = PDFPageInterpreter(rsrcmgr, device)

        page = next(PDFPage.get_pages(fp, pagenos=set([page_number])))
        interpreter.process_page(page)
        layout = device.get_result()

    text_in_range = [obj for obj in layout if isinstance(
        obj, LTTextBox) and in_range(obj.bbox, range)]

    return text_in_range


class TextObject:
    def __init__(self, text, bbox, is_vertical):
        self.text = text
        self.bbox = bbox
        self.is_vertical = is_vertical

    def __repr__(self):
        center_x = (self.bbox[0] + self.bbox[2]) / 2
        center_y = (self.bbox[1] + self.bbox[3]) / 2
        return 'TextObject({}, ({:.2f}, {:.2f}) -> ({:.2f}, {:.2f}), {})'.format(self.text, *self.bbox, 'v' if self.is_vertical else 'h')
        # return 'TextObject({}, ({:.2f}, {:.2f}), {})'.format(self.text, center_x, center_y, 'v' if self.is_vertical else 'h')

    def approx_fontsize(self):
        x0, y0, x1, y1 = self.bbox
        w = x1 - x0
        h = y1 - y0
        return w*h / len(self.text)

    def x(self):
        return (self.bbox[0] + self.bbox[2]) / 2

    def y(self):
        return (self.bbox[1] + self.bbox[3]) / 2


def split_objs(textboxes):
    ret = []
    for textbox in textboxes:
        x0, y0, x1, y1 = textbox.bbox
        text = textbox.get_text().strip()
        # First whitespace character
        sep = next((c for c in text if c.isspace()), None)
        arr = text.split()  # split by whitespace
        width = x1 - x0
        height = y1 - y0
        # TODO
        if isinstance(textbox, LTTextBoxHorizontal):
            if sep == '\n':
                approx_h = height / len(arr)
                # evenly divide in vertical direction
                for index, txt in enumerate(arr):
                    ret.append(TextObject(
                        txt, (x0, y1 - (index+1)*approx_h, x1, y1 - index*approx_h), is_vertical=False))
            else:
                approx_w = width / len(arr)
                # evenly divide in horizontal direction
                for index, txt in enumerate(arr):
                    ret.append(TextObject(
                        txt, (x1-(index+1)*approx_w, y0, x1-index*approx_w, y1), is_vertical=False))
        else:  # Vertical text
            if sep != '\n':
                approx_h = height / len(arr)
                # evenly divide in vertical direction
                for index, txt in enumerate(arr):
                    ret.append(TextObject(
                        txt, (x0, y1 - (index+1)*approx_h, x1, y1 - index*approx_h), is_vertical=True))
            else:
                approx_w = width / len(arr)
                # evenly divide in horizontal direction
                for index, txt in enumerate(arr):
                    ret.append(TextObject(
                        txt, (x1-(index+1)*approx_w, y0, x1-index*approx_w, y1), is_vertical=True))
    return ret


def overlapped(a, b):
    a_left, a_bottom, a_right, a_top = a
    b_left, b_bottom, b_right, b_top = b
    return not (a_bottom > b_top or a_top < b_bottom or a_right < b_left or a_left > b_right)


def aligned(a, b):
    a_left, a_bottom, a_right, a_top = a
    b_left, b_bottom, b_right, b_top = b
    return a_left == b_left or a_bottom == b_bottom or a_right == b_right or a_top == b_top


def distance(a, b):
    a_left, a_bottom, a_right, a_top = a
    b_left, b_bottom, b_right, b_top = b
    a_mid_x = (a_left + a_right) / 2
    a_mid_y = (a_top + a_bottom) / 2
    b_mid_x = (b_left + b_right) / 2
    b_mid_y = (b_top + b_bottom) / 2
    return math.hypot(a_mid_x - b_mid_x, a_mid_y - b_mid_y)


def merge_overlapped(textboxes):
    merged_textboxes = []
    for i_ind, i in enumerate(textboxes):
        for j_ind in range(i_ind+1, len(textboxes)):
            j = textboxes[j_ind]
            if i is not j and overlapped(i.bbox, j.bbox) and aligned(i.bbox, j.bbox):
                x0, y0, x1, y1 = j.bbox
                delta = (y1 - y0) / len(j._objs)
                anno = i._objs[-1]._objs.pop()  # remove \n from i temporarily
                cutted = j._objs[0]._objs.pop(0)  # remove 0 from j
                i._objs[-1]._objs.append(cutted)  # add 0 from j to i
                i._objs[-1]._objs.append(anno)  # restore \n in i
                j._objs.pop(0)  # remove unused '\n' (or ' ') in j
                j.bbox = (x0, y0, x1, y1 - delta)  # fix up y1 of j


def split_pin_and_number(textboxes):
    pins = []
    numbers = []
    for textbox in textboxes:
        text = textbox.text
        if text.isdigit():
            numbers.append(textbox)
        else:
            pins.append(textbox)
    return pins, numbers


def match_pin_and_number(pins, numbers):
    l, b, t, r = find_pos_maxima(numbers)
    x_limit = (r - l) / 2
    y_limit = (t - b) / 2

    ret = {num.text: [] for num in numbers}
    for pin in pins:
        nearest = None
        shortest_dist = float('inf')
        for number in numbers:
            dist = distance(pin.bbox, number.bbox)
            if dist < shortest_dist:
                shortest_dist = dist
                nearest = number.text
        ret[nearest].append(pin)
    return ret


def find_pos_maxima(numbers):
    leftmost = 0
    rightmost = 0
    top = 0
    bottom = 0
    for num in numbers:
        x0, y0, x1, y1 = num.bbox
        leftmost = min(leftmost, x0)
        rightmost = max(rightmost, x1)
        top = max(top, y1)
        bottom = min(bottom, y0)
    return leftmost, bottom, top, rightmost


def midpoint(box):
    x0, y0, x1, y1 = box
    return ((x0+x1)/2, (y0+y1)/2)


def merge_pins_mapped_to_same_number(map):
    for num, group in map.items():
        if len(group) == 1:
            map[num] = group[0]
            continue
        # ref_fontsize = group[0].approx_fontsize() # assume first character is not subscript/superscript
        # TODO deal with superscript and subscript
        merged = TextObject('', (float('inf'), float('inf'), 0, 0), True)
        # calculate merged dimension
        for text_obj in group:
            m_x0, m_y0, m_x1, m_y1 = merged.bbox
            x0, y0, x1, y1 = text_obj.bbox
            merged.bbox = (min(m_x0, x0), min(m_y0, y0),
                           max(m_x1, x1), max(m_y1, y1))
        x0, y0, x1, y1 = text_obj.bbox
        w = x1 - x0
        h = y1 - y0
        if w < h:
            # is vertical
            group.sort(key=TextObject.y)  # sort by y
        else:
            # is horizontal
            merged.is_vertical = False
            group.sort(key=TextObject.x)  # sort by x
        merged.text = ''.join(i.text for i in group)
        map[num] = merged


def plot_object(lst):
    xs = []
    ys = []
    for i in lst:
        x, y = midpoint(i.bbox)
        xs.append(x)
        ys.append(y)
    plt.scatter(xs, ys)
    plt.show()


if __name__ == '__main__':
    # textboxes = get_text('../data/42-45S83200G-16160G.pdf',2, (0, 274, 612, 650))
    # textboxes = get_text('../data/TLK2711.pdf', 2, (0, 90, 612, 422))
    textboxes = get_text('../data/ds093.pdf', 16, (0, 329, 612, 740))

    merge_overlapped(textboxes)
    textboxes = split_objs(textboxes)
    pins, numbers = split_pin_and_number(textboxes)
    result = match_pin_and_number(pins, numbers)
    merge_pins_mapped_to_same_number(result)

    pprint(result)
    plot_object(result.values())
