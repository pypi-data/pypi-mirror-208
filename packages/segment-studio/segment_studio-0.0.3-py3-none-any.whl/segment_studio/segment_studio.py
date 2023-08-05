#!/usr/bin/env python
# coding: utf-8

# In[1]:

import subprocess
import pickle
import platform
import os
import requests

def runcmd(cmd, verbose = False, *args, **kwargs):

    process = subprocess.Popen(
        cmd,
        stdout = subprocess.PIPE,
        stderr = subprocess.PIPE,
        text = True,
        shell = True
    )
    std_out, std_err = process.communicate()
    if verbose:
        print(std_out.strip(), std_err)
    pass

###############SAM MODEL###################################################

# import sys
# # !pip3 install torch torchvision torchaudio
runcmd('pip3 install torch torchvision torchaudio', verbose = True)

# !pip install tk
# subprocess.check_call([sys.executable, "-m", "pip", "install", "tk"])
# if platform.system() == 'Darwin':
runcmd('python -m pip install tk-tools', verbose = True)
# !pip install Pillow
# subprocess.check_call([sys.executable, "-m", "pip", "install", "Pillow"])
runcmd('pip install Pillow', verbose = True)
# get_ipython().system('pip list')

runcmd('pip install opencv-python', verbose = True)

runcmd('pip install supervision', verbose = True)

runcmd('pip install sv-ttk', verbose = True)

# In[2]:


import os
HOME = os.getcwd()
# print("HOME:", HOME)


# In[3]:


# get_ipython().run_line_magic('cd', '{HOME}')
# os.chdir(HOME)
runcmd('cd ' + HOME)

# get_ipython().system("{sys.executable} -m pip install 'git+https://github.com/facebookresearch/segment-anything.git'")
# subprocess.check_call([sys.executable, "-m", "pip", "install", "'git+https://github.com/facebookresearch/segment-anything.git'"])
runcmd("pip install 'git+https://github.com/facebookresearch/segment-anything.git'", verbose = True)

if os.path.isfile(os.path.join(HOME, "weights", "add-folder-modified.png")) == False:
    
    icons = ["https://cdn-icons-png.flaticon.com/128/2312/2312340.png", "https://cdn-icons-png.flaticon.com/128/7955/7955492.png", "https://cdn-icons-png.flaticon.com/128/4208/4208397.png", "https://cdn-icons-png.flaticon.com/128/10732/10732417.png", "https://cdn-icons-png.flaticon.com/128/603/603570.png"]

    icon_names = ["add-folder-modified.png", "color-wheel-modified.png", "download-modified.png", "move-modified.png", "pencil-modified.png"]

    for i in range(len(icons)):
        img_data = requests.get(icons[i]).content
        with open(icon_names[i], 'wb') as handler:
            handler.write(img_data)

# In[4]:


# !pip install -q jupyter_bbox_widget roboflow dataclasses-json supervision


# In[5]:


# !brew install wget


# In[6]:

if os.path.isfile(os.path.join(HOME, "weights", "sam_vit_h_4b8939.pth")) == False:
    # get_ipython().run_line_magic('cd', '{HOME}')
    os.chdir(HOME)
    # runcmd('cd ' + HOME)

    # get_ipython().system('mkdir {HOME}/weights')
    os.mkdir(HOME + '/weights')
    # runcmd('mkdir ' + HOME + '/weights')

    # get_ipython().run_line_magic('cd', '{HOME}/weights')
    os.chdir(HOME + '/weights')
    # runcmd('cd ' + HOME + '/weights')

    # get_ipython().system('wget -q https://dl.fbaipublicfiles.com/segment_anything/sam_vit_h_4b8939.pth')
    runcmd('wget -q https://dl.fbaipublicfiles.com/segment_anything/sam_vit_h_4b8939.pth', verbose = True)


# # In[7]:

CHECKPOINT_PATH = os.path.join(HOME, "weights", "sam_vit_h_4b8939.pth")
print(CHECKPOINT_PATH, "; exist:", os.path.isfile(CHECKPOINT_PATH))


# # In[8]:


# # %cd {HOME}
# # !mkdir {HOME}/data
# # %cd {HOME}/data

# # !wget -q https://media.roboflow.com/notebooks/examples/dog.jpeg
# # !wget -q https://media.roboflow.com/notebooks/examples/dog-2.jpeg
# # !wget -q https://media.roboflow.com/notebooks/examples/dog-3.jpeg
# # !wget -q https://media.roboflow.com/notebooks/examples/dog-4.jpeg


# # In[9]:





# In[10]:

import torch

DEVICE = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')
MODEL_TYPE = "vit_h"


# In[11]:


from segment_anything import sam_model_registry, SamAutomaticMaskGenerator, SamPredictor

