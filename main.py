#!/bin/python2

from __future__ import print_function

import gi


gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, Gio, GObject, GdkPixbuf



from main_window import MainWindow
from config import config
from image_manipulate import imageManipulate
from paths import paths
from JSON_mod import JSON_mod


class MyApplication(Gtk.Application):
    def __init__(self):
        Gtk.Application.__init__(self)
        paths.set_config(config)
        paths.create_dirs()
        config.set_imageManipulate(imageManipulate)
        self.first_initiate()

    def first_initiate(self):
        paths.initiate_img_paths()
        data_imported = JSON_mod.import_data()
        JSON_mod.conf_create_or_import_conf_file()
        JSON_mod.params_create_or_import_params_file()
        paths.create_keys_dirs()
        if data_imported: config.new_image()
        imageManipulate.crop_pieces()

    def do_activate(self):
        win = MainWindow(app=self)
        # win.connect("delete-event", Gtk.main_quit)
        win.connect("key_press_event", win.press_key_event)
        win.set_resizable(False)
        win.show_all()

    def do_startup(self):
        Gtk.Application.do_startup(self)

        #  the actions related to the application
        quit_action = Gio.SimpleAction.new("quit", None)
        quit_action.connect("activate", self.quit_callback)
        self.add_action(quit_action)

    def quit_callback(self, action, parameter):
        print("Quitting...")
        self.quit()


if __name__ == "__main__":
    app = MyApplication()
    app.run()
    app.quit()
