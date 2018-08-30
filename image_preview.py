#!/bin/python3

from __future__ import print_function

import gi


gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, Gio, GObject, GdkPixbuf

from PIL import ImageDraw


import os




from config import config
from paths import paths
from image_manipulate import imageManipulate



class ImagePreview(Gtk.Dialog):
    def __init__(self, parent, hide):
        # change_it: scale value will change the dimensions of dialog window
        concerned_label = config.keys[hide][0]
        print(hide)

        Gtk.Dialog.__init__(self, "View " + concerned_label, parent, 0, (Gtk.STOCK_OK, Gtk.ResponseType.OK))

        box = self.get_content_area()
        box.set_spacing(30)

        self.keys_icons = [Gtk.Image() for i in range(2, len(config.keys))]

        self.original_image = Gtk.Image()
        self.initiate_preview(hide)

        ##keys
        try: os.makedirs("keys")
        except OSError: pass

        hbox = Gtk.Box(spacing=20)


        for i in range(2, len(config.keys)):
            b = Gtk.EventBox()
            b.connect('button_press_event', self.refresh_img, i)
            b.add(self.keys_icons[i-2])
            hbox.pack_start(b, False, False, 0)
            hbox.pack_start(Gtk.Label(config.keys[i][0]), False, False, 0)

        b = Gtk.EventBox()
        b.connect('button_press_event', self.refresh_img, 1)
        b.add(Gtk.Image.new_from_file(paths.get_key_icon_path('current')))
        hbox.pack_end(Gtk.Label("current"), False, False, 0)
        hbox.pack_end(b, False, False, 0)

        original_image_e = Gtk.EventBox()
        original_image_e.connect("button_press_event", self.motion_notify)
        original_image_e.add(self.original_image)
        box.add(original_image_e)
        box.add(hbox)

        self.show_all()
        self.set_resizable(False)

    def initiate_preview(self, hide):

        ##original image
        img = config.img_cropped.copy()
        draw = ImageDraw.Draw(img)

        # draw diffrent colors
        imageManipulate.image_preview_draw_rectangles(draw, hide)

        # draw current
        imageManipulate.image_preview_draw_current_pos(draw)

        # saving
        imageManipulate.image_preview_save_draw(img)

        self.original_image.set_from_file(paths.tmp_open_image)

        # generate keys
        imageManipulate.image_preview_generate_keys(hide)

        for i in range(2, len(config.keys)):
            self.keys_icons[i - 2].set_from_file(paths.get_key_icon_path(str(i - 1)))

    def refresh_img(self, *args):
        hide = args[-1]
        self.initiate_preview(hide)


    def motion_notify(self, widget, event):
        x, y = (int(event.x / (config.PIECE_WIDTH * config.scale_value)),
                int(event.y / (config.PIECE_WIDTH * config.scale_value)))
        config.current_position = x + y * config.COLUMNS
        if (x < config.COLUMNS) & (y < config.LINES):
            print("mouse position : ", (x, y), config.current_position)
            self.destroy()


    def press_key_event(self, widget, event):
        if event.string in ("o", "O"):
            self.destroy()