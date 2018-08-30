#!/bin/python3


from __future__ import print_function

import re

import gi

from JSON_mod import JSON_mod
from image_manipulate import imageManipulate

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, Gio, GObject, GdkPixbuf

from PIL import Image


import os, glob
from shutil import rmtree


from config import config
from paths import paths


class WindowParameters(Gtk.Dialog):
    def __init__(self, parent):
        # Gtk.Window.__init__(self, title="Simple Notebook Example")
        Gtk.Dialog.__init__(self, "All Parameters", parent, 0)
        # self.connect("realize", self.entry_icon_event)
        self.set_border_width(10)
        self.set_default_size(100, 700)


        self.parent = parent

        self.treeview = None

        self.notebook = Gtk.Notebook()

        # page_1
        self.page1 = Gtk.VBox()
        self.page1.set_border_width(10)
        self.notebook.append_page(self.page1, Gtk.Label('Original Image'))
        self.path = paths.img_sample

        self.image_item = Gtk.Image()
        self.page1.pack_end(self.image_item, False, False, 0)

        self.input_img_p = Gtk.Entry()
        self.input_img_p.set_icon_from_icon_name(Gtk.EntryIconPosition.SECONDARY, "document-open")
        self.input_img_p.set_text(paths.img_abs_path)
        # self.image_path.set_icon_activatable(True)
        self.input_img_p.connect("icon_press", self.entry_icon_event)
        self.input_img_p.connect("activate", self.new_image_path)
        self.page1.pack_start(self.input_img_p, False, False, 0)

        # page_2
        self.page2 = Gtk.VBox(spacing=16)
        self.page2.set_border_width(10)
        self.notebook.append_page(self.page2, Gtk.Label('PIECE_WIDTH'))
        self.scale_button = Gtk.Scale()
        self.scale_button.set_increments(2, 10)
        self.scale_button.set_digits(0)

        self.scale_button.connect('button_release_event', self.on_change_pw)
        self.page2.pack_start(self.scale_button, False, False, 0)
        self.P_W_preview = Gtk.Image()
        self.page2.pack_start(self.P_W_preview, True, False, 0)

        # page_3
        self.page3 = Gtk.VBox(spacing=16)
        self.page3.set_border_width(10)
        self.notebook.append_page(self.page3, Gtk.Label('Scale View'))
        self.scale_button_2 = Gtk.Scale()
        self.scale_button_2.set_increments(2, 10)
        self.scale_button_2.set_digits(2)

        self.scale_button_2.connect('button_release_event', self.on_change_scale)
        self.page3.pack_start(self.scale_button_2, False, False, 0)
        self.S_V_preview = Gtk.Image()
        self.page3.pack_end(self.S_V_preview, False, False, 0)

        # page_4
        self.page4 = Gtk.VBox(spacing=16)
        self.page4.set_border_width(10)
        self.notebook.append_page(self.page4, Gtk.Label('Labels'))
        self.treeview = CellRendererToggleWindow(parent)
        self.change_image_begin()
        self.page4_result = self.treeview.get_result()
        self.page4.add(self.page4_result)

        box = self.get_content_area()
        box.add(self.notebook)
        self.show_all()
        self.set_resizable(False)

    def entry_icon_event(self, widget, *args):  # (.. , icon, event):
        # print(icon == Gtk.EntryIconPosition.SECONDARY)
        print("opening image")
        self.open_image()

    def on_change_pw(self, widget, *args):
        if len(args) == 0:
            self.on_change_pw_part_2()
        elif config.PIECE_WIDTH != int(widget.get_value()):
            response = Gtk.ResponseType.OK
            if len(args):
                response = self.show_warning()
                if response == Gtk.ResponseType.OK:
                    config.PIECE_WIDTH = int(widget.get_value())
                    config.new_PIECE_WIDTH()

                    # remove pieces
                    for file in glob.glob(os.path.join(paths.results_final, '*/*.jpg')):
                        if paths.img_stamp in file:
                            os.remove(file)
                    JSON_mod.new_PW()
                    imageManipulate.crop_pieces()

                    self.on_change_pw_part_2()
                elif response == Gtk.ResponseType.CANCEL:
                    widget.set_value(config.PIECE_WIDTH)
            elif response == Gtk.ResponseType.OK:
                self.on_change_pw_part_2()

    def on_change_pw_part_2(self):
        imageManipulate.refresh_preview_part(config.COLUMNS / 2, config.LINES / 2)
        self.P_W_preview.set_from_file(paths.tmp_current)

        if self.treeview:  self.treeview.new_piece_width()

        w, h = config.img_cropped.size
        self.img_s_1 = config.img_cropped.resize((int(w * config.scale_min), int(h * config.scale_min)),
                                                 Image.ANTIALIAS)
        self.img_s_1.save(paths.tmp_original_preview, 'JPEG', quality=100)
        self.image_item.set_from_file(paths.tmp_original_preview)

    def on_change_scale(self, widget, *args):
        # print(widget.get_value())
        if widget.get_value(): config.scale_value = widget.get_value()
        w, h = config.img_original.size

        im = config.img_cropped.resize((int(w * config.scale_value), int(h * config.scale_value)), Image.ANTIALIAS)
        im = im.crop((0, 0, self.img_s_1.size[0], self.img_s_1.size[1]))
        im.save(os.path.join("tmp", "scale_preview.jpg"), 'JPEG', quality=100)
        self.S_V_preview.set_from_file(os.path.join("tmp", "scale_preview.jpg"))

        # xml stuff
        #parameters_xml = config.doc.documentElement.getElementsByTagName("parameters")[0]
        #parameters_xml.getElementsByTagName("SView")[0].childNodes[0].data = str(config.scale_value)

    def open_image(self, *args):
        self.parent.open_image()
        self.destroy()

    def new_image_path(self, *args):
        if type(args[0]) is str: text = args[0]
        else: text = args[0].get_text()
        print(text)
        self.original_name = text

        self.input_img_p.set_text(text)
        self.change_image()

    def change_image(self):
        # page_1
        config.new_image()
        self.change_image_begin()

    def change_image_begin(self):
        w, h = config.img_original.size
        # config.scale_min = 1
        self.treeview.set_initial_scale_value(config.scale_min)  # from page_4
        self.img_s_1 = config.img_cropped.resize((int(w * config.scale_min), int(h * config.scale_min)),
                                                 Image.ANTIALIAS)
        self.img_s_1.save(paths.tmp_original_preview, 'JPEG', quality=100)
        self.image_item.set_from_file(paths.tmp_original_preview)

        # page_2
        self.scale_button.set_range(20, min(config.img_original.size) / 3)
        self.scale_button.set_value(config.PIECE_WIDTH)
        self.on_change_pw(self.scale_button)

        # page_3
        self.scale_button_2.set_range(config.scale_min, config.scale_max)
        self.scale_button_2.set_value(config.scale_value)
        self.on_change_scale(widget=self.scale_button_2)

        # page_4
        self.treeview.new_piece_width()

    def show_warning(self):
        dialog = Gtk.MessageDialog(self, 0, Gtk.MessageType.WARNING, (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                                                                      Gtk.STOCK_OK, Gtk.ResponseType.OK),
                                   "Your progress can'be removed")
        dialog.format_secondary_text("Assigning a new width will automtically remove all your data")
        response = dialog.run()
        dialog.destroy()
        return response


class CellRendererToggleWindow():
    def __init__(self, parent):
        # Gtk.Window.__init__(self, title="CellRendererToggle Example")
        self.parent = parent

        self.liststore = Gtk.ListStore(str, str)

        self.liststore.append([config.keys[0][0], config.keys[0][1]])
        for k in config.keys[2:]:
            self.liststore.append([k[0], k[1]])


        treeview = Gtk.TreeView(model=self.liststore)
        col_min_width = 150

        # text
        renderer_text = Gtk.CellRendererText()
        column_text = Gtk.TreeViewColumn("Label", renderer_text, text=0)
        column_text.set_min_width(col_min_width)
        treeview.append_column(column_text)
        renderer_text.set_property("editable", True)
        renderer_text.connect("edited", self.text_edited)

        # colors
        list = ["Red", "Green", "Blue", "Yellow", "Orange", "Pink", "Brown", "Purple", "White", "Black", "Gray"]
        self.liststore_colors = Gtk.ListStore(str)
        for item in list:
            self.liststore_colors.append([item])

        renderer_combo = Gtk.CellRendererCombo()
        renderer_combo.set_property("editable", True)
        renderer_combo.set_property("model", self.liststore_colors)
        renderer_combo.set_property("text-column", 0)
        renderer_combo.set_property("has-entry", False)
        renderer_combo.connect("edited", self.on_select_color)

        column_combo = Gtk.TreeViewColumn("Color", renderer_combo, text=1)
        column_combo.set_min_width(col_min_width)
        treeview.append_column(column_combo)
        # treeview.override_background_color(Gtk.StateFlags.PRELIGHT, Gdk.RGBA(255,0,0,255))


        # pixbuf
        treeview.columns_autosize()

        self.box = Gtk.VBox(spacing=0)
        self.box.pack_start(treeview, False, False, 0)

        hbox = Gtk.Box()
        image = Gtk.Image()
        image.set_from_stock(Gtk.STOCK_ADD, Gtk.IconSize.BUTTON)

        self.box.pack_start(hbox, False, False, 15)

        # drawing pieces

        self.labels_preview = Gtk.Image.new_from_file(paths.tmp_labels_preview)

        self.box.pack_end(self.labels_preview, False, False, 0)

        self.adding = 4

    def text_edited(self, widget, path, text):
        path = int(path)
        if path:
            v = True
            for k in config.keys:
                if text == k[0]: v = False; break;
            if v:
                # TODO:
                # config.tag_key[path + 1].childNodes[0].data = text
                os.rename(paths.get_key_results_path(config.keys[path + 1][0]),
                          os.path.join(paths.results_final, text))
                ##! I failed changing menu labels :'(
                ##
                self.parent.radio_buttons[path - 1].set_label(text)
                self.parent.menu_popup_items[path - 1].set_label(text)
                ##
                self.liststore[path][0] = text
                config.keys[path + 1][0] = text
                JSON_mod.conf['keys'][path + 1]['name'] = text
                print("text edited successfully")
            else:
                print("~> this label does already exist")

    def on_select_color(self, widget, path, text):
        # print((path, len(config.tag_key)))
        self.liststore[path][1] = text
        path = int(path)
        if path != 0: path += 1
        config.keys[path][1] = text
        JSON_mod.conf['keys'][path]['color'] = text
        imageManipulate.window_parameters_draw_image()
        self.labels_preview.set_from_file(paths.tmp_labels_preview)
        # TODO:
        #config.tag_key[path].setAttribute("color", text)

    def new_piece_width(self):
        self.PIECE_WIDTH = int(config.PIECE_WIDTH * self.initial_scale_value)
        imageManipulate.window_parameters_draw_image()
        self.labels_preview.set_from_file(paths.tmp_labels_preview)

    def set_initial_scale_value(self, scale_value):
        self.initial_scale_value = scale_value

    def get_result(self):
        return self.box


class CellRendererClickablePixbuf(Gtk.CellRendererPixbuf):
    __gsignals__ = {'clicked': (GObject.SIGNAL_RUN_LAST, GObject.TYPE_NONE,
                                (GObject.TYPE_STRING,))
                    }

    def __init__(self):
        Gtk.CellRendererPixbuf.__init__(self)
        self.set_property('mode', Gtk.CellRendererMode.ACTIVATABLE)

    def do_activate(self, event, widget, path, background_area, cell_area,
                    flags):
        self.emit('clicked', path)