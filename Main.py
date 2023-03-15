import cv2
import imutils
import pytesseract
import os
import winsound

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# Define function to check if string is in file
def check_if_string_in_file(file_name, string_to_search):
    with open(file_name, 'r') as read_obj:
        for line in read_obj:
            if string_to_search in line:
                return True
        return False

# Create directory to store images
if not os.path.exists("CarPictures"):
    os.makedirs("CarPictures")

# Capturing number plate of vehicle. Use quality camera for more accurate results.
vid = cv2.VideoCapture(0)
count = 0
while True:
    ret, image = vid.read()
    cv2.imshow('image', image)
    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        # Save image to disk with unique name
        filename = "CarPictures/car{}.jpg".format(count)
        cv2.imwrite(filename, image)
        count += 1
        break
vid.release()
cv2.destroyAllWindows()

# Load the latest saved image
image = cv2.imread(filename)

# Resize image
image = imutils.resize(image, width=500)

# Convert image to grayscale
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

# Reduce noise and smooth image
gray = cv2.bilateralFilter(gray, 11, 17, 17)

# Find edges in image
edged = cv2.Canny(gray, 170, 200)

# Find contours in image
cnts, _ = cv2.findContours(edged.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

# Sort contours by area and keep the top 30
cnts = sorted(cnts, key=cv2.contourArea, reverse=True)[:30]
NumberPlateCount = None

# Loop through contours to find the number plate
for c in cnts:
    perimeter = cv2.arcLength(c, True)
    approx = cv2.approxPolyDP(c, 0.02 * perimeter, True)
    if len(approx) == 4:
        NumberPlateCount = approx
        x, y, w, h = cv2.boundingRect(c)
        crp_img = image[y:y + h, x:x + w]
        cv2.imwrite("crop.jpg", crp_img)
        break

# Draw contour of number plate on original image
cv2.drawContours(image, [NumberPlateCount], -1, (0, 255, 0), 3)

# Read cropped image and convert to text using pytesseract
text = pytesseract.image_to_string('crop.jpg', lang='eng')
text = ''.join(e for e in text if e.isalnum())

# Check if the number is in the database
if check_if_string_in_file("database.txt", text):
    # Play beep sound
    frequency = 2500  # Set frequency in Hz
    duration = 1000  # Set duration in ms
    winsound.Beep(frequency, duration)

print("Number is:", text)

def check_if_string_in_file(file_name, string_to_search):
    with open(file_name, 'r') as read_obj:
        for line in read_obj:
            if string_to_search in line:
                return True
        return False

if check_if_string_in_file("database.txt", text):
    # Play beep sound
    frequency = 2500 # Set frequency in Hz
    duration = 1000 # Set duration in ms
    winsound.Beep(frequency, duration)

print("Number is:", text)