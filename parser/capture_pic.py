from pdf2image import convert_from_path

def ImageCapture(path, page, size, pos, out_name):
    images = convert_from_path(path, dpi=300, first_page=page, single_file=True, fmt='png', size = size)
    image = images[0]
    width, height = image.size
    x1, y1, x2, y2 = pos
    y1 = height - y1
    y2 = height - y2
    cropImg = image.crop((x1, y2, x2, y1))
    cropImg.save(out_name)
    return cropImg

if __name__ == '__main__':
    width = 1224
    height = 1584
    x1, y1, x2, y2 = 0, 658, 1224, 1480 # left lower to right upper
    # return Croped Img
    cropImg = ImageCapture('../data/ds093.pdf', 17, (width, height), (x1, y1, x2, y2), 'test.png')
    cropImg.show()