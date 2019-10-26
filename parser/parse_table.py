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
from pdfminer.layout import LAParams, LTTextBox, LTTextLine, LTFigure, LTImage, LTTextBoxHorizontal, LTAnno, LTChar


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


def get_table_bound(textboxes):
    l = b = float('inf')
    t = r = 0
    for textbox in textboxes:
        x0, y0, x1, y1 = textbox.bbox
        l = min(l, x0)
        b = min(b, y0)
        r = max(r, x1)
        t = max(t, y1)
    return l, b, r, t


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


def split_objs(textboxes, table_w, table_h):
    ret = []
    for textbox in textboxes:
        x0, y0, x1, y1 = textbox.bbox
        text = textbox.get_text().strip()
        # First whitespace character
        sep = next((c for c in text if c.isspace()), None)
        width = x1 - x0
        height = y1 - y0
        if not sep:
            # if there is not whitespace
            if (width < table_w / 2 and height < table_h / 2):
                # if the box itself is too small
                is_vertical = not isinstance(textbox, LTTextBoxHorizontal)
                ret.append(TextObject(text, textbox.bbox, is_vertical))
                continue
        arr = [char for char in textbox._objs[0] if isinstance(char, LTChar)]

        if isinstance(textbox, LTTextBoxHorizontal):
            if sep == '\n':
                arr.sort(key=lambda c: c.bbox[1], reverse=True)
                arr = [i.get_text() for i in arr if not i.get_text().isspace()]
                approx_h = height / len(arr)
                # evenly divide in vertical direction
                for index, txt in enumerate(arr):
                    ret.append(TextObject(
                        txt, (x0, y1 - (index+1)*approx_h, x1, y1 - index*approx_h), is_vertical=False))
            else:
                arr.sort(key=lambda c: c.bbox[0])
                arr = [i.get_text() for i in arr if not i.get_text().isspace()]
                approx_w = width / len(arr)
                # evenly divide in horizontal direction
                for index, txt in enumerate(arr):
                    ret.append(TextObject(
                        txt, (x0+index*approx_w, y0, x0+(index+1)*approx_w, y1), is_vertical=False))
        else:  # Vertical text
            if sep != '\n':
                arr.sort(key=lambda c: c.bbox[1], reverse=True)
                arr = [i.get_text() for i in arr if not i.get_text().isspace()]
                approx_h = height / len(arr)
                # evenly divide in vertical direction
                for index, txt in enumerate(arr):
                    ret.append(TextObject(
                        txt, (x0, y1 - (index+1)*approx_h, x1, y1 - index*approx_h), is_vertical=True))
            else:
                arr.sort(key=lambda c: c.bbox[1])
                arr = [i.get_text() for i in arr if not i.get_text().isspace()]
                approx_w = width / len(arr)
                # evenly divide in horizontal direction
                for index, txt in enumerate(arr):
                    ret.append(TextObject(
                        txt, (x0+index*approx_w, y0, x0+(index+1)*approx_w, y1), is_vertical=False))
    return ret


def midpoint(box):
    x0, y0, x1, y1 = box
    return ((x0+x1)/2, (y0+y1)/2)


def aligned(a, b):
    a_left, a_bottom, a_right, a_top = a
    b_left, b_bottom, b_right, b_top = b
    return a_left == b_left or a_bottom == b_bottom or a_right == b_right or a_top == b_top


def plot_object(lst):
    xs = []
    ys = []
    for i in lst:
        x, y = midpoint(i.bbox)
        xs.append(x)
        ys.append(y)
    plt.scatter(xs, ys)
    plt.show()


def extract_header(textboxes, bound):
    header1 = []
    header2 = []
    rest = []
    min_x, max_x, min_y, max_y = 0, float('inf'), 0, float('inf')
    for textbox in textboxes:
        text = textbox.text
        if all(c.isdigit() for c in text):
            header2.append(textbox)
        elif len(text) == 1:
            header1.append(textbox)
            x0, y0, x1, y1 = textbox.bbox
            min_x = min(min_x, x0)
            max_x = max(max_x, x1)
            min_y = min(min_y, y0)
            max_y = max(max_y, y1)
        else:
            rest.append(textbox)
    delta_x = max_x - min_x
    delta_y = max_y - min_y
    if delta_x < delta_y:
        # header1 is x header
        return header1, header2, rest
    else:
        return header2, header1, rest


def sweep_2d_array(data, x_count, y_count, min_x, max_y, delta_x, delta_y):
    ret = [[None for _ in range(x_count)] for _ in range(y_count)]
    min_x -= delta_x / 2  # account for midpoint loss
    max_y += delta_y / 2
    for text_obj in data:
        y = round((max_y - text_obj.y()) / delta_y) - 1
        x = round((text_obj.x() - min_x) / delta_x) - 1
        ret[y][x] = text_obj
    return ret


if __name__ == '__main__':
    # textboxes = get_text('../data/TLK2711.pdf', 2, (0, 460, 612, 693))
    # textboxes = get_text('../data/42-45S83200G-16160G.pdf', 4, (0, 300, 612, 660))
    textboxes = get_text(
        '../data/66-67WVE2M16EALL-BLL-CLL.pdf', 2, (0, 383, 612, 664))

    bound = get_table_bound(textboxes)
    x0, y0, x1, y1 = bound
    table_w = x1 - x0
    table_h = y1 - y0

    result = split_objs(textboxes, table_w, table_h)
    # TODO use set to record header to avoid duplicate
    header_x, header_y, data = extract_header(result, bound)
    header_x.sort(key=TextObject.x)
    header_y.sort(key=TextObject.y, reverse=True)

    data_bound = get_table_bound(data)

    x_count = len(header_x)
    y_count = len(header_y)
    d_x0, d_y0, d_x1, d_y1 = data_bound
    data_w = d_x1 - d_x0
    data_h = d_y1 - d_y0
    h_delta = data_h / y_count
    w_data = data_w / x_count

    arr_2d = sweep_2d_array(data, x_count, y_count,
                            d_x0, d_y1, w_data, h_delta)

    result = {}
    for row_ind, row in enumerate(arr_2d):
        for col_ind, i in enumerate(row):
            if not i:  # empty block
                continue
            id = '{}{}'.format(header_y[row_ind].text, header_x[col_ind].text)
            if i.text not in result:
                result[i.text] = []
            result[i.text].append(id)
    pprint(result)