sam = sam_model_registry[MODEL_TYPE](checkpoint=CHECKPOINT_PATH).to(device=DEVICE)

os.chdir(HOME)

# In[12]:

# pickle.dump(sam, open("sam_model", 'wb'))

# sam_model = pickle.load(open('sam_model', 'rb'))

# mask_generator = SamAutomaticMaskGenerator(sam_model)

# pickle.dump(mask_generator, open("mask_generator_model", 'wb'))

# mask_generator = pickle.load(open('mask_generator_model', 'rb'))

mask_generator = SamAutomaticMaskGenerator(sam)


# In[13]:

runcmd("pip install tk", verbose = True)

import tkinter as tk            # ウィンドウ作成用
from tkinter import filedialog  # ファイルを開くダイアログ用
from PIL import Image, ImageTk  # 画像データ用
import math                     # 回転の計算用
import numpy as np              # アフィン変換行列演算用
import os                       # ディレクトリ操作用

class Application(tk.Frame):
    
    pen_color = "black"
    pen_size = 5
    file_path = ""
    layers = []
    
    def __init__(self, master=None):
        super().__init__(master)

        self.master.geometry("600x400") 
 
        self.pil_image = None   # 表示する画像データ
        self.my_title = "Python Image Viewer"

        # ウィンドウの設定
        self.master.title(self.my_title)
 
        # 実行内容
        self.create_menu()   # メニューの作成
        self.create_widget() # ウィジェットの作成

        # 初期アフィン変換行列
        self.reset_transform()

    def menu_open_clicked(self, event=None):
        # ファイル→開く
        filename = tk.filedialog.askopenfilename(
            filetypes = [("Image file", ".bmp .png .jpg .tif"), ("Bitmap", ".bmp"), ("PNG", ".png"), ("JPEG", ".jpg"), ("Tiff", ".tif") ], # ファイルフィルタ
            initialdir = os.getcwd() # カレントディレクトリ
            )

        # 画像ファイルを設定する
        # self.set_image(filename)

    def menu_quit_clicked(self):
        # ウィンドウを閉じる
        self.master.destroy() 

    # create_menuメソッドを定義
    def create_menu(self):
        self.menu_bar = tk.Menu(self) # Menuクラスからmenu_barインスタンスを生成
 
        self.file_menu = tk.Menu(self.menu_bar, tearoff = tk.OFF)
        self.menu_bar.add_cascade(label="File", menu=self.file_menu)

        self.file_menu.add_command(label="Open", command = self.menu_open_clicked, accelerator="Ctrl+O")
        self.file_menu.add_separator() # セパレーターを追加
        self.file_menu.add_command(label="Exit", command = self.menu_quit_clicked)

        self.menu_bar.bind_all("<Control-o>", self.menu_open_clicked) # ファイルを開くのショートカット(Ctrol-Oボタン)
        
        self.master.bind("<Button-1>", self.mouse_down_left)                   # MouseDown
        self.master.bind("<B1-Motion>", self.mouse_move_left)                  # MouseDrag（ボタンを押しながら移動）
        self.master.bind("<Motion>", self.mouse_move)                          # MouseMove
        self.master.bind("<Double-Button-1>", self.mouse_double_click_left)    # MouseDoubleClick
        self.master.bind("<MouseWheel>", self.mouse_wheel)                     # MouseWheel
        
        self.master.config(menu=self.menu_bar) # メニューバーの配置
 
    # create_widgetメソッドを定義
    def create_widget(self):

        # ステータスバー相当(親に追加)
        frame_statusbar = tk.Frame(self.master, bd=1, relief = tk.SUNKEN)
        self.label_image_info = tk.Label(frame_statusbar, text="image info", anchor=tk.E, padx = 5)
        self.label_image_pixel = tk.Label(frame_statusbar, text="(x, y)", anchor=tk.W, padx = 5)
        self.label_loading_img = tk.Label(frame_statusbar, text="", padx = 5)
        self.label_image_info.pack(side=tk.RIGHT)
        self.label_image_pixel.pack(side=tk.LEFT)
        self.label_loading_img.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        frame_statusbar.pack(side=tk.BOTTOM, fill=tk.X)

        # Canvas
        self.canvas = tk.Canvas(self.master, background="grey")
        self.canvas.pack(expand=True, fill=tk.BOTH)  # この両方でDock.Fillと同じ
    
    def set_loading_widget(self, loading_val, loading):
        if loading:
            load, tot_load = loading_val
            self.label_loading_img["text"] = f"Loading {load} of {tot_load}"
        else:
            self.label_loading_img["text"] = f""

    def set_pen_size(self, size):
        global pen_size
        
        pen_size = size

    def set_draw(self, tool):
        if tool == "move":
             # マウスイベント
            self.canvas.unbind("<B1-Motion>")
            self.canvas.bind("<Button-1>", self.mouse_down_left)                   # MouseDown
            self.canvas.bind("<B1-Motion>", self.mouse_move_left)                  # MouseDrag（ボタンを押しながら移動）
            self.canvas.bind("<Motion>", self.mouse_move)                          # MouseMove
            self.canvas.bind("<Double-Button-1>", self.mouse_double_click_left)    # MouseDoubleClick
            self.canvas.bind("<MouseWheel>", self.mouse_wheel)                     # MouseWheel
        elif tool == "draw":
             # マウスイベント
            self.master.unbind("<Button-1>")                   # MouseDown
            self.master.unbind("<B1-Motion>")                  # MouseDrag（ボタンを押しながら移動）
            self.master.unbind("<Motion>")                          # MouseMove
            self.master.unbind("<Double-Button-1>")    # MouseDoubleClick
            self.master.unbind("<MouseWheel>")                     # MouseWheel
            self.canvas.bind("<B1-Motion>", self.draw)
        
    def set_image(self, file):
        ''' 画像ファイルを開く '''
        if not file:
            return
        # PIL.Imageで開く
        self.pil_image = file
        # 画像全体に表示するようにアフィン変換行列を設定
        self.zoom_fit(self.pil_image.width, self.pil_image.height)
        # 画像の表示
        self.draw_image(self.pil_image)

        # ウィンドウタイトルのファイル名を設定
        # self.master.title(self.my_title + " - " + os.path.basename(filename))
        # ステータスバーに画像情報を表示する
        self.label_image_info["text"] = f"{self.pil_image.format} : {self.pil_image.width} x {self.pil_image.height} {self.pil_image.mode}"
        # カレントディレクトリの設定
        # os.chdir(os.path.dirname(filename))

    # -------------------------------------------------------------------------------
    # マウスイベント
    # -------------------------------------------------------------------------------
    def draw(self, event):
        if showing_mask:
            drawing = ImageDraw.Draw(layers[curr_layer_idx].masks[curr_mask_idx].data)
        else:
            drawing = ImageDraw.Draw(layers[curr_layer_idx].data)

        x1, y1 = (event.x - pen_size), (event.y - pen_size)
        x2, y2 = (event.x + pen_size), (event.y + pen_size)
        image_point = self.to_image_point(event.x, event.y)
        x1_draw, y1_draw = (image_point[0]- pen_size), (image_point[1] - pen_size)
        x2_draw, y2_draw = (image_point[0]+ pen_size), (image_point[1] + pen_size)
        # self.canvas.create_oval(x1, y1, x2, y2, fill=pen_color, outline='')
        drawing.ellipse([(x1_draw, y1_draw), (x2_draw, y2_draw)], fill=pen_color)
        self.redraw_image()

