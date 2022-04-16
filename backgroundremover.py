import cv2
import numpy as np
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QFileDialog, QApplication, QPushButton, QMainWindow
import sys

def mause_callback(event, x_val, y_val, flags, param):
    global marks_updates, x, y
    if event == cv2.EVENT_LBUTTONDOWN:
        x = int(round(x_val/scaleFactor))
        y = int(round(y_val/scaleFactor))
        marks_updates = True

def resize(img):
    global scaleFactor
    return cv2.resize(img, None, fx=scaleFactor, fy=scaleFactor, interpolation=cv2.INTER_LINEAR)

def scaleImage(*args):
    global scaleFactor
    scaleFactor = args[0]/100

def alphaImage(*args):
    global alpha
    alpha = args[0]/100

def betaImage(*args):
    global beta
    beta = -1*args[0]

class Photo:
    def __init__(self):
        self.app = QApplication(sys.argv)

        self.maxScaleUp = 100
        self.windowName = 'Backgroud remover'
        self.windowName2 = 'Gamma editor'
        self.trackBarsValue = ['Scale','alpha','beta']
        self.colors = [(0,0,0), (255,0,0), (0,0,255)]
        self.current_marker = 1
        self.marks_updates = False
        self.edition_mode = True
        self.stop_process = False


    def dialog(self):
        file, check = QFileDialog.getOpenFileName(None, 'Open file', '', 'Images (*.png *.jpg *.jpeg *.bmp)')
        if check:
            self.img = cv2.imread(file)
            self.img_copy = np.copy(self.img)
            self.img_gamma = np.copy(self.img)
            self.marker_img = np.zeros(self.img.shape[:2], dtype=np.int32)
            self.segments = np.zeros(self.img.shape, dtype=np.uint8)
            global scaleFactor
            scaleFactor = 800/self.img.shape[1]
        else:
            self.dialog()
    
    def set_window(self):
        cv2.namedWindow(self.windowName, cv2.WINDOW_AUTOSIZE)
        cv2.namedWindow(self.windowName2, cv2.WINDOW_AUTOSIZE)
        cv2.createTrackbar(self.trackBarsValue[0], self.windowName, round(scaleFactor*100), 200, scaleImage)
        cv2.createTrackbar(self.trackBarsValue[1], self.windowName2, 125, 200, alphaImage)
        cv2.createTrackbar(self.trackBarsValue[2], self.windowName2, 100, 200, betaImage)

    def edit(self):
        global marks_updates
        self.show_img = cv2.addWeighted(self.img_copy, 0.6, self.segments, 0.4, 0)
        self.img_gamma_copy = np.copy(self.img_gamma)

        cv2.add(self.img_gamma_copy, np.array([float(beta)]), self.img_gamma_copy)
        cv2.multiply(self.img_gamma_copy, np.array([alpha]), self.img_gamma_copy)

        cv2.imshow(self.windowName, resize(self.show_img))
        cv2.imshow(self.windowName2, resize(self.img_gamma_copy))

        keyname = cv2.waitKey(1)
        if keyname == 27:
            self.close()
        elif keyname == ord('r'):
            self.img_copy = np.copy(self.img)
            self.marker_img = np.zeros(self.img.shape[:2], dtype=np.int32)
            self.segments = np.zeros(self.img.shape, dtype=np.uint8)
        elif keyname > 0 and chr(keyname).isdigit():
            self.current_marker = int(chr(keyname))
        elif keyname == ord('s'):
            self.img_to_write = np.copy(self.img)
            self.img_to_write[np.where((self.segments == [0,0,255]).all(axis=2))] = [255,255,255]
            self.edition_mode = False
            
        if marks_updates:
            cv2.circle(self.marker_img, (x, y), 3, self.current_marker, -1)
            cv2.circle(self.img_copy, (x, y), 3, self.colors[self.current_marker], -1)
            marker_image_copy = np.copy(self.marker_img)
            cv2.watershed(self.img_gamma, marker_image_copy)

            for color_ind in range(3):
                self.segments[np.where((marker_image_copy == color_ind))] = self.colors[color_ind]
            marks_updates = False
    
    def effect(self):
        cv2.imshow(self.windowName, resize(self.img_to_write))
        keyname = cv2.waitKey(1)
        if keyname == 27:
            self.close()
        elif keyname == ord('e'):
            self.edition_mode = True
        elif keyname == ord('s'):
            file, check = QFileDialog.getSaveFileName(None, 'Save file', '', 'Images (*.png *.jpg *.jpeg *.bmp)')
            if check:
                cv2.imwrite(file, self.img_to_write)

    def close(self):
        cv2.destroyAllWindows()
        self.app.closeAllWindows()
        self.app.quit()
        self.stop_process = True

marks_updates = False
scaleFactor = 1
alpha = 1.25
beta = -100.0

photo = Photo()
photo.dialog()
photo.set_window()
while True:
    if photo.edition_mode:
        try:
            cv2.setMouseCallback(photo.windowName, mause_callback)
        except:
            pass
        photo.edit()
    else:
        try:
            cv2.setMouseCallback(photo.windowName, lambda *args: None)
        except:
            pass
        photo.effect()
    if photo.stop_process:
        break
