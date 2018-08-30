
from __future__ import print_function

import gi

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, Gio, GObject, GdkPixbuf

from PIL import Image
from paths import paths

import os




class Config():
    def __init__(self):
        # parameters
        self.PIECE_WIDTH = 0

        self.w = self.h = self.img_cropped = self.LINES = 0
        self.COLUMNS = 1


        self.scale_min = self.scale_max = self.scale_value = self.black \
            = self.doc = self.tag_key = None

        self.keys = [["Current", "#2196f3"], ["None", "#e8e8e7"], ["Sparse", "green"],
                     ["Medium", "yellow"], ["Dense", "red"]]
        self.current_position = 0
        self.current_value = 0


        self.P_W_viewed = 150
        self.safe_space_x = 60.0
        self.safe_space_y = 190.0

        self.tag_piece = 0
        self.i_adj = Gtk.Adjustment(0, 0, 0, 1, 5.0, 0.0)
        self.x_adj = Gtk.Adjustment(0, 0, 0, 1, 5.0, 0.0)
        self.y_adj = Gtk.Adjustment(0, 0, 0, 1, 5.0, 0.0)


        self.pp = 4  # width of lines displayed

    def set_imageManipulate(self, imageManipulate):
        self.imageManipulate = imageManipulate

    def get_position(self, i):
        return i % self.COLUMNS, i / self.COLUMNS

    def new_PIECE_WIDTH(self):
        w, h = self.img_original.size
        if not self.PIECE_WIDTH:
            self.PIECE_WIDTH = int(h / 5)
        # w, h = 300, 400

        self.w = w - w % self.PIECE_WIDTH
        self.h = h - h % self.PIECE_WIDTH
        self.img_cropped = self.img_original.crop((0, 0, self.w, self.h))
        self.LINES = int(self.h / self.PIECE_WIDTH)
        self.COLUMNS = int(self.w / self.PIECE_WIDTH)


        self.i_adj.set_upper(self.COLUMNS * self.LINES - 1)
        self.x_adj.set_upper(self.COLUMNS - 1)
        self.y_adj.set_upper(self.LINES - 1)

        self.current_position = 0

    def new_image(self):
        print('-'*300)
        print(paths.img_name_original)
        try:
            self.img_original = Image.open(paths.img_name_original)
        except IOError:
            self.img_original = Image.new("RGB", (800, 800), "Black")

        self.hashcode = paths.get_img_hashcode()



        win = Gtk.Window()
        w, h = self.img_original.size
        self.scale_min = int(min(900.0 / w, 450.0 / h) * 10 + 1) / 10.0
        self.scale_max = min((win.get_screen().get_width() - self.safe_space_x) / w,
                             (win.get_screen().get_height() - self.safe_space_y) / h)
        self.scale_value = (self.scale_min + self.scale_max) / 2
        print("scale value in init", self.scale_value)

        self.new_PIECE_WIDTH()

        self.black = max(self.img_original.getcolors(self.img_original.size[0] * self.img_original.size[1]))[1]
        self.black = (255 - self.black[0], 255 - self.black[1], 255 - self.black[2])




    def __str__(self):
        return ('<<< Config Class >>>')


config = Config()
