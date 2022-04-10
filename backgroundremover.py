import cv2
import numpy as np

link = input('Podaj sciezke do zdjęcia: ').replace('\"', '')
print(link)
img = cv2.imread(link)
img_copy = np.copy(img)
scaleFactor = 1
maxScaleUp = 100
windowName = 'ResizeImage'
trackBarValue = 'Scale'

marker_img = np.zeros(img.shape[:2], dtype=np.int32)
segments = np.zeros(img.shape, dtype=np.uint8)

colors = [(0,0,0), (255,0,0), (0,0,255)]

current_marker = 1
marks_updates = False
show_img = cv2.addWeighted(img_copy, 0.6, segments, 0.4, 0)

def display():
    global show_img
    show_img = resize(show_img)
    cv2.imshow(windowName, show_img)

def mause_callback(event, x, y, flags, param):
    global marks_updates, scaleFactor
    if event == cv2.EVENT_LBUTTONDOWN:
        x = int(round(x/scaleFactor))
        y = int(round(y/scaleFactor))
        cv2.circle(marker_img, (x, y), 3, current_marker, -1)
        cv2.circle(img_copy, (x, y), 3, colors[current_marker], -1)
        marks_updates = True

def resize(img):
    global scaleFactor
    return cv2.resize(img, None, fx=scaleFactor, fy=scaleFactor, interpolation=cv2.INTER_LINEAR)

def scaleImage(*args):
    global scaleFactor
    scaleFactor = args[0]/100

def edit():
    cv2.setMouseCallback(windowName, mause_callback)
    global current_marker, marks_updates, img_copy, segments, marker_img, img, colors, write_img, show_img
    while True:
        show_img = cv2.addWeighted(img_copy, 0.6, segments, 0.4, 0)
        display()
        cv2.imshow(windowName, show_img)
        k = cv2.waitKey(1)
        if k == 27:
            break
        elif k == ord('r'):
            img_copy = np.copy(img)
            marker_img = np.zeros(img.shape[:2], dtype=np.int32)
            segments = np.zeros(img.shape, dtype=np.uint8)
            marks_updates = False
            show_img = cv2.addWeighted(img_copy, 0.6, segments, 0.4, 0)

        elif k > 0 and chr(k).isdigit():
            current_marker = int(chr(k))
        
        elif k == ord('s'):
            write_img = np.copy(img)
            write_img[np.where((segments == [0,0,255]).all(axis=2))] = [255,255,255]

            file_name = '\\'.join(link.split('\\')[:-1]+['new_'+link.split('\\')[-1]])
            cv2.imwrite(file_name, write_img)
            effect()
            break

        if marks_updates:
            marker_image_copy = marker_img.copy()
            cv2.watershed(img, marker_image_copy)

            segments = np.zeros(img.shape, dtype=np.uint8)
            for color_ind in range(3):
                segments[marker_image_copy == (color_ind)] = colors[color_ind]
            marks_updates = False
            show_img = cv2.addWeighted(img_copy, 0.6, segments, 0.4, 0)

def effect():
    cv2.setMouseCallback(windowName, lambda *args: None)
    global show_img
    while True:
        show_img = write_img.copy()
        display()
        k = cv2.waitKey(1)
        if k == 27:
            break
        elif k == ord('e'):
            edit()
            break
            

cv2.namedWindow(windowName, cv2.WINDOW_AUTOSIZE)
cv2.createTrackbar(trackBarValue, windowName, 100, 200, scaleImage)

display()
edit()
cv2.destroyAllWindows()