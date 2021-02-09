
#from GUI import Gui

from tkinter import filedialog
import cv2
#from PIL import Image
import numpy as np
import os
from tkinter import *
#from GUI.functionality_in_buttons import pause_flag,pause
from PIL import ImageTk,Image
#from Get_background_module.Get_backgraound_image import Get_bkgI
global filename,frame_num,iterations,B_pause,cap,canvas,fp
#bg = np.zeros((600, 800, 3), np.uint8)
Behavier = ['orienting', 'tapping' ,'singing' ,'attempting', 'copulation','nothing']
#attempting and copulation 不會有前三種情況
#新增有幾種動作的資料夾，frame有一種、二種、三種

es = cv2.getStructuringElement(cv2.MORPH_RECT,(2,2))
kernel = np.ones((9,9), np.uint8)
frame_diff = np.zeros((600,800),np.uint8)
frame_bin = np.zeros((600,800), np.bool)
frame_mor = np.zeros((600,800), np.bool)
#pause_flag = False


def frame_GATMD(frame):
    global bg,frame_diff,frame_bin,frame_mor,kernel,es
    frame_diff = bg.apply(frame)
    frame_bin = cv2.adaptiveThreshold(frame_diff,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,cv2.THRESH_BINARY_INV,13,10)
 #   ret,frame_bin = cv2.threshold(frame_diff,50,255,cv2.THRESH_BINARY)
 #   frame_mor = cv2.morphologyEx(frame_bin,cv2.MORPH_OPEN,es)
    frame_dilate = cv2.dilate(frame_bin, es, iterations=1)
 #   canv_imshow(frame_dilate)
    return frame_dilate
'''    gray = cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
    cv2.absdiff(bg,gray,frame_diff)
    ret,frame_bin = cv2.threshold(frame_diff,10,255,cv2.THRESH_BINARY)
    frame_mor = cv2.morphologyEx(frame_bin,cv2.MORPH_OPEN,kernel)
    frame_dilate = cv2.dilate(frame_mor, kernel, iterations=2)
    #canv_imshow(frame_diff)
    return frame_dilate'''



def classifier(frame,x,y,w,h,line,object_c):
    global filename,Behavier
    s=['0','0','0','0','0']
 #   newimage = frame[y:y+h,x:x+w]
    tmpn = ''
    gn = filename.strip(".avi")
    fn,s[0],s[1],s[2],s[3],s[4]=line.split('\t')

    for i in range(4,-1,-1):
        if i > 2 and s[i] == '1':
            tmpn = Behavier[i]
            break
        else:
            if s[i]=='1':
                tmpn = tmpn + Behavier[i]+'_'
    if tmpn != '':
        tmpn = './'+ tmpn +'/'
        print(tmpn,'\n')
        if not os.path.exists(tmpn):
            os.makedirs(tmpn)
        wn = tmpn + gn.split('/')[-1] + '_'+ (fn) +'_'+str(object_c)+'.jpg'
        cv2.imwrite(wn,frame[y:y+h,x:x+w])
    cv2.waitKey(5)

def bounding_box(frame_di,frame):
    global iterations,filename
    (cnts, _) = cv2.findContours(frame_di, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    line = fp.readline()
    object_c=0
    shf = frame.copy()
 #   print(len(cnts),'\n')
    for c in cnts:
    #    M = cv2.moments(c)
    #    cX = int(M["m10"] / M["m00"])
    #    cY = int(M["m01"] / M["m00"])
    #    cv2.circle(frame, (cX, cY), 10, (1, 227, 254), -1)
    #    box = cv2.minAreaRect(c)
    #    box = np.int0(cv2.boxPoints (box))
        if cv2.contourArea(c)>3000:
            x, y, w, h = cv2.boundingRect(c)
            classifier(frame,x,y,w,h,line,object_c)
            cv2.rectangle(shf, (x,y), (x+w,y+h), (255,0,0), 2)
            object_c = object_c+1
        #cv2.drawContours(frame, [box], -1, (0, 255, 0), 2)
 #   if len(cnts) ==1 :
    return shf

'''    for c in cnts:
        mask = np.zeros(gray.shape, dtype="uint8")
        cv2.drawContours(mask,[c],-1,255,-1)
        frame_tmp = cv2.bitwise_and(frame,frame,mask=mask)
        canv_imshow(frame_tmp)'''




'''    for i in range(0,len(cnts)):  
	    x, y, w, h = cv2.boundingRect(cnts[i])   
	    cv2.rectangle(frame, (x,y), (x+w,y+h), (153,153,0), 5)
    newimage=frame[y:y+h,x:x+w]
    return newimage'''





def canv_imshow(frame):
    global cap,canvas,pause_flag
    try:
        img = cv2.resize(frame,(800,600))
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGBA)
    except:
    #    canv_showtext("Load Video Error",canvas)
        return 0
    photo = ImageTk.PhotoImage(image = Image.fromarray(img))
    canvas.imgtk = photo
    canvas.create_image(0, 0, image=photo, anchor=NW)
 #   print(pause_flag,'\n')

def openfile():
    global filename,frame_num,iterations,cap,bg,fp
    bg = cv2.createBackgroundSubtractorKNN()
    filename = filedialog.askopenfilename(initialdir = "..",title = "Select file",filetypes = (("avi files","*.avi"),("all files","*.*")))
    if filename:
        cap = cv2.VideoCapture(filename)
        frame_num = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        iterations = 0
        print(filename.split('/')[-1] ,"  ",frame_num)
        fp = open(filename.split('/')[-1]+'.txt',"r")
        #print(pause_flag,'\n')
        video_loop()


def video_loop():
    global iterations,cap,frame_num,canvas
    if iterations < frame_num :
        ret,frame = cap.read()
    #    outframe = frame.copy()
        frame_di = frame_GATMD(frame)
        frame_box = bounding_box(frame_di,frame)
        canv_imshow(frame_box)
        iterations=iterations+1
        canvas.after(10,video_loop)
    else:
        print('The video is finished\n')
     
#------------------------------------Tkinter介面------------------------------------------

root = Tk()


root.geometry("1280x800")
root.title("Fly Detection")

canvas = Canvas(root, width=800, height=600)
canvas.pack(side=LEFT, padx=5)

# MenuBar
menubar = Menu(root)
filemenu = Menu(menubar, tearoff=False)
menubar.add_cascade(label="檔案", menu=filemenu)
filemenu.add_command(label="開啟影片", command=openfile) 
filemenu.add_command(label="離開", command=root.destroy)


optionmenu = Menu(menubar, tearoff=False)
menubar.add_cascade(label="選項", menu=optionmenu)


# filemenu.add_command(label="匯出")

SPEEDUP=BooleanVar(root, True)
optionmenu.add_checkbutton(label="加速", variable=SPEEDUP)
optionmenu.add_command(label="設定")
root.config(menu=menubar) #刷新顯示選單

#Labels
F_coord = LabelFrame(root, text="座標")
F_coord.pack(fill=X, padx=10)
strv_coord = StringVar()
L_coord = Label(F_coord, textvariable=strv_coord, anchor=NW)
L_coord.pack(fill=BOTH)


F_dist = LabelFrame(root, text="距離")
F_dist.pack(fill=BOTH, padx=10)
strv_dist = StringVar()
L_dist = Label(F_dist, textvariable=strv_dist, anchor=NW)
L_dist.pack(fill=BOTH)


F_chasing = LabelFrame(root, text="Chasing")
F_chasing.pack(fill=BOTH, padx=10)
F_chasing1 = Frame(F_chasing)
F_chasing1.pack(fill=X)

Label(F_chasing1,text="時間: ").pack(side=LEFT)
strv_chasing_time = StringVar()
L_chasing_time = Label(F_chasing1, textvariable=strv_chasing_time, anchor=W)
L_chasing_time.pack(fill=X, side=LEFT)
F_chasing2 = Frame(F_chasing)
F_chasing2.pack(fill=X)

Label(F_chasing2,text="距離: ").pack(side=LEFT)
strv_chasing_dist = StringVar()
L_chasing_dist = Label(F_chasing2, textvariable=strv_chasing_dist, anchor=W)
L_chasing_dist.pack(fill=X, side=LEFT)

F_chasing4 = Frame(F_chasing)
F_chasing4.pack(fill=X)
Label(F_chasing4,text="平均速度: ").pack(side=LEFT)
strv_chasing_speed = StringVar()
L_chasing_speed = Label(F_chasing4, textvariable=strv_chasing_speed, anchor=W)
L_chasing_speed.pack(fill=X, side=LEFT)


F_attach = LabelFrame(root, text="接觸")
F_attach.pack(fill=BOTH, padx=10)
F_attach1 = Frame(F_attach)
F_attach1.pack(fill=X)
Label(F_attach1,text="時間: ").pack(side=LEFT)
strv_attach_time = StringVar()
L_attach = Label(F_attach1, textvariable=strv_attach_time, anchor=NW)
L_attach.pack(fill=X, side=LEFT)
F_attach2 = Frame(F_attach)
F_attach2.pack(fill=X)
Label(F_attach2,text="次數: ").pack(side=LEFT)
strv_attach_round = StringVar()
L_attach = Label(F_attach2, textvariable=strv_attach_round, anchor=NW)
L_attach.pack(fill=X, side=LEFT)


#B_pause = Button(root, text="pause", command=pause) 
#B_pause.pack() 

L_fps = Label(root, text="fps")
L_fps.pack(anchor = SW,padx = 10)
L_time = Label(root, text = "time")
L_time.pack(anchor = SW,padx = 10)
#-----------------------------------------------------------------------------------------
#canv_showtext("No Video Input",canvas)
root.mainloop()