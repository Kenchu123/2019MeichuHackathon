from tabula import read_pdf, convert_into
import pdfplumber
import json
from parse_diagram import get_text, merge_overlapped, split_objs, split_pin_and_number, match_pin_and_number, merge_pins_mapped_to_same_number
import re

table_settings = {
    "vertical_strategy": "lines", 
    "horizontal_strategy": "lines",
    "explicit_vertical_lines": [],
    "explicit_horizontal_lines": [],
    "snap_tolerance": 3,
    "join_tolerance": 3,
    "edge_min_length": 3,
    "min_words_vertical": 5,
    "min_words_horizontal": 5,
    "keep_blank_chars": True,
    "text_tolerance": 3,
    "text_x_tolerance": None,
    "text_y_tolerance": None,
    "intersection_tolerance": 3,
    "intersection_x_tolerance": None,
    "intersection_y_tolerance": None,
}
# print(pdf.pages[6].extract_text())
class PDF_PARSER:
    def __init__(self, src_path, out_path):
        self.src_path = src_path
        self.out_path = out_path
        self.diction = {'pin' : [] , 'name' : []}
        self.s = dict()
    def insert(self, k, pi, ty = "", des = ""):
        self.s[k] = {"pin" : [] , "type" : ""  , "description" : ""} if k not in self.s else self.s[k]
        self.s[k]["pin"].append(pi)
        self.s[k]["type"] = ty
        self.s[k]["description"] = des
    def ispin(self, vec):
        for v in vec:
            if v == None or v not in self.diction['pin']:
                return False
        return True 
    def isname(self, vec):
        for v in vec:
            if v == None or v not in self.diction['name']:
                return False
        return True 
    def istype(self, vec):
        string = ''.join(vec)
        return string.find('I') != -1 or string.find('i') != -1 or string.find('O') != -1 or string.find('i') != -1
    def isdescript(self, vec):
        return len(' '.join(vec)) > 15
    # def search_page(self, path, diction, default = 0):
    #     if default != 0:
    #         return default
    #     with pdfplumber.open(path) as pdf:
    #         for pages in pdf.pages:
    #             ff = pages.extract_text()
    #             for v in diction:
    def parse_img(self, page, x1, y1, x2, y2):
        textboxes = get_text(self.src_path, page, (x1, y1, x2, y2))

        merge_overlapped(textboxes)
        textboxes = split_objs(textboxes)
        pins, numbers = split_pin_and_number(textboxes)

        result = match_pin_and_number(pins, numbers)
        merge_pins_mapped_to_same_number(result)
        result = {k: v.text for k, v in result.items()}
        for key in result: 
            self.diction['pin'].append(key)
            self.diction['name'].append(result[key])

    def output_json(self, page, x1, y1, x2, y2):
        self.parse_img(page, x1, y1, x2, y2)
        with pdfplumber.open(self.src_path) as pdf:
            for pages in pdf.pages:
                for pdf_table in pages.extract_tables(table_settings = table_settings):
                    for row in pdf_table:
                        tp, have_pin, have_name, have_type, have_des = list(), -1, -1, -1, -1 
                        for ind, ele in enumerate(row):
                            tp.append(str(ele).replace('\t',  ' ').replace(',', '\n').replace('\n\n', '\n').replace(' ', '').split('\n'))
                            if self.ispin(tp[-1]):
                                have_pin = ind
                            if self.isname(tp[-1]):
                                have_name = ind
                            if self.istype(tp[-1]):
                                have_type = ind
                            if self.isdescript(tp[-1]):
                                have_des = ind
                        if have_pin == -1 or have_name == -1:
                            continue
                        #print(row)
                        #print(have_name, have_pin, have_type, have_des)
                        for ele in tp:
                            for name in ele[have_name]:
                                self.insert(name, row[have_pin], row[have_type], row[have_des])

        with open(self.out_path, 'w') as fp:
            fp.write(json.dumps(self.s, indent = 4, sort_keys = False))
                
if __name__ == "__main__":
    src_path = ('ds093.pdf')
    out_path = ('output1.json')
    parser = PDF_PARSER(src_path, out_path)
    parser.output_json(16, 0, 329, 612, 740)