#     def draw(event):
#         global drawing

#         if showing_mask:
#             drawing = ImageDraw.Draw(layers[curr_layer_idx].masks[curr_mask_idx].data)
#         else:
#             drawing = ImageDraw.Draw(layers[curr_layer_idx].data)

#         x1, y1 = (event.x - pen_size), (event.y - pen_size)
#         x2, y2 = (event.x + pen_size), (event.y + pen_size)
#         # canvas.create_oval(x1, y1, x2, y2, fill=pen_color, outline='')
#         drawing.ellipse([(x1, y1), (x2, y2)], fill=pen_color)
    
    def mouse_down_left(self, event):
        ''' マウスの左ボタンを押した '''
        self.__old_event = event

    def mouse_move_left(self, event):
        ''' マウスの左ボタンをドラッグ '''
        if (self.pil_image == None):
            return
        self.translate(event.x - self.__old_event.x, event.y - self.__old_event.y)
        self.redraw_image() # 再描画
        self.__old_event = event

    def mouse_move(self, event):
        ''' マウスの左ボタンをドラッグ '''
        if (self.pil_image == None):
            return
        
        image_point = self.to_image_point(event.x, event.y)
        if image_point != []:
            self.label_image_pixel["text"] = (f"({image_point[0]:.2f}, {image_point[1]:.2f})")
        else:
            self.label_image_pixel["text"] = ("(--, --)")


    def mouse_double_click_left(self, event):
        ''' マウスの左ボタンをダブルクリック '''
        if self.pil_image == None:
            return
        self.zoom_fit(self.pil_image.width, self.pil_image.height)
        self.redraw_image() # 再描画

    def mouse_wheel(self, event):
        ''' マウスホイールを回した '''
        if self.pil_image == None:
            return

        if event.state != 9: # 9はShiftキー(Windowsの場合だけかも？)
            if (event.delta < 0):
                # 下に回転の場合、拡大
                self.scale_at(1.25, event.x, event.y)
            else:
                # 上に回転の場合、縮小
                self.scale_at(0.8, event.x, event.y)
        else:
            if (event.delta < 0):
                # 下に回転の場合、反時計回り
                self.rotate_at(-5, event.x, event.y)
            else:
                # 上に回転の場合、時計回り
                self.rotate_at(5, event.x, event.y)     
        self.redraw_image() # 再描画
        
    # -------------------------------------------------------------------------------
    # 画像表示用アフィン変換
    # -------------------------------------------------------------------------------

    def reset_transform(self):
        '''アフィン変換を初期化（スケール１、移動なし）に戻す'''
        self.mat_affine = np.eye(3) # 3x3の単位行列

    def translate(self, offset_x, offset_y):
        ''' 平行移動 '''
        mat = np.eye(3) # 3x3の単位行列
        mat[0, 2] = float(offset_x)
        mat[1, 2] = float(offset_y)

        self.mat_affine = np.dot(mat, self.mat_affine)

    def scale(self, scale:float):
        ''' 拡大縮小 '''
        mat = np.eye(3) # 単位行列
        mat[0, 0] = scale
        mat[1, 1] = scale

        self.mat_affine = np.dot(mat, self.mat_affine)

    def scale_at(self, scale:float, cx:float, cy:float):
        ''' 座標(cx, cy)を中心に拡大縮小 '''

        # 原点へ移動
        self.translate(-cx, -cy)
        # 拡大縮小
        self.scale(scale)
        # 元に戻す
        self.translate(cx, cy)

    def rotate(self, deg:float):
        ''' 回転 '''
        mat = np.eye(3) # 単位行列
        mat[0, 0] = math.cos(math.pi * deg / 180)
        mat[1, 0] = math.sin(math.pi * deg / 180)
        mat[0, 1] = -mat[1, 0]
        mat[1, 1] = mat[0, 0]

        self.mat_affine = np.dot(mat, self.mat_affine)

    def rotate_at(self, deg:float, cx:float, cy:float):
        ''' 座標(cx, cy)を中心に回転 '''

        # 原点へ移動
        self.translate(-cx, -cy)
        # 回転
        self.rotate(deg)
        # 元に戻す
        self.translate(cx, cy)

    def zoom_fit(self, image_width, image_height):
        '''画像をウィジェット全体に表示させる'''

        # キャンバスのサイズ
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()

        if (image_width * image_height <= 0) or (canvas_width * canvas_height <= 0):
            return

        # アフィン変換の初期化
        self.reset_transform()

        scale = 1.0
        offsetx = 0.0
        offsety = 0.0

        if (canvas_width * image_height) > (image_width * canvas_height):
            # ウィジェットが横長（画像を縦に合わせる）
            scale = canvas_height / image_height
            # あまり部分の半分を中央に寄せる
            offsetx = (canvas_width - image_width * scale) / 2
        else:
            # ウィジェットが縦長（画像を横に合わせる）
            scale = canvas_width / image_width
            # あまり部分の半分を中央に寄せる
            offsety = (canvas_height - image_height * scale) / 2

        # 拡大縮小
        self.scale(scale)
        # あまり部分を中央に寄せる
        self.translate(offsetx, offsety)

    def to_image_point(self, x, y):
        '''　キャンバスの座標から画像の座標へ変更 '''
        if self.pil_image == None:
            return []
        # 画像→キャンバスの変換からキャンバス→画像にする（逆行列にする）
        mat_inv = np.linalg.inv(self.mat_affine)
        image_point = np.dot(mat_inv, (x, y, 1.))
        if  image_point[0] < 0 or image_point[1] < 0 or image_point[0] > self.pil_image.width or image_point[1] > self.pil_image.height:
            return []

        return image_point

    # -------------------------------------------------------------------------------
    # 描画
    # -------------------------------------------------------------------------------

    def draw_image(self, pil_image):
        
        if pil_image == None:
            return

        self.pil_image = pil_image

        # キャンバスのサイズ
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()

        # キャンバスから画像データへのアフィン変換行列を求める
        #（表示用アフィン変換行列の逆行列を求める）
        mat_inv = np.linalg.inv(self.mat_affine)

        # numpy arrayをアフィン変換用のタプルに変換
        affine_inv = (
            mat_inv[0, 0], mat_inv[0, 1], mat_inv[0, 2],
            mat_inv[1, 0], mat_inv[1, 1], mat_inv[1, 2]
            )

        # PILの画像データをアフィン変換する
        dst = self.pil_image.transform(
                    (canvas_width, canvas_height),# 出力サイズ
                    Image.AFFINE,   # アフィン変換
                    affine_inv,     # アフィン変換行列（出力→入力への変換行列）
                    Image.NEAREST   # 補間方法、ニアレストネイバー     
                    )

        im = ImageTk.PhotoImage(image=dst)

        # 画像の描画
        item = self.canvas.create_image(
                0, 0,           # 画像表示位置(左上の座標)
                anchor='nw',    # アンカー、左上が原点
                image=im        # 表示画像データ
                )

        self.image = im

    def redraw_image(self):
        ''' 画像の再描画 '''
        if self.pil_image == None:
            return
        self.draw_image(self.pil_image)


# if __name__ == "__main__":
#     root = tk.Tk()
#     app = Application(master=root)
#     app.mainloop()


# In[14]:


# !pip install multiprocess


# In[ ]:


import tkinter
from tkinter import *
from tkinter import filedialog
from tkinter import colorchooser
from PIL import Image, ImageOps, ImageTk, ImageFilter, ImageDraw
from tkinter import ttk
# from concurrent.futures import ThreadPoolExecutor, as_completed
import cv2
import supervision as sv
import time
import math
import sv_ttk
# from multiprocessing.pool import ThreadPool
import uuid
import os
# import torch
import threading
# import multiprocessing
# import multiprocess
# from concurrent.futures.thread import ThreadPoolExecutor
# import concurrent.futures

# multiprocessing.set_start_method('spawn')

root = tkinter.Tk()
root.geometry("1920x1080")
root.title("Image Drawing Tool")
root.config(bg="black")

pen_color = "black"
pen_size = 5
file_path = ""
layers = []
curr_masks = []
drawing = None
seg_loading = False

showing_mask = False
curr_layer_idx = 0
curr_mask_idx = 0
current_image = None
draw_canvas = None
image_bgr = None

load_total_img = None

class Mask:
    def __init__(self, name, data):
        self.name = name
        self.data = data

class Layer:
    def __init__(self, name, data, masks):
        self.name = name
        self.data = data
        self.masks = masks

class EditableListbox(Listbox):
    """A listbox where you can directly edit an item via double-click"""
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        
        self.edit_item = None
        
        self.mask = False
        
        self.popup_menu = Menu(self, tearoff=0)
        self.popup_menu.add_command(label="Delete",
                                    command=self.delete_selected)
        self.popup_menu.add_command(label="Select All",
                                    command=self.select_all)
        
        button = ""
        
        if platform.system() == 'Darwin':
            button = "<Button-2>"
        else:
            button = "<Button-3>"

        self.bind(button, self.popup) # Button-2 on Aqua
    
    def isMask(self, mask):
        
        self.mask = mask
        
        # print("mask", self.mask)
        
        if mask:
            self.bind("<Double-1>", self.show_masks)
            self.popup_menu.add_command(label="Rename", command=self.start_edit)
        else:
            self.bind("<Double-1>", self.show_layer)
    
    def popup(self, event):
        try:
            self.popup_menu.tk_popup(event.x_root, event.y_root, 0)
        finally:
            self.popup_menu.grab_release()

    def delete_selected(self):
        if self.mask:
            for i in listbox_masks.curselection():
                # print(listbox_masks.get(i))
                listbox_masks.delete(i )
                curr_masks.pop(i)
        else:
            for i in listbox_layer.curselection():
                # print(listbox_layer.get(i))
                listbox_layer.delete(i)
                layers.pop(i)

    def select_all(self):
        self.selection_set(0, 'end')

    def _start_edit(self, event):
        index = self.index(f"@{event.x},{event.y}")
        self.start_edit(index)
        return "break"

    def start_edit(self):
        index = None
        for i in self.curselection()[::-1]:
            index = i
        self.edit_item = index
        text = self.get(index)
        y0 = self.bbox(index)[1]
        entry = Entry(self, borderwidth=0, highlightthickness=1)
        entry.bind("<Return>", self.accept_edit)
        entry.bind("<Escape>", self.cancel_edit)

        entry.insert(0, text)
        entry.selection_from(0)
        entry.selection_to("end")
        entry.place(relx=0, y=y0, relwidth=1, width=-1)
        entry.focus_set()
        entry.grab_set()

    def cancel_edit(self, event):
        event.widget.destroy()

    def accept_edit(self, event):
        new_data = event.widget.get()
        # self.delete(self.edit_item)
        listbox_masks.delete(self.edit_item)
        self.insert(self.edit_item, new_data)
        # listbox_masks.insert(self.edit_item, new_data)
        layers[curr_layer_idx].masks[self.edit_item].name = new_data
        event.widget.destroy()
        
    def show_layer(self, event):
        global curr_masks
        global curr_layer_idx
        global showing_mask
        global draw_canvas
        
        showing_mask = False
        
        for i in listbox_layer.curselection():
            pilimage = layers[i].data
            draw_canvas.set_image(pilimage)
            # canvas.config(width=pilimage.width, height=pilimage.height)
            pilimage = ImageTk.PhotoImage(pilimage)
            # canvas.image = pilimage
            # canvas.create_image(0, 0, image=pilimage, anchor="nw")
            curr_masks = []
            curr_masks = layers[i].masks
            listbox_masks.delete(0, END)
            for masks in layers[i].masks:
                listbox_masks.insert(END, masks.name)
            curr_layer_idx = i

    def show_masks(self, event):
        global curr_mask_idx
        global showing_mask
        global draw_canvas
        
        showing_mask = True
        
        for i in listbox_masks.curselection():          
            pilimage = layers[curr_layer_idx].masks[i].data
            draw_canvas.set_image(pilimage)
            # canvas.config(width=pilimage.width, height=pilimage.height)
            pilimage = ImageTk.PhotoImage(pilimage)
            # canvas.image = pilimage
            # canvas.create_image(0, 0, image=pilimage, anchor="nw")
            curr_mask_idx = i
            image = layers[curr_layer_idx].masks[curr_mask_idx].data

def add_image():
    global file_path
    global layers
    global seg_loading
    global image_bgr
    global draw_canvas

    file_path = filedialog.askopenfilenames(
        initialdir="D:/codefirst.io/Tkinter Image Editor/Pictures")

    seg_loading = True
    threads = []
    # print("starting threads")

    # manager = multiprocessing.Manager()

    results = []
    # executor = concurrent.futures.ProcessPoolExecutor(10)
    # futures = [executor.submit(seg_func.seg_image, file, results) for file in file_path]
    # concurrent.futures.wait(futures)

    # with ThreadPoolExecutor(max_workers=2) as executor:
    #     for file in file_path:
    #         executor.submit(seg_image, file)
#         results = []

#         pool = multiprocessing.Pool()
#         for file in file_path:
#             pool.apply_async(seg_func.seg_image, args = (file, ), callback = log_result)
#         pool.close()
#         # pool.join()
#         print(result_list)

    # p = multiprocess.Pool(4)
    # results = p(target=seg_func.seg_image, args=file_path)

    # for file in file_path:
    #     results.append(multiprocess.Process(target=seg_func.seg_image, args=(file, )).start())
#         with multiprocessing.get_context("spawn").Pool(8) as p:
#             results = p.map(seg_func.seg_image, file_path)

    # time.sleep(240)

    # print(results[-1].name)
    # print(len(results))
    
    threading.Thread(target=seg_image, args=(file_path, )).start()

#     for result in range(len(results)):
#         layers.append(results[result])
#         listbox_layer.insert(END, results[result].name)

#         pilimage = results[result].data
#         width, height = int(pilimage.width / 2), int(pilimage.height / 2)
#         pilimagePhotoImage = pilimage.resize((width, height), Image.ANTIALIAS)

#         # canvas.config(width=pilimagePhotoImage.width, height=pilimagePhotoImage.height)
#         pilimagePhotoImage = ImageTk.PhotoImage(pilimagePhotoImage)
#         # canvas.image = pilimagePhotoImage
#         # canvas.create_image(0, 0, image=pilimagePhotoImage, anchor="nw")
#         load_total_img = (result + 1, len(results))
#         draw_canvas.set_loading_widget(load_total_img)


    

    # threading.Thread(target=seg_image, args=(file_path[0], )).start()
    # threading.Thread(target=seg_image, args=(file_path[1], )).start()

#         for thread in threads:
#             thread.start()

#         for thread in threads:
#             thread.join()
    # with ThreadPool() as pool:
    #     pool.map(seg_image, file_path)

#         processes = []
#         with ThreadPoolExecutor(max_workers=10) as executor:
#             for file in file_path:
#                 processes.append(executor.submit(seg_image, file))

    # print("file_path", file_path)

    load_total_img = None

    seg_loading = False
    # print("ending threads")

        
result_list = []
def log_result(result):
    # This is called whenever foo_pool(i) returns a result.
    # result_list is modified only by the main process, not the pool workers.
    result_list.append(result)
    

def seg_image(files):
    global layers
    
    # print("entered seg_image")
    
    for file in range(len(files)):
        
        load_total_img = (file, len(files))
        draw_canvas.set_loading_widget(load_total_img, True)

    #     image_bgr = cv2.imread(file)

    #     image_rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
    #     sam_result = mask_generator.generate(image_rgb)

    #     print(sam_result[0]['segmentation'])

    #     mask_annotator = sv.MaskAnnotator()

    #     detections = sv.Detections.from_sam(sam_result=sam_result)

    #     annotated_image = mask_annotator.annotate(scene=image_bgr.copy(), detections=detections)



        # color_coverted = cv2.cvtColor(annotated_image, cv2.COLOR_BGR2RGB)
        color_coverted = cv2.cvtColor(sv.MaskAnnotator().annotate(scene=cv2.imread(files[file]).copy(), detections=sv.Detections.from_sam(sam_result=mask_generator.generate(cv2.cvtColor(cv2.imread(files[file]), cv2.COLOR_BGR2RGB)))), cv2.COLOR_BGR2RGB)

        # print("processing done")

        # Displaying the converted image
        pilimage = Image.fromarray(color_coverted)

        # pilimage = Image.open(file_path)
        width, height = int(pilimage.width), int(pilimage.height)
        pilimagePhotoImage = pilimage.resize((width, height), Image.ANTIALIAS)

        # canvas.config(width=pilimagePhotoImage.width, height=pilimagePhotoImage.height)
        pilimagePhotoImage = ImageTk.PhotoImage(pilimagePhotoImage)
        # canvas.image = pilimagePhotoImage
        # canvas.create_image(0, 0, image=pilimagePhotoImage, anchor="nw")


        masks = [
            mask['segmentation']
            for mask
            in sorted(mask_generator.generate(cv2.cvtColor(cv2.imread(files[file]), cv2.COLOR_BGR2RGB)), key=lambda x: x['area'], reverse=True)
        ]

        maskarr = []

        for i in range(len(masks)):
            data = Image.fromarray(masks[i])
            width, height = int(data.width), int(data.height)
            maskImg = data.resize((width, height), Image.ANTIALIAS)
            maskarr.append(Mask("mask " + str(i), maskImg))
            
        if not layers:

            draw_canvas.set_image(pilimage)

            # print("canvas set")

        layers.append(Layer(files[file].split("/")[-1], pilimage, maskarr))

        # print("file_path 2", files[file])

        listbox_layer.insert(END, files[file].split("/")[-1])
        
    draw_canvas.set_loading_widget(0, False)
        

def change_color():
    global pen_color
    pen_color = colorchooser.askcolor(title="Select Pen Color")[1]

def change_size(size):
    global pen_size
    pen_size = size

# def draw(event):
#     global drawing
    
#     if showing_mask:
#         drawing = ImageDraw.Draw(layers[curr_layer_idx].masks[curr_mask_idx].data)
#     else:
#         drawing = ImageDraw.Draw(layers[curr_layer_idx].data)
    
#     x1, y1 = (event.x - pen_size), (event.y - pen_size)
#     x2, y2 = (event.x + pen_size), (event.y + pen_size)
#     # canvas.create_oval(x1, y1, x2, y2, fill=pen_color, outline='')
#     drawing.ellipse([(x1, y1), (x2, y2)], fill=pen_color)

# def delete_layer():
#     for i in listbox_layer.curselection():
#         print(listbox_layer.get(i))
#         listbox_layer.delete(i + 1)
#         layers.pop(i)
        
def set_draw_tool():
     draw_canvas.set_draw("draw")
        
def set_move_tool():
    draw_canvas.set_draw("move")
    
# def save_img():
#     if showing_mask:
#         layers[curr_layer_idx].masks[curr_mask_idx].data.show()
#         layers[curr_layer_idx].masks[curr_mask_idx].data.save("/Users/shanmuk/Downloads/test001.png")
#     else:
#         layers[curr_layer_idx].data.show()
#         layers[curr_layer_idx].data.save("/Users/shanmuk/Downloads/test001.png")

def save_img():
    dir_name = filedialog.askdirectory() # asks user to choose a directory
    # print("dir_name", dir_name)
    for layer in layers:
        for mask in layer.masks:
            save_image = mask.data
            image_filename = mask.name
            save_image.save(dir_name + "/" + image_filename + "_" + str(uuid.uuid4()) + ".png")
        
# def clear_canvas():
    
#     if showing_mask:
#         clear_draw = ImageDraw.Draw(layers[curr_layer_idx].masks[curr_mask_idx].data)
#     else:
#         clear_draw = ImageDraw.Draw(layers[curr_layer_idx].data)
    
#     # canvas.delete("all")
#     # canvas.create_image(0, 0, image=canvas.image, anchor="nw")
#     clear_draw.rectangle() 

# def apply_filter(filter):
#     image = Image.open(file_path)
#     width, height = int(image.width / 2), int(image.height / 2)
#     image = image.resize((width, height), Image.ANTIALIAS)
#     if filter == "Black and White":
#         image = ImageOps.grayscale(image)
#     elif filter == "Blur":
#         image = image.filter(ImageFilter.BLUR)
#     elif filter == "Sharpen":
#         image = image.filter(ImageFilter.SHARPEN)
#     elif filter == "Smooth":
#         image = image.filter(ImageFilter.SMOOTH)
#     elif filter == "Emboss":
#         image = image.filter(ImageFilter.EMBOSS)
#     image = ImageTk.PhotoImage(image)
#     # canvas.image = image
#     # canvas.create_image(0, 0, image=image, anchor="nw")

def do_popup(event):
    try:
        m.tk_popup(event.x_root, event.y_root)
    finally:
        m.grab_release()

def slider_changed(event):
    draw_canvas.set_pen_size(pen_size_slider.get())

left_frame = ttk.Frame(root, width=200, height=600)
left_frame.pack(side="left", fill="y")

right_frame = ttk.Frame(root, width=200, height=600)
right_frame.pack(side="right", fill="y")

right_frame_image_list = ttk.Frame(right_frame)
right_frame_image_list.pack()

right_frame_masks_list = ttk.Frame(right_frame)
right_frame_masks_list.pack()

# canvas = tkinter.Canvas(root, width=750, height=600)
# canvas.pack()

# canvas.bind("<B1-Motion>", draw)

draw_canvas = Application(master=root)

image_button_icon = ImageTk.PhotoImage(Image.open("add-folder-modified.png").resize((20,20), Image.ANTIALIAS))

image_button = ttk.Button(left_frame, image=image_button_icon, command=add_image)
image_button.pack(padx = 15, pady = 7.5)

color_button_icon = ImageTk.PhotoImage(Image.open("color-wheel-modified.png").resize((20,20), Image.ANTIALIAS))

color_button = ttk.Button(left_frame, image=color_button_icon, command=change_color)
color_button.pack(padx = 15, pady = 7.5)

# pen_size_frame = ttk.Frame(left_frame)
# pen_size_frame.pack()

# pen_size_1 = Radiobutton(
#     pen_size_frame, text="Small", value=3, command=lambda: change_size(3))
# pen_size_1.pack(side="left")

# pen_size_2 = Radiobutton(
#     pen_size_frame, text="Medium", value=5, command=lambda: change_size(5))
# pen_size_2.pack(side="left")
# pen_size_2.select()

# pen_size_3 = Radiobutton(
#     pen_size_frame, text="Large", value=7, command=lambda: change_size(7))
# pen_size_3.pack(side="left")

# clear_button = ttk.Button(left_frame, text="Clear", command=clear_canvas)
# clear_button.pack()

save_button_icon = ImageTk.PhotoImage(Image.open("download-modified.png").resize((20,20), Image.ANTIALIAS))

save_button = ttk.Button(left_frame, image=save_button_icon, command=save_img)
save_button.pack(padx = 15, pady = 7.5)

move_button_icon = ImageTk.PhotoImage(Image.open("move-modified.png").resize((20,20), Image.ANTIALIAS))

move_button = ttk.Button(left_frame, image=move_button_icon, command=set_move_tool)
move_button.pack(padx = 15, pady = 7.5)

draw_button_icon = ImageTk.PhotoImage(Image.open("pencil-modified.png").resize((20,20), Image.ANTIALIAS))

draw_button = ttk.Button(left_frame, image=draw_button_icon, command=set_draw_tool)
draw_button.pack(padx = 15, pady = 7.5)

pen_size_slider = ttk.Scale(
    left_frame,
    from_=1,
    to=100,
    orient='vertical',
    command=slider_changed
)
pen_size_slider.pack(pady = 7.5)

listbox_layer = EditableListbox(right_frame_image_list)
listbox_layer.isMask(False)
listbox_layer_scrollbar = ttk.Scrollbar(right_frame_image_list, command=listbox_layer.yview)
listbox_layer.configure(yscrollcommand=listbox_layer_scrollbar.set)

listbox_layer_scrollbar.pack(side="right", fill="y")
listbox_layer.pack(side="left", fill="both", expand=True)

listbox_masks = EditableListbox(right_frame_masks_list)
listbox_masks.isMask(True)
listbox_masks_scrollbar = ttk.Scrollbar(right_frame_masks_list, command=listbox_masks.yview)
listbox_masks.configure(yscrollcommand=listbox_masks_scrollbar.set)

listbox_masks_scrollbar.pack(side="right", fill="y")
listbox_masks.pack(side="left", fill="both", expand=True)

# listbox_layer_delete = ttk.Button(right_frame, text="Delete", command=delete_layer)
# listbox_layer_delete.pack()

# listbox_layer_show = ttk.Button(right_frame, text="Show Image", command=show_layer)
# listbox_layer_show.pack()

# listbox_masks_show = ttk.Button(right_frame, text="Show Mask", command=show_masks)
# listbox_masks_show.pack()

# filter_label = ttk.Label(left_frame, text="Select Filter")
# filter_label.pack()
# filter_combobox = ttk.Combobox(left_frame, values=["Black and White", "Blur",
#                                              "Emboss", "Sharpen", "Smooth"])
# filter_combobox.pack()

# filter_combobox.bind("<<ComboboxSelected>>",
#                      lambda event: apply_filter(filter_combobox.get()))

sv_ttk.set_theme("dark")

root.mainloop()

# if __name__ == '__main__':
#     thread.start_new_thread(threadmain, ())


# In[ ]:




