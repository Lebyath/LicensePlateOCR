import cv2
import imutils
import pytesseract
import os
import winsound
from skimage.filters import threshold_otsu, gaussian

class LicensePlateDetector:
    def __init__(self):
        pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
        if not os.path.exists("CarPictures"):
            os.makedirs("CarPictures")
        self.filename = None

    def capture_license_plate(self):
        vid = cv2.VideoCapture(0)
        count = 0
        while True:
            ret, image = vid.read()
            cv2.imshow('image', image)
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                self.filename = "CarPictures/car{}.jpg".format(count)
                cv2.imwrite(self.filename, image)
                count += 1
                break
        vid.release()
        cv2.destroyAllWindows()

    def load_image(self):
        image = cv2.imread(self.filename)
        return imutils.resize(image, width=500)

    def convert_to_grayscale(self, image):
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        gray = cv2.bilateralFilter(gray, 11, 17, 17)
        return gray

    def apply_gaussian_filter(self, image):
        return gaussian(image, sigma=1)

    def find_license_plate(self, image):
        edged = cv2.Canny(image, 170, 200)
        cnts, _ = cv2.findContours(edged.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
        cnts = sorted(cnts, key=cv2.contourArea, reverse=True)[:30]
        LicensePlateCount = None
        for c in cnts:
            perimeter = cv2.arcLength(c, True)
            approx = cv2.approxPolyDP(c, 0.02 * perimeter, True)
            if len(approx) == 4:
                LicensePlateCount = approx
                x, y, w, h = cv2.boundingRect(c)
                crp_img = image[y:y + h, x:x + w]
                cv2.imwrite("crop.jpg", crp_img)
                break
        return LicensePlateCount

    def draw_contour_on_image(self, image, LicensePlateCount):
        cv2.drawContours(image, [LicensePlateCount], -1, (0, 255, 0), 3)

    def read_license_plate(self):
        img = cv2.imread('crop.jpg', cv2.IMREAD_GRAYSCALE)
        thresh = cv2.adaptiveThreshold(img, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2)
        text = pytesseract.image_to_string(thresh, lang='eng')
        return ''.join(e for e in text if e.isalnum())


    def write_to_database(self, text):
        with open("database.txt", "a", encoding="utf-8") as f:
            f.write(text + "\n")

    def check_database(self, text):
        with open("database.txt", 'r') as read_obj:
            for line in read_obj:
                if text in line:
                    return True
            return False

    def play_beep(self):
        frequency = 2500
        duration = 1000
        winsound.Beep(frequency, duration)

    def detect_license_plate(self):
        self.capture_license_plate()
        image = self.load_image()
        gray = self.convert_to_grayscale(image)
        LicensePlateCount = self.find_license_plate(gray)
        self.draw_contour_on_image(image, LicensePlateCount)
        plate_strings = []
        while len(plate_strings) < 24 or len(set(plate_strings)) > 1:
            text = self.read_license_plate()
            plate_strings.append(text)
            if len(plate_strings) >= 24 and len(set(plate_strings)) == 1:
                break
        text = plate_strings[0]
        self.write_to_database(text)
        if self.check_database(text):
            self.play_beep()
        print("License plate:", text)
