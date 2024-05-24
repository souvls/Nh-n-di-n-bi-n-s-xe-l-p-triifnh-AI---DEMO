from tkinter import *
from tkinter import messagebox, filedialog
import cv2
from easyocr import Reader
from PIL import Image, ImageTk
from datetime import date
import winsound

harcascade = "model/haarcascade_russian_plate_number.xml"
min_area = 500
count = 0
array_list = []

def open_file_dialog():
    file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg;*.jpeg;*.png;*.gif;*.bmp")])
    if file_path:
        load_and_display_image(file_path)
        picture = cv2.imread(file_path)
        #cv2.imshow("img",picture)
        result = processIMG(picture)
        if result != "":
            winsound.Beep(1000, 500)
            data = [date.today(),result]
            listBox.insert(0,data)



def load_and_display_image(file_path):
    image = Image.open(file_path)
    image.thumbnail((300,300)) 
    photo = ImageTk.PhotoImage(image)
    label.config(image=photo)
    label.image = photo

def processIMG(img):
    try:
        img = cv2.resize(img, (800, 600))
        grayscale = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(grayscale, (5, 5), 0)
        edged = cv2.Canny(blurred, 10, 200)
        contours, _ = cv2.findContours(edged, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        contours = sorted(contours, key = cv2.contourArea, reverse = True)[:5]

        number_plate_shape = None
        for c in contours:
            perimeter = cv2.arcLength(c, True)
            approximation = cv2.approxPolyDP(c, 0.02 * perimeter, True)
            if len(approximation) == 4: # rectangle
                number_plate_shape = approximation
                break
        (x, y, w, h) = cv2.boundingRect(number_plate_shape)
        number_plate = grayscale[y:y + h, x:x + w]

        reader = Reader(['en'])
        detection = reader.readtext(number_plate)
        if len(detection) == 0:
            return ""
        else:
            text = f"{detection[0][1]}"
            return text
    except:
        messagebox.showerror("Error", "No plate number")
        return ""


def openCamera():
    
    cap = cv2.VideoCapture(0)
    # cap.set(cv2.CAP_PROP_FRAME_WIDTH, 800)
    # cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 600)

    if not cap.isOpened():
        messagebox.showerror("Error", "Cannot open camera")
    
    while True:
        ret, img = cap.read()
        plate_cascade = cv2.CascadeClassifier(harcascade)
        img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        plates = plate_cascade.detectMultiScale(img_gray, 1.1, 4)

        for (x,y,w,h) in plates:
            area = w * h
            if area > min_area:
                cv2.rectangle(img, (x,y), (x+w, y+h), (0,255,0), 2)
                cv2.putText(img, "Number Plate", (x,y-5), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, (255, 0, 255), 2)

                # img_roi = img[y: y+h, x:x+w]
                # cv2.imshow("ROI", img_roi)
        cv2.imshow('Scan plate number', img)
        # cv2.imshow('process1', grayscale)
        # cv2.imshow('process2', edged)

        if not ret:
            break
        if cv2.waitKey(1) & 0xFF == ord('e'):
            break
        if cv2.waitKey(1) & 0xFF == ord('c'):
            result = processIMG(img)
            if result != "":
                cv2.imshow("capture",img)
                winsound.Beep(1000, 500)
                data = [date.today(),result]
                listBox.insert(0,data)
                break
            else:
                messagebox.showerror("Error", "agian")

    cap.release()
    cv2.destroyAllWindows()
# Tạo GUI
root = Tk()


# label1 = Label(root,text="C='capture', E='end").grid(row=0,column=2)
btnStart = Button(root,text="Webcam",bg="green",fg="white",padx=10,command=openCamera).grid(row=1,column=1)
btn = Button(root, text="Picture", command=open_file_dialog).grid(row=2,column=2)
label = Label(root)
label.grid(row=2,column=0)

label2 = Label(root,text="Danh sách Biển số xe",font=20, bg="yellow").grid(row=3,column=0)

listBox = Listbox(root,width=50)
listBox.grid(row=4,column=0)

for item in array_list:
    listBox.insert(0,item)
root.title("Nhận diện biế số xe")
root.geometry("500x500+10+10")
root.mainloop()




# messagebox.showerror("Error", "Cannot open camera")