from pdf2image import convert_from_path
import sys

def ImageCapture(path, page, size, pos, out_path):
    print("Start Capture Image")
    images = convert_from_path(path, dpi=300, first_page=page, single_file=True, fmt='png', size = size)
    image = images[0]
    width, height = image.size
    x1, y1, x2, y2 = pos
    y1 = height - y1
    y2 = height - y2
    cropImg = image.crop((x1, y2, x2, y1))
    cropImg.save(out_path)
    print("Image Capture Finish!")
    return cropImg

if __name__ == '__main__':
    # name = 'ds093'
    # page = 17
    width = 612
    height = 792
    # x1, y1, x2, y2 = 0, 658, 1224, 1480 # left lower to right upper
    name, page, x1, y1, x2, y2 = sys.argv[1], int(sys.argv[2]), float(sys.argv[3]), float(sys.argv[4]), float(sys.argv[5]), float(sys.argv[6])
    print(sys.argv)
    # return Croped Img
    path = ''.join(('../uploads/', name, '.pdf'))
    out_path = ''.join(('../pictures/', name, '.png'))
    cropImg = ImageCapture(path, page, (width, height), (x1, y2, x2, y1), out_path)
    # cropImg.show()