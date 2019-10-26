# import tabula

# df = tabula.read_pdf('../data/TLK2711.pdf', page=2)
# print(df)

# ================================

# import PyPDF2
# with open('../data/TLK2711.pdf', 'rb') as pdfFile:
#     pdf = PyPDF2.PdfFileReader(pdfFile)
#     if pdf.isEncrypted:
#         pdf.decrypt('')

#     page = pdf.getPage(2)
#     print(page.extractText())

# ==================================
from pprint import pprint

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

        if isinstance(text, LTTextBoxHorizontal):
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
                        txt, (x1-(index+1)*approx_w, y0, x1-index*approx_w, y1), is_vertical=True))
        else:  # Vertical text
            if sep == '\n':
                approx_w = width / len(arr)
                # evenly divide in horizontal direction
                for index, txt in enumerate(arr):
                    ret.append(TextObject(
                        txt, (x1-(index+1)*approx_w, y0, x1-index*approx_w, y1), is_vertical=True))
            else:
                approx_h = height / len(arr)
                # evenly divide in vertical direction
                for index, txt in enumerate(arr):
                    ret.append(TextObject(
                        txt, (x0, y1 - (index+1)*approx_h, x1, y1 - index*approx_h), is_vertical=False))
    return ret


def overlapped(a, b):
    a_left, a_bottom, a_right, a_top = a
    b_left, b_bottom, b_right, b_top = b
    return not (a_bottom > b_top or a_top < b_bottom or a_right < b_left or a_left > b_right)


def aligned(a, b):
    a_left, a_bottom, a_right, a_top = a
    b_left, b_bottom, b_right, b_top = b
    return a_left == b_left or a_bottom == b_bottom or a_right == b_right or a_top == b_top


def merge_overlapped(textboxes):
    merged_textboxes = []
    for i_ind, i in enumerate(textboxes):
        for j_ind in range(i_ind+1, len(textboxes)):
            j = textboxes[j_ind]
            if i is not j and overlapped(i.bbox, j.bbox) and aligned(i.bbox, j.bbox):
                anno = i._objs[-1]._objs.pop()  # remove \n from i temporarily
                cutted = j._objs[0]._objs.pop(0)  # remove 0 from j
                i._objs[-1]._objs.append(cutted)  # add 0 from j to i
                i._objs[-1]._objs.append(anno)  # restore \n in i
                j._objs.pop(0)  # remove unused '\n' (or ' ') in j


if __name__ == '__main__':
    # textboxes = get_text('../data/42-45S83200G-16160G.pdf', 2, (0, 274, 612, 650))
    textboxes = get_text('../data/TLK2711.pdf', 2, (0, 90, 612, 422))
    # textboxes = get_text('../data/ds093.pdf', 16, (0, 329, 612, 740))

    # pprint(split_objs(textboxes))
    merge_overlapped(textboxes)

    pprint(textboxes)
