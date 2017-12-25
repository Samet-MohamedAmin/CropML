#! /bin/python2

from __future__ import print_function

import gi

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, Gio, GObject, GdkPixbuf

from PIL import Image, ImageDraw

import xml.dom.minidom as minidom

import hashlib, io, os
from shutil import copyfile, move, rmtree


class GridWindow(Gtk.ApplicationWindow):
    def __init__(self, app):
        Gtk.Window.__init__(self, title="CropML", application=app)
        self.set_default_icon_from_file("logo.png")
        self.p = app
        self.create_img_directory()

        Gtk.Window.__init__(self, title="Project")
        layout = Gtk.VBox()

        # HEADER_BAR
        self.header = Gtk.HeaderBar()
        Gtk.HeaderBar.set_show_close_button(self.header, True)
        Gtk.HeaderBar.set_title(self.header, "CropML Project")
        Gtk.HeaderBar.set_has_subtitle(self.header, False)

        self.set_titlebar(self.header)

        # main menu
        self.view_label_action = []
        self.test_clear_action = []
        self.make_menu_file()
        self.make_menu_parameters()
        self.make_menu_about()
        self.clicked_area = 0
        self.menu_popup = Gtk.Menu()
        self.make_menu_popup()

        # main box
        main_box = Gtk.Box(spacing=20)
        # menu
        button2 = Gtk.Button(label="save")
        button2.connect("clicked", self.deal_with_xml)

        # right widget
        right_widget = Gtk.VBox(spacing=10)
        # right_widget.set_border_width(20)
        right_widget.set_margin_right(10)
        right_widget.set_valign(Gtk.Align.CENTER)
        # postion labels
        # self.button3 = Gtk.Label("value_1")
        hbox_postion = Gtk.Box(spacing=10)
        # this is i
        hbox1_postion = Gtk.Box(spacing=10)
        i_label = Gtk.Label("i :")
        i_spin = Gtk.SpinButton()
        i_spin.set_adjustment(self.p.i_adj)
        i_spin.set_wrap(True)

        # event i_adj
        self.p.i_adj.connect("value_changed", self.change_position_i)

        hbox1_postion.pack_start(i_label, False, False, 0)
        hbox1_postion.pack_start(i_spin, False, False, 0)
        # this is x
        x_label = Gtk.Label("x :")
        x_spin = Gtk.SpinButton()
        x_spin.set_adjustment(self.p.x_adj)
        x_spin.set_wrap(True)
        # this is y
        y_label = Gtk.Label("y :")
        y_spin = Gtk.SpinButton()
        y_spin.set_adjustment(self.p.y_adj)
        y_spin.set_wrap(True)

        # event x_adj & y_adj
        self.p.x_adj.connect("value_changed", self.change_position_x)
        self.p.y_adj.connect("value_changed", self.change_position_y)

        hbox_postion.pack_start(x_label, False, False, 0)
        hbox_postion.pack_start(x_spin, False, False, 0)
        hbox_postion.pack_start(y_label, False, False, 0)
        hbox_postion.pack_start(y_spin, False, False, 0)

        self.button3 = hbox_postion

        hbox = Gtk.Box(spacing=4)
        # radio buttons
        self.radio_buttons = []

        self.noneButton = Gtk.RadioButton.new_with_label_from_widget(None, "None")
        self.noneButton.connect("toggled", self.on_button_toggled)
        hbox.pack_start(self.noneButton, False, False, 0)

        for i in range(2, len(self.p.keys)):
            self.radio_buttons.append(Gtk.RadioButton.new_with_label_from_widget(self.noneButton, self.p.keys[i][0]))
            self.radio_buttons[-1].connect("toggled", self.on_button_toggled)
            hbox.pack_start(self.radio_buttons[-1], False, False, 0)

        self.button4 = hbox

        right_widget.pack_start(hbox1_postion, False, False, 0)

        hbox1_postion.set_halign(3)
        right_widget.pack_start(self.button3, False, False, 0)
        right_widget.pack_start(self.button4, False, False, 0)
        right_widget.pack_end(button2, False, False, 0)

        # left widget

        self.center_image_e = Gtk.EventBox()
        self.center_image_e.set_tooltip_text("hello")

        self.myImage = Gtk.Image.new_from_file(os.path.join("tmp", "img_current.jpg"))
        self.button_center = self.myImage

        self.center_image_e.add(self.button_center)

        # packing..........

        main_box.pack_start(self.center_image_e, False, False, 0)
        main_box.pack_end(right_widget, False, False, 0)
        layout.pack_end(main_box, False, False, 0)
        self.add(layout)

        # self.center_image_e.connect("button_press_event", self.open_original, ("original"))
        # self.center_image_e.connect("button_press_event", self.press_current_img)
        self.center_image_e.connect_object("button_press_event", self.press_current_img, self.menu_popup)
        self.center_image_e.connect("motion-notify-event", self.set_tooltip_text)

        # now I can change position

        self.change_position()

    def get_index_label(self, s):
        for i in range(2, len(self.p.keys)):
            if self.p.keys[i][0] == s:
                return i - 2
        return -1

    def make_menu_file(self):
        menu_menu = Gtk.MenuButton()
        menu_menu.add(Gtk.Image.new_from_icon_name("open-menu-symbolic", Gtk.IconSize.MENU))

        # a menu with two actions
        menu_model = Gio.Menu()
        menu_model.append("Open", "win.open")
        menu_model.append("export GroundTruth", "win.export_ground_truth")

        # the action related to the window (get_ground_truth)
        ground_truth_action = Gio.SimpleAction.new("export_ground_truth", None)
        ground_truth_action.connect("activate", self.export_ground_truth)
        self.add_action(ground_truth_action)

        # a submenu with one action for the menu
        submenu = Gio.Menu()
        submenu.append("Original", "win.view_original")
        submenu2 = Gio.Menu()
        for i in range(2, len(self.p.keys)):
            submenu2.append(self.p.keys[i][0], "win.view_" + self.p.keys[i][0])
            # the action related to the window (view label)
            self.view_label_action.append(Gio.SimpleAction.new("view_" + self.p.keys[i][0], None))
            self.view_label_action[-1].connect("activate", self.open_original, (self.p.keys[i][0]))
            self.add_action(self.view_label_action[-1])
        submenu.append_section("specific", submenu2)
        menu_model.append_submenu("View", submenu)

        # the action related to the window (view_original)
        view_original_action = Gio.SimpleAction.new("view_original", None)
        view_original_action.connect("activate", self.open_original)
        self.add_action(view_original_action)

        # a submenu with one action for the menu
        submenu = Gio.Menu()
        submenu.append("All", "win.clear_all")
        submenu2 = Gio.Menu()
        for i in range(2, len(self.p.keys)):
            submenu2.append(self.p.keys[i][0], "win.clear_" + self.p.keys[i][0])
            # the action related to the window (clear label)
            self.test_clear_action.append(Gio.SimpleAction.new("clear_" + self.p.keys[i][0], None))
            self.test_clear_action[-1].connect("activate", self.test_clear)
            self.add_action(self.test_clear_action[-1])

        submenu.append_section("specific", submenu2)
        menu_model.append_submenu("Clear", submenu)

        submenu2 = Gio.Menu()
        submenu2.append("Quit", "app.quit")
        menu_model.append_section(None, submenu2)

        # the action related to the window (open)
        open_action = Gio.SimpleAction.new("open", None)
        open_action.connect("activate", self.open_image)
        self.add_action(open_action)

        # the action related to the window (Clear All)
        clear_all_action = Gio.SimpleAction.new("clear_all", None)
        clear_all_action.connect("activate", self.clear_it)
        self.add_action(clear_all_action)

        # the menu is set as the menu of the menubutton
        menu_menu.set_menu_model(menu_model)

        self.header.pack_start(menu_menu)

    def make_menu_parameters(self):
        menu_preferences = Gtk.Button()
        menu_preferences.add(Gtk.Image.new_from_icon_name("preferences-system-symbolic", Gtk.IconSize.MENU))

        menu_preferences.connect("clicked", self.open_parameters)

        self.header.pack_start(menu_preferences)

    def make_menu_about(self):
        menu_abut = Gtk.Button()
        menu_abut.add(Gtk.Image.new_from_icon_name("help-about-symbolic", Gtk.IconSize.MENU))
        menu_abut.connect("clicked", self.open_about)

        self.header.pack_end(menu_abut)

    def set_tooltip_text(self, widget, event):
        x, y = (int(event.x / self.p.P_W_viewed),
                int(event.y / self.p.P_W_viewed))
        text = "open original"
        if (x, y) == (1, 0):
            text = "move Up"
        elif (x, y) == (2, 1):
            text = "move Right"
        elif (x, y) == (1, 2):
            text = "move Down"
        elif (x, y) == (0, 1):
            text = "move Left"
        self.center_image_e.set_tooltip_text(text)

    def change_value(self, *args):
        self.p.keys[1][2] = self.clicked_area
        if args[1] == 0:
            self.noneButton.set_active(True)
        else:
            self.radio_buttons[args[1] - 1].set_active(True)

        self.p.changed_values[self.clicked_area] = args[1]

        self.deal_with_xml()

    def make_menu_popup(self):
        menu_item_none = Gtk.MenuItem(self.p.keys[0][0])
        menu_item_none.connect("activate", self.change_value, 0)
        self.menu_popup.append(menu_item_none)
        self.menu_popup.append(Gtk.SeparatorMenuItem())
        value = 1
        for key in self.p.keys[2:]:
            menu_item = Gtk.MenuItem(key[0])
            menu_item.connect("activate", self.change_value, value)
            self.menu_popup.append(menu_item)
            value += 1
        self.menu_popup.show_all()

    def create_img_directory(self):
        self.p.new_image()

        try:
            os.listdir(os.path.join(self.p.path_results, "xml"))
            self.p.initial_it()
        except OSError:
            os.makedirs(os.path.join(self.p.path_results, "xml"))
            xml_file = open(self.p.path_xml, "w")
            xml_file.close()
            os.mkdir(self.p.path_crop)
            self.crop()
            self.p.initial_xml()
            try:
                os.mkdir("tmp")
            except:
                print("tmp directory does already exist")
            try:
                os.mkdir("keys")
            except:
                print("keys directory does already exist")

        try:
            os.makedirs(os.path.join(self.p.path_final, "ground_truth"))
        except OSError:
            print("\"" + self.p.path_final + "\" does already exist!")

        for key in self.p.keys[2:]:
            try:
                os.mkdir(os.path.join(self.p.path_final, key[0]))
            except OSError:
                print("\"" + os.path.join(self.p.path_final, key[0]) + "\" does already exist!")

        # create None directory
        try:
            os.mkdir(os.path.join(self.p.path_final, self.p.keys[0][0]))
        except OSError:
            print("\"" + os.path.join(self.p.path_final, self.p.keys[0][0]) + "\" does already exist!")

        for i in range(len(self.p.tag_piece)):
            value = int(self.p.tag_piece[i].childNodes[0].data)
            if not value:
                value = -1

            src = os.path.join(self.p.path_crop, self.p.get_piece_path(i))
            dst = os.path.join(self.p.path_final, str(self.p.keys[value + 1][0]), self.p.get_piece_path(i))

            copyfile(src, dst)

    def append_index_keys(self):
        for i in range(2, len(self.p.keys)):
            self.p.keys[i][2] = []
        for i in range(len(self.p.tag_piece)):
            value = int(self.p.tag_piece[i].childNodes[0].data)
            if value:
                self.p.keys[value + 1][2].append(i)
        return self.p.keys

    def crop(self):
        # change_it: piece_width in main window
        self.p.img_cropped.save(self.p.path_results + ".jpg", 'JPEG', quality=100)
        i = 0
        for y in range(0, self.p.h, self.p.PIECE_WIDTH):
            for x in range(0, self.p.w, self.p.PIECE_WIDTH):
                area = (x, y, x + self.p.PIECE_WIDTH, y + self.p.PIECE_WIDTH)
                cropped_img = self.p.img_cropped.crop(area)
                # cropped_img = cropped_img.resize((self.p.P_W_viewed,self.p.P_W_viewed), Image.ANTIALIAS)
                cropped_img.save(os.path.join(self.p.path_crop, self.p.get_piece_path(i)), 'JPEG', quality=100)
                i += 1

    def move_up(self, *args):
        m = self.p.keys[1][2] - self.p.COLUMNS
        if m < 0:
            self.no_more("LINES")
        else:
            self.p.keys[1][2] = m
            self.change_position()

    def move_right(self, *args):
        if (self.p.keys[1][2] + 1) % self.p.COLUMNS == 0:
            self.no_more("COLUMNS")
        else:
            self.p.keys[1][2] += 1
            self.change_position()

    def move_down(self, *args):
        m = self.p.keys[1][2] + self.p.COLUMNS
        if m > self.p.COLUMNS * self.p.LINES - 1:
            self.no_more("LINES")
        else:
            self.p.keys[1][2] = m
            self.change_position()

    def move_left(self, *args):
        if (self.p.keys[1][2]) % self.p.COLUMNS == 0:
            self.no_more("COLUMNS")
        else:
            self.p.keys[1][2] -= 1
            self.change_position()

    def no_more(self, s):
        dialog = Gtk.MessageDialog(self, 0, Gtk.MessageType.ERROR, Gtk.ButtonsType.OK,
                                   "you've exceeded the LIMIT of " + s)
        dialog.format_secondary_text("no more " + s)
        dialog.run()

        dialog.destroy()

    def press_current_img(self, widget, event):
        x, y = (int(event.x / self.p.P_W_viewed),
                int(event.y / self.p.P_W_viewed))

        x_c, y_c = self.p.get_position(self.p.keys[1][2])
        if x_c == self.p.COLUMNS - 1:
            x_c -= 2
        elif x_c != 0:
            x_c -= 1

        if y_c == self.p.LINES - 1:
            y_c -= 2
        elif y_c != 0:
            y_c -= 1
        self.clicked_area = (x_c + x) + (y_c + y) * self.p.COLUMNS

        if event.get_button()[1] == Gdk.BUTTON_SECONDARY:
            self.menu_popup.popup(None, None, None, None, 0, Gtk.get_current_event_time())
        else:
            if (x, y) == (1, 1):
                self.open_original(self.p.keys[self.p.current_value + 1][0])
            elif (x, y) == (1, 0):
                self.move_up()
            elif (x, y) == (2, 1):
                self.move_right()
            elif (x, y) == (1, 2):
                self.move_down()
            elif (x, y) == (0, 1):
                self.move_left()
            else:
                self.open_original("original")

    # change label
    def change_position(self):
        # supposing that the width > height always
        self.p.i_adj.set_value(self.p.keys[1][2])
        x, y = self.p.get_position(self.p.keys[1][2])
        # print("i=", self.p.keys[1][2], "\tx=", x, "\ty=", y)
        self.p.x_adj.set_value(x)
        self.p.y_adj.set_value(y)

        # don't remove that !
        # img_current_tmp = Image.open(os.path.join(self.p.path_crop, self.p.get_piece_path(self.p.keys[1][2])))
        # img_current_tmp = img_current_tmp.resize((self.p.P_W_viewed, self.p.P_W_viewed), Image.ANTIALIAS)
        # img_current_tmp.save(os.path.join("tmp", "img_current.jpg"), 'JPEG', quality=100)

        self.change_position_image(x, y)

        self.button_center.set_from_file(os.path.join("tmp", "img_current.jpg"))
        self.p.current_value = 0
        try:
            self.p.current_value = int(self.p.changed_values[self.p.keys[1][2]])
        except:
            if (self.p.tag_piece * self.p.current_value != 0):
                self.p.current_value = int(self.p.tag_piece[self.p.keys[1][2]].childNodes[0].data)

        n = self.p.current_value - 1
        if n < 0:
            self.noneButton.set_active(True)
        else:
            self.radio_buttons[n].set_active(True)

    def change_position_image(self, x, y):
        p_w_v = self.p.P_W_viewed
        c, l = x, y

        if c != 0:
            if c == self.p.COLUMNS - 1:
                c -= 2
            else:
                c -= 1

        if l != 0:
            if l == self.p.LINES - 1:
                l -= 2
            else:
                l -= 1

        img_current_tmp = self.p.img_cropped.crop((c * self.p.PIECE_WIDTH,
                                                   l * self.p.PIECE_WIDTH,
                                                   (c + 3) * self.p.PIECE_WIDTH,
                                                   (l + 3) * self.p.PIECE_WIDTH))\
            .resize((3 * p_w_v, 3 * p_w_v), Image.ANTIALIAS)
        draw = ImageDraw.Draw(img_current_tmp)

        for i in range(9):
            x_i, y_i = i % 3, i / 3
            r = int(self.p.tag_piece[c + x_i + (l + y_i) * self.p.COLUMNS].childNodes[0].data)
            if r:
                fill = self.p.keys[r + 1][1]
                if fill.upper() == "GREEN":
                    fill = "#4caf50"
                elif fill.upper() == "YELLOW":
                    fill = "#ffeb3b"
                elif fill.upper() == "RED":
                    fill = "#f44336"
                draw.line([x_i * p_w_v, y_i * p_w_v, (x_i + 1) * p_w_v, (y_i + 1) * p_w_v], fill, self.p.pp)
                draw.line([(x_i + 1) * p_w_v, y_i * p_w_v, x_i * p_w_v, (y_i + 1) * p_w_v], fill, self.p.pp)

        for i in (self.p.pp / 2 - 1, p_w_v, 2 * p_w_v, 3 * p_w_v - self.p.pp / 2):  draw.line([i, 0, i, self.p.h],
                                                                                              self.p.black, self.p.pp)
        for i in (self.p.pp / 2 - 1, p_w_v, 2 * p_w_v, 3 * p_w_v - self.p.pp / 2):  draw.line([0, i, self.p.w, i],
                                                                                              self.p.black, self.p.pp)

        for i in range(-1, self.p.pp, 1):
            draw.rectangle(
                [(x - c) * p_w_v + i, (y - l) * p_w_v + i, (x - c + 1) * p_w_v - i + 1, (y - l + 1) * p_w_v - i + 1],
                outline=self.p.keys[1][1])

        img_current_tmp.save(os.path.join("tmp", "img_current.jpg"))

    def change_position_i(self, *args):
        if self.p.keys[1][2] != int(args[0].get_value()):
            self.p.keys[1][2] = int(args[0].get_value())
            print(self.p.keys[1][2])

            self.change_position()

    def change_position_x(self, widget):
        x, y = self.p.get_position(self.p.keys[1][2])
        if x != widget.get_value():
            self.p.keys[1][2] = int(widget.get_value()) + y * self.p.COLUMNS

            self.change_position()

    def change_position_y(self, widget):
        x, y = self.p.get_position(self.p.keys[1][2])
        if y != widget.get_value():
            self.p.keys[1][2] = x + int(widget.get_value()) * self.p.COLUMNS

            self.change_position()

    # entry value changed
    def value_changed(self, widget):
        self.p.changed_values[self.p.keys[1][2]] = widget.get_text()

    def on_button_toggled(self, button):
        if button.get_active():
            if button.get_label() == "None":
                self.p.changed_values[self.p.keys[1][2]] = "0"
            else:
                self.p.changed_values[self.p.keys[1][2]] = str(self.get_index_label(button.get_label()) + 1)

    # save button
    def deal_with_xml(self, *args):
        # current position
        self.p.tag_key[1].setAttribute("current", str(self.p.keys[1][2]))

        # changed_values
        print(self.p.changed_values)
        if self.p.changed_values != {}:
            for i in self.p.changed_values.keys():
                if self.p.tag_piece[i].childNodes[0].data != self.p.changed_values[i]:
                    if int(self.p.changed_values[i]) == 0:
                        k_place_dst = -1
                    else:
                        k_place_dst = int(self.p.changed_values[i])

                    dst = os.path.join(self.p.path_final, self.p.keys[k_place_dst + 1][0],
                                       self.p.get_piece_path(i))

                    if int(self.p.tag_piece[i].childNodes[0].data) == 0:
                        k_place = -1
                    else:
                        k_place = int(self.p.tag_piece[i].childNodes[0].data)

                    src = os.path.join(self.p.path_final,
                                       self.p.keys[k_place + 1][0],
                                       self.p.get_piece_path(i))
                    move(src, dst)
                    self.p.tag_piece[i].childNodes[0].data = self.p.changed_values[i]

            del self.p.changed_values
            self.p.changed_values = {}

            print("overwriting.....")
            xml_file = open(self.p.path_xml, "w+")
            self.p.doc.writexml(xml_file)
            xml_file.close()
        if len(args) & (self.p.keys[1][2] < (self.p.LINES * self.p.COLUMNS - 1)):
            self.p.keys[1][2] += 1

        self.change_position()

    # original_button
    def open_original(self, *args):
        index = self.get_index_label(args[-1]) + 1

        dialog = DialogExample(self, index, self.p.get_position(self.p.keys[1][2]), self.p)

        dialog.connect("key_press_event", dialog.press_key_event)
        dialog.run()
        self.p.keys[1][2] = dialog.getCurrent()
        dialog.destroy()

        self.change_position()

    # parameters_button
    def open_parameters(self, *args):
        print("open parameters")
        self.append_index_keys()
        old_piece_width = self.p.PIECE_WIDTH
        dialog = MyWindow(self, self.p.originalName, self.p.path_results + ".jpg", self.p, self.p.keys)
        dialog.run()
        dialog.destroy()

        for i in range(1, len(self.p.tag_key)):
            self.p.tag_key[i].childNodes[0].data = self.p.keys[i][0]
            self.p.tag_key[i].setAttribute("color", self.p.keys[i][1])

        if old_piece_width != self.p.PIECE_WIDTH:
            if old_piece_width < self.p.PIECE_WIDTH:
                self.p.keys[1][2] = 0
            self.change_position()
            self.p.initial_xml()
            del self.p.changed_values
            self.p.changed_values = {}
            for i in range(2, len(self.p.keys)):
                del (self.p.keys[i][2])
                self.p.keys[i].append([])
            self.button_center.set_from_file(os.path.join("tmp", "img_current.jpg"))

    # about_button
    def open_about(self, *args):
        about_dialog = Gtk.AboutDialog(self)
        about_dialog.set_transient_for(self)

        about_dialog.set_wrap_license(True)
        about_dialog.set_license(
            "CropML is free software: you can redistribute it and/or modify it\nunder the terms of the GNU General "
            "Public License as published by\nthe Free Software Foundation, either version 3 of the License,"
            "\nor (at your option) any later version.\n\nCropML is distributed in the hope that it will be useful, "
            "but WITHOUT\nANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A "
            "PARTICULAR PURPOSE.\n\nSee the GNU General Public License for more details. You should\nhave received a "
            "copy of the GNU General Public License along\nwith CropML. If not, see <http://www.gnu.org/licenses/>.")

        about_dialog.set_program_name("CropML")
        about_dialog.set_version("0.1.4")
        about_dialog.set_copyright("Copyright \xc2\xa9 2017 SAMET MohamedAmin")
        about_dialog.set_authors(["SAMET MohamedAmin"])
        about_dialog.set_title("this is the title")
        about_dialog.set_comments("This is surely an unfinished job")

        logo = GdkPixbuf.Pixbuf.new_from_file("logo.png")
        about_dialog.set_logo(logo)

        about_dialog.run()
        about_dialog.destroy()

    def delete_labels_img(self, list):
        for key in list:
            for file_name in os.listdir(os.path.join(self.p.path_final, key[0])):
                os.remove(os.path.join(self.p.path_final, key[0], file_name))

    def clear_it(self, *args):
        if len(args) > 0:
            self.p.initial_xml()
            print("initialisation from clear it")
            # bug / may be here
            self.delete_labels_img(self.p.keys[2:])
        else:
            print("no need for initialisation")

        # clear changedValues
        del self.p.changed_values
        self.p.changed_values = {}

        # clear xml file
        self.p.doc = minidom.parse(self.p.path_xml)
        collection = self.p.doc.documentElement
        self.p.tag_piece = collection.getElementsByTagName("image")[0].getElementsByTagName("piece")

        # self.delete_labels_img(self.p.keys[2:])
        self.deal_with_xml()

        # make it none
        self.noneButton.set_active(True)

    def test_clear(self, menu_item, idk):
        name = menu_item.get_name().split("_")[1]
        label_id = self.get_index_label(name) + 1

        del self.p.changed_values
        self.p.changed_values = {}

        for i in range(len(self.p.tag_piece)):
            if int(self.p.tag_piece[i].childNodes[0].data) == label_id:
                self.p.changed_values[i] = 0

        self.deal_with_xml()
        self.delete_labels_img([self.p.keys[label_id + 1]])

    def remove_label(self, label_id):
        print("removing label", label_id)
        print(self.p.keys, label_id)
        rmtree(os.path.join(self.p.path_final, self.p.keys[label_id + 1][0]))

        del self.p.changed_values
        self.p.changed_values = {}

        for i in range(len(self.p.tag_piece)):
            if int(self.p.tag_piece[i].childNodes[0].data) == label_id:
                self.p.changed_values[i] = 0
            elif int(self.p.tag_piece[i].childNodes[0].data) > label_id:
                self.p.changed_values[i] = int(self.p.tag_piece[i].childNodes[0].data) - 1

        self.radio_buttons[label_id - 1].hide_on_delete()
        del (self.radio_buttons[label_id - 1])

        del (self.p.keys[label_id + 1])
        self.p.tag_key[0].parentNode.removeChild(self.p.tag_key[label_id + 1])
        self.p.tag_key.remove(self.p.tag_key[label_id + 1])
        if self.p.current_value == label_id: self.p.current_value = 0

        # delete key_logo :
        try:
            os.remove(os.path.join("keys", "key_" + str(label_id + 1) + ".png"))
        except:
            pass

        self.deal_with_xml()

    def open_image(self, *args):
        dlg = Gtk.FileChooserDialog("Open Image", self, Gtk.FileChooserAction.OPEN,
                                    (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OPEN, Gtk.ResponseType.OK))
        # response = dlg.run()
        dlg.run()
        path = dlg.get_filename()
        if path:
            self.p.originalName = path
            dlg.destroy()
            self.create_img_directory()
            self.clear_it()
            self.p.changed_values = {}  # buug
            self.p.keys[1][2] = 0

            self.change_position()
        else:
            dlg.destroy()
        return path

    def export_ground_truth(self, *args):
        img = self.p.img_cropped.copy()
        draw = ImageDraw.Draw(img)
        for i in range(self.p.LINES):
            for j in range(self.p.COLUMNS):
                x1 = j * self.p.PIECE_WIDTH
                y1 = i * self.p.PIECE_WIDTH
                x2 = x1 + self.p.PIECE_WIDTH
                y2 = y1 + self.p.PIECE_WIDTH
                try:
                    r = int(self.p.tag_piece[self.p.COLUMNS * i + j].childNodes[0].data)
                    if r:
                        draw.rectangle([x1, y1, x2, y2], fill=self.p.keys[r + 1][1])
                except:
                    print("baddd exception!! (out of the dialog class)")

        fp_path = os.path.join(self.p.path_final, "ground_truth",
                               self.p.path_img_name + "_" + self.p.hashcode + "_GT.jpg")
        img.save(fp_path, 'JPEG', quality=100)
        Image.open(fp_path).show()

    def press_key_event(self, widget, event):
        list_labels = ["N", "S", "M", "D"]
        if event.keyval == Gdk.KEY_Up:
            self.move_up()
        elif event.keyval == Gdk.KEY_Right:
            self.move_right()
        elif event.keyval == Gdk.KEY_Down:
            self.move_down()
        elif event.keyval == Gdk.KEY_Left:
            self.move_left()

        elif event.keyval == Gdk.KEY_Page_Down:
            if self.p.keys[1][2] < (self.p.LINES * self.p.COLUMNS - 1):
                self.p.keys[1][2] += 1
                self.change_position()
            else:
                self.no_more("pieces")

        elif event.keyval == Gdk.KEY_Page_Up:
            if self.p.keys[1][2] > 0:
                self.p.keys[1][2] -= 1
                self.change_position()
            else:
                self.no_more("pieces")

        elif event.keyval == Gdk.KEY_Control_R:
            self.deal_with_xml()

        elif event.string == "o":
            self.open_original("original")
        elif event.string == "O":
            self.open_original((self.p.keys[self.p.current_value + 1][0]))

        elif event.string.upper() in list_labels:
            if event.string.upper() == list_labels[0]:
                self.noneButton.set_active(True)
                self.p.changed_values[self.p.keys[1][2]] = "0"
            else:
                n = list_labels.index(event.string.upper())
                if event.string.islower():
                    self.radio_buttons[n - 1].set_active(True)
                    self.p.changed_values[self.p.keys[1][2]] = str(n)
                else:
                    self.open_original((self.p.keys[n + 1][0]))


class DialogExample(Gtk.Dialog):
    def __init__(self, parent, hide, position, p):
        # change_it: scale value will change the dimensions of dialog window
        concerned_label = p.keys[hide + 1][0]
        if hide == 0:  concerned_label = p.keys[0][0]
        Gtk.Dialog.__init__(self, "View " + concerned_label, parent, 0, (Gtk.STOCK_OK, Gtk.ResponseType.OK))
        self.position = position
        self.p = p

        box = self.get_content_area()
        box.set_spacing(30)

        ##original image

        img = self.p.img_cropped.copy()
        draw = ImageDraw.Draw(img)
        p_w = self.p.PIECE_WIDTH

        # draw diffrent colors
        if hide: hide += 1
        for i in range(self.p.LINES):
            for j in range(self.p.COLUMNS):
                r = int(self.p.tag_piece[self.p.COLUMNS * i + j].childNodes[0].data)
                if r != 0: r += 1
                fill, outline = p.keys[r][1], self.p.black
                if hide == r:
                    fill = None
                elif r == 0:
                    outline = None
                if fill:
                    if fill.upper() == "GREEN":
                        fill = "#4caf50"
                    elif fill.upper() == "YELLOW":
                        fill = "#ffeb3b"
                    elif fill.upper() == "RED":
                        fill = "#f44336"
                draw.rectangle([j * p_w, i * p_w, p_w * (j + 1) - 1, p_w * (i + 1) - 1], fill=fill, outline=outline)

        # draw current
        l, c = self.position
        x1, y1, x2, y2 = l * p_w + self.p.pp / 2, c * p_w, p_w * (l + 1) - self.p.pp / 2, p_w * (c + 1)

        draw.line([x1, y1, x2, y1], p.keys[1][1], self.p.pp)
        draw.line([x2, y1, x2, y2], p.keys[1][1], self.p.pp)
        draw.line([x2, y2, x1, y2], p.keys[1][1], self.p.pp)
        draw.line([x1, y2, x1, y1], p.keys[1][1], self.p.pp)

        # saving
        del (draw)
        img = img.resize((int(self.p.w * self.p.scale_value), int(self.p.h * self.p.scale_value)), Image.ANTIALIAS)
        path_2 = os.path.join("tmp", "open_image.jpg")
        img.save(path_2, 'JPEG', quality=100)

        original_image = Gtk.Image.new_from_file(path_2)

        ##keys
        try:
            os.makedirs("keys")
        except OSError:
            """nothing to do"""
        hbox = Gtk.Box(spacing=20)
        for i in range(2, len(p.keys)):
            fill = p.keys[i][1]
            if hide == i: fill = p.keys[0][1]

            if fill.upper() == "GREEN":
                fill = "#4caf50"
            elif fill.upper() == "YELLOW":
                fill = "#ffeb3b"
            elif fill.upper() == "RED":
                fill = "#f44336"

            im = Image.new("RGB", (20, 20), fill)
            ImageDraw.Draw(im).rectangle([0, 0, 19, 19], outline="#212121")
            ImageDraw.Draw(im).rectangle([1, 1, 18, 18], outline="#212121")

            im.save(os.path.join("keys", "key_" + str(i) + ".png"))
            hbox.pack_start(Gtk.Image.new_from_file(os.path.join("keys", "key_" + str(i) + ".png")), False, False, 0)
            hbox.pack_start(Gtk.Label(p.keys[i][0]), False, False, 0)

        im = Image.new("RGBA", (20, 20), (0, 0, 0, 0))
        im_draw = ImageDraw.Draw(im)
        w, h = im.size
        im_draw.rectangle([0, 0, w - 1, h - 1], outline=p.keys[1][1])
        im_draw.rectangle([1, 1, w - 2, h - 2], outline=p.keys[1][1])
        del (im_draw)
        im.save(os.path.join("keys", "key_3.png"))
        hbox.pack_end(Gtk.Label("current"), False, False, 0)
        hbox.pack_end(Gtk.Image.new_from_file(os.path.join("keys", "key_3.png")), False, False, 0)

        original_image_e = Gtk.EventBox()
        original_image_e.connect("button_press_event", self.motion_notify)
        original_image_e.add(original_image)
        box.add(original_image_e)
        box.add(hbox)

        self.show_all()
        self.set_resizable(False)

    def motion_notify(self, widget, event):
        x, y = (int(event.x / (self.p.PIECE_WIDTH * self.p.scale_value)),
                int(event.y / (self.p.PIECE_WIDTH * self.p.scale_value)))
        self.position = (x, y)
        if (x < self.p.COLUMNS) & (y < self.p.LINES):
            print("mouse position : ", self.position, self.getCurrent())
            self.destroy()

    def getCurrent(self):
        x, y = self.position
        return (x + y * self.p.COLUMNS)

    def press_key_event(self, widget, event):
        if event.string in ("o", "O"):
            self.destroy()


class MyWindow(Gtk.Dialog):
    def __init__(self, parent, original_name, path, p, keys):
        # Gtk.Window.__init__(self, title="Simple Notebook Example")
        Gtk.Dialog.__init__(self, "All Parameters", parent, 0)
        # self.connect("realize", self.entry_icon_event)
        self.set_border_width(10)
        self.set_default_size(100, 700)

        self.p = p

        self.parent = parent
        self.p.keys = keys

        self.treeview = None

        self.notebook = Gtk.Notebook()

        # page_1
        self.page1 = Gtk.VBox()
        self.page1.set_border_width(10)
        self.notebook.append_page(self.page1, Gtk.Label('Original Image'))
        self.original_name = os.path.abspath(original_name)
        self.path = path

        self.image_item = Gtk.Image()
        self.page1.pack_end(self.image_item, False, False, 0)

        self.image_path = Gtk.Entry()
        self.image_path.set_icon_from_icon_name(Gtk.EntryIconPosition.SECONDARY, "document-open")
        self.image_path.set_text(self.original_name)
        # self.image_path.set_icon_activatable(True)
        self.image_path.connect("icon_press", self.entry_icon_event)
        self.image_path.connect("activate", self.new_image_path)
        self.page1.pack_start(self.image_path, False, False, 0)

        # page_2
        self.page2 = Gtk.VBox(spacing=16)
        self.page2.set_border_width(10)
        self.notebook.append_page(self.page2, Gtk.Label('PIECE_WIDTH'))
        self.scale_button = Gtk.Scale()
        self.scale_button.set_increments(2, 10)
        self.scale_button.set_digits(0)

        self.scale_button.connect('button_release_event', self.on_changed)
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

        self.scale_button_2.connect('button_release_event', self.on_changed_2)
        self.page3.pack_start(self.scale_button_2, False, False, 0)
        self.S_V_preview = Gtk.Image()
        self.page3.pack_end(self.S_V_preview, False, False, 0)

        # page_4
        self.page4 = Gtk.VBox(spacing=16)
        self.page4.set_border_width(10)
        self.notebook.append_page(self.page4, Gtk.Label('Labels'))
        self.treeview = CellRendererToggleWindow(parent, self.p)
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

    def on_changed(self, widget, *args):
        if len(args) == 0:
            self.on_changed_part_2()
        elif self.p.PIECE_WIDTH != int(widget.get_value()):
            for i in range(2, len(self.p.keys)):
                del (self.p.keys[i][2])
                self.p.keys[i].append([])
            response = Gtk.ResponseType.OK
            if len(args):
                response = self.show_warning()
                if response == Gtk.ResponseType.OK:
                    self.p.PIECE_WIDTH = int(widget.get_value())
                    self.p.new_PIECE_WIDTH()

                    self.parent.delete_labels_img(self.p.keys[2:])
                    rmtree(self.p.path_crop)
                    os.mkdir(self.p.path_crop)
                    self.parent.crop()
                    self.p.initial_xml()

                    self.p.new_PIECE_WIDTH()
                    self.parent.change_position()
                    self.on_changed_part_2()
                elif response == Gtk.ResponseType.CANCEL:
                    widget.set_value(self.p.PIECE_WIDTH)
            elif response == Gtk.ResponseType.OK:
                self.on_changed_part_2()

    def on_changed_part_2(self):
        self.parent.change_position_image(self.p.COLUMNS / 2, self.p.LINES / 2)
        self.P_W_preview.set_from_file(os.path.join("tmp", "img_current.jpg"))

        if self.treeview:  self.treeview.new_piece_width()

        w, h = self.p.img_cropped.size
        self.img_s_1 = self.p.img_cropped.resize((int(w * self.p.scale_min), int(h * self.p.scale_min)),
                                                 Image.ANTIALIAS)
        self.img_s_1.save(os.path.join("tmp", "original_preview.jpg"), 'JPEG', quality=100)
        self.image_item.set_from_file(os.path.join("tmp", "original_preview.jpg"))

    def on_changed_2(self, widget, *args):
        # print(widget.get_value())
        if widget.get_value():
            self.p.scale_value = widget.get_value()
        w, h = self.p.img_original.size

        im = self.p.img_cropped.resize((int(w * self.p.scale_value), int(h * self.p.scale_value)), Image.ANTIALIAS)
        im = im.crop((0, 0, self.img_s_1.size[0], self.img_s_1.size[1]))
        im.save(os.path.join("tmp", "scale_preview.jpg"), 'JPEG', quality=100)
        self.S_V_preview.set_from_file(os.path.join("tmp", "scale_preview.jpg"))

        parameters_xml = self.p.doc.documentElement.getElementsByTagName("parameters")[0]
        parameters_xml.getElementsByTagName("SView")[0].childNodes[0].data = str(self.p.scale_value)

    def open_image(self, *args):
        path_1 = self.parent.open_image()
        if path_1:
            self.path = self.parent.path + ".jpg"
            del self.p.keys
            self.p.keys = self.parent.append_index_keys()
            self.new_image_path(path_1)

    def new_image_path(self, *args):
        if type(args[0]) is str:
            text = args[0]
        else:
            text = args[0].get_text()
        print(text)
        self.original_name = text

        self.image_path.set_text(text)
        self.change_image()

    def change_image(self):
        # page_1
        self.p.new_image()
        self.change_image_begin()

    def change_image_begin(self):
        w, h = self.p.img_original.size
        # self.p.scale_min = 1
        self.treeview.set_initial_scale_value(self.p.scale_min)  # from page_4
        self.img_s_1 = self.p.img_cropped.resize((int(w * self.p.scale_min), int(h * self.p.scale_min)),
                                                 Image.ANTIALIAS)
        self.img_s_1.save(os.path.join("tmp", "original_preview.jpg"), 'JPEG', quality=100)
        self.image_item.set_from_file(os.path.join("tmp", "original_preview.jpg"))

        # page_2
        self.scale_button.set_range(20, min(self.p.img_original.size) / 3)
        self.scale_button.set_value(self.p.PIECE_WIDTH)
        self.on_changed(self.scale_button)

        # page_3
        self.scale_button_2.set_range(self.p.scale_min, self.p.scale_max)
        self.scale_button_2.set_value(self.p.scale_value)
        self.on_changed_2(widget=self.scale_button_2)

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
    def __init__(self, parent, p):
        # Gtk.Window.__init__(self, title="CellRendererToggle Example")

        self.p = p

        self.parent = parent

        self.liststore = Gtk.ListStore(str, str, str, str, str)
        kk = self.p.keys[1:]
        for k in kk:
            self.liststore.append([k[0], k[1], "go-up", "go-down", "edit-delete"])

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
        renderer_combo.connect("edited", self.on_combo_changed)

        column_combo = Gtk.TreeViewColumn("Color", renderer_combo, text=1)
        column_combo.set_min_width(col_min_width)
        treeview.append_column(column_combo)
        # treeview.override_background_color(Gtk.StateFlags.PRELIGHT, Gdk.RGBA(255,0,0,255))


        # pixbuf
        renderer_pixbuf_1 = CellRendererClickablePixbuf()
        renderer_pixbuf_1.connect("clicked", self.pixbuf_move_up_down, (-1))
        column_pixbuf_1 = Gtk.TreeViewColumn("Move Up", renderer_pixbuf_1, icon_name=2)
        column_pixbuf_1.set_min_width(col_min_width)
        treeview.append_column(column_pixbuf_1)

        renderer_pixbuf_2 = CellRendererClickablePixbuf()
        renderer_pixbuf_2.connect("clicked", self.pixbuf_move_up_down, (1))
        column_pixbuf_2 = Gtk.TreeViewColumn("Move Down", renderer_pixbuf_2, icon_name=3)
        column_pixbuf_2.set_min_width(col_min_width)
        treeview.append_column(column_pixbuf_2)

        renderer_pixbuf_3 = CellRendererClickablePixbuf()
        renderer_pixbuf_3.connect("clicked", self.pixbuf_delete)
        column_pixbuf_3 = Gtk.TreeViewColumn("Delete", renderer_pixbuf_3, icon_name=4)
        column_pixbuf_3.set_min_width(col_min_width)
        treeview.append_column(column_pixbuf_3)
        treeview.columns_autosize()

        self.box = Gtk.VBox(spacing=0)
        self.box.pack_start(treeview, False, False, 0)

        hbox = Gtk.Box()
        button_add = Gtk.Button()
        image = Gtk.Image()
        image.set_from_stock(Gtk.STOCK_ADD, Gtk.IconSize.BUTTON)
        button_add.set_image(image)
        button_add.connect("clicked", self.add_line)
        hbox.pack_start(button_add, False, False, 30)

        self.box.pack_start(hbox, False, False, 15)

        # drawing pieces

        self.labels_preview = Gtk.Image.new_from_file(os.path.join("tmp", "labels_preview.jpg"))

        self.box.pack_end(self.labels_preview, False, False, 0)

        self.adding = 4

    def text_edited(self, widget, path, text):
        path = int(path)
        print("txt")
        if path:
            v = True
            for k in self.p.keys:
                if text == k[0]: v = False; break;
            if v:
                self.p.tag_key[path + 1].childNodes[0].data = text
                os.rename(os.path.join(self.p.path_final, self.p.keys[path + 1][0]),
                          os.path.join(self.p.path_final, text))
                ##! I failed changing menu labels :'(
                ##
                self.parent.radio_buttons[path - 1].set_label(text)
                ##
                self.liststore[path][0] = text
                self.p.keys[path + 1][0] = text
                print("text edited successfully")
            else:
                print("~> this label does already exist")

    def on_combo_changed(self, widget, path, text):
        print((path, len(self.p.tag_key)))
        self.liststore[path][1] = text
        path = int(path) + 1
        self.p.keys[path][1] = text
        self.draw_image()
        self.labels_preview.set_from_file(os.path.join("tmp", "labels_preview.jpg"))
        self.p.tag_key[path].setAttribute("color", text)

    def add_line(self, *args):
        if len(self.liststore) < 7:
            self.adding += 1
            new_label = "bla_" + str(self.adding)
            new_color = "White"
            self.p.keys.append([new_label, new_color, []])
            self.liststore.append([self.p.keys[-1][0], self.p.keys[-1][1], "go-up", "go-down", "edit-delete"])

            try:
                os.mkdir(os.path.join(self.p.path_final, new_label))
            except:
                """nothing to do here"""

            self.parent.radio_buttons.append(
                Gtk.RadioButton.new_with_label_from_widget(self.parent.noneButton, self.p.keys[-1][0]))
            self.parent.radio_buttons[-1].connect("toggled", self.parent.on_button_toggled)
            self.parent.button4.pack_start(self.parent.radio_buttons[-1], False, False, 0)

            another_key = self.p.doc.createElement("key")
            another_key_label = self.p.doc.createTextNode(new_label)
            another_key.appendChild(another_key_label)
            another_key.setAttribute("color", new_color)
            self.p.tag_key[0].parentNode.appendChild(another_key)
            self.p.tag_key.append(another_key)

    def pixbuf_delete(self, widget, path):
        path = int(path)
        if path:
            self.liststore.remove(self.liststore.get_iter(path))
            print("Line ", path, " has been removed")
            self.parent.remove_label(path)
            self.draw_image()
            self.labels_preview.set_from_file(os.path.join("tmp", "labels_preview.jpg"))
        else:
            print("~> can't delete the first line !")

    def pixbuf_move_up_down(self, widget, path, *args):
        add = args[0]
        path = int(path)
        print("path is : ", path)
        print(path - int((add - 1) / 2))

        if path + int((add - 1) / 2) > 0:
            if ((add != 1) | (path + 1 < len(self.liststore))):
                for i in range(2):
                    self.liststore[path + add][i], self.liststore[path][i] = \
                        self.liststore[path][i], self.liststore[path + add][i]

                self.p.tag_key[path + add + 1].childNodes[0].data, \
                self.p.tag_key[path + 1].childNodes[0].data = \
                    self.p.tag_key[path + 1].childNodes[0].data, \
                    self.p.tag_key[path + add + 1].childNodes[0].data

                color_1 = self.p.tag_key[path + add].getAttribute("color")
                color_2 = self.p.tag_key[path + add + 1].getAttribute("color")
                self.p.tag_key[path + add + 1].setAttribute("color", color_1)
                self.p.tag_key[path + add].setAttribute("color", color_2)

                for piece in self.p.tag_piece:
                    value = int(piece.childNodes[0].data)
                    if value == path:
                        piece.childNodes[0].data = str(value + add)
                    elif value == path + add:
                        piece.childNodes[0].data = str(value - add)

                self.p.keys[path + 1], self.p.keys[path + add + 1] = \
                    self.p.keys[path + add + 1], self.p.keys[path + 1]

                self.parent.radio_buttons[path - 1].set_label(self.p.keys[path + 1][0])
                self.parent.radio_buttons[path + add - 1].set_label(self.p.keys[path + add + 1][0])

                if self.p.current_value == path:  # current_value
                    self.p.current_value = path + add
                elif self.p.current_value == path + add:
                    self.p.current_value = path
                if self.p.current_value:
                    self.parent.radio_buttons[self.p.current_value - 1].set_active(True)
                print("Line ", path, " has been moved down")
            else:
                print("~> first can't !")
        else:
            print("~> can't move the first line!")

    def draw_image(self):
        img = Image.open(self.p.path_results + ".jpg")
        w, h = img.size

        draw = ImageDraw.Draw(img)

        for i in range(0, w, self.p.PIECE_WIDTH):
            draw.line([i, 0, i, h], self.p.black, 1)
        for i in range(0, h, self.p.PIECE_WIDTH):
            draw.line([0, i, w, i], self.p.black, 1)

        for path in range(2, len(self.p.keys)):
            for i in self.p.keys[path][2]:
                x1, y1 = self.p.get_position(i)
                x1, y1 = x1 * self.p.PIECE_WIDTH, y1 * self.p.PIECE_WIDTH
                draw.rectangle([x1, y1, x1 + self.p.PIECE_WIDTH, y1 + self.p.PIECE_WIDTH], fill=self.p.keys[path][1],
                               outline=self.p.black)

        x1, y1 = int((self.p.COLUMNS - 1) / 2) * self.p.PIECE_WIDTH, int((self.p.LINES - 1) / 2) * self.p.PIECE_WIDTH
        x2, y2 = x1 + self.p.PIECE_WIDTH, y1 + self.p.PIECE_WIDTH
        draw.line([x1, y1, x2, y1], self.p.keys[1][1], 5)
        draw.line([x2, y1, x2, y2], self.p.keys[1][1], 5)
        draw.line([x2, y2, x1, y2], self.p.keys[1][1], 5)
        draw.line([x1, y2, x1, y1], self.p.keys[1][1], 5)

        img = img.resize((int(w * self.p.scale_min), int(h * self.p.scale_min)), Image.ANTIALIAS)
        img.save(os.path.join("tmp", "labels_preview.jpg"), "JPEG", quality=100)

    def new_piece_width(self):
        self.PIECE_WIDTH = int(self.p.PIECE_WIDTH * self.initial_scale_value)
        self.draw_image()
        self.labels_preview.set_from_file(os.path.join("tmp", "labels_preview.jpg"))

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


class MyApplication(Gtk.Application):
    def __init__(self):
        Gtk.Application.__init__(self)

        # parameters
        self.originalName = "original.jpg"
        self.PIECE_WIDTH = 42

        self.w = self.h = self.img_cropped = self.LINES = self.COLUMNS = self.str_len = 0

        self.hashcode = self.path_img_name = self.path_results = self.path_xml \
            = self.path_crop = self.scale_min = self.scale_max = self.scale_value = self.img_original = self.black \
            = self.doc = self.tag_key = None

        self.keys = [["None", "#e8e8e7"], ["Current", "#2196f3", 0], ["Sparse", "green", []],
                     ["Medium", "yellow", []], ["Dense", "red", []]]
        self.changed_values = {}
        self.P_W_viewed = 150
        self.safe_space_x = 60.0
        self.safe_space_y = 190.0

        self.tag_piece = 0
        self.i_adj = Gtk.Adjustment(0, 0, 0, 1, 5.0, 0.0)
        self.x_adj = Gtk.Adjustment(0, 0, 0, 1, 5.0, 0.0)
        self.y_adj = Gtk.Adjustment(0, 0, 0, 1, 5.0, 0.0)

        self.path_final = os.path.join("results", "final_results")

        self.pp = 4  # width of lines displayed

    def do_activate(self):
        win = GridWindow(self)
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

    def img_hashcode(self):
        m = hashlib.md5()
        with io.BytesIO() as memf:
            data = memf.getvalue()
            m.update(data)
        return m.hexdigest()[:5]

    def new_image(self):
        print("------------------------->")

        try:
            self.img_original = Image.open(self.originalName)
        except IOError:
            self.img_original = Image.new("RGB", (800, 800), "Black")

        self.hashcode = self.img_hashcode()

        self.path_img_name = os.path.basename(self.originalName).split(".")[0]
        self.path_results = os.path.join("results", self.path_img_name, self.hashcode)
        self.path_xml = os.path.join(self.path_results, "xml", self.hashcode + ".xml")
        self.path_crop = os.path.join(self.path_results, "pieces")

        win = Gtk.Window()
        w, h = self.img_original.size
        self.scale_min = int(min(900.0 / w, 500.0 / h) * 10 + 1) / 10.0
        self.scale_max = min((win.get_screen().get_width() - self.safe_space_x) / w,
                             (win.get_screen().get_height() - self.safe_space_y) / h)
        self.scale_value = (self.scale_min + self.scale_max) / 2
        print("scale value in init", self.scale_value)

        self.new_PIECE_WIDTH()

        self.black = max(self.img_original.getcolors(self.img_original.size[0] * self.img_original.size[1]))[1]
        self.black = (255 - self.black[0], 255 - self.black[1], 255 - self.black[2])

    def new_PIECE_WIDTH(self):
        w, h = self.img_original.size

        self.w = w - w % self.PIECE_WIDTH
        self.h = h - h % self.PIECE_WIDTH
        self.img_cropped = self.img_original.crop((0, 0, self.w, self.h))
        self.LINES = int(self.h / self.PIECE_WIDTH)
        self.COLUMNS = int(self.w / self.PIECE_WIDTH)
        self.str_len = len(str(self.LINES * self.COLUMNS))

        self.i_adj.set_upper(self.COLUMNS * self.LINES - 1)
        self.x_adj.set_upper(self.COLUMNS - 1)
        self.y_adj.set_upper(self.LINES - 1)

    def initial_xml(self):
        self.doc = minidom.Document()

        tag_root = self.doc.createElement("root")
        self.doc.appendChild(tag_root)

        tag_image = self.doc.createElement("image")
        tag_root.appendChild(tag_image)
        tag_image.setAttribute("name", self.path_img_name)
        tag_image.setAttribute("p_w", str(self.PIECE_WIDTH))

        for i in range(self.LINES * self.COLUMNS):
            tag_piece = self.doc.createElement("piece")
            tag_image.appendChild(tag_piece)
            tag_piece.setAttribute("id", str(i).rjust(self.str_len, "0"))
            tag_piece.appendChild(self.doc.createTextNode("0"))

        self.tag_piece = tag_image.getElementsByTagName("piece")

        tag_parameters = self.doc.createElement("parameters")
        tag_root.appendChild(tag_parameters)

        tag_keys = self.doc.createElement("keys")
        tag_parameters.appendChild(tag_keys)
        for key in self.keys:
            tag_key = self.doc.createElement("key")
            tag_keys.appendChild(tag_key)
            if key == self.keys[1]: tag_key.setAttribute("current", str(self.keys[1][2]))
            tag_key.setAttribute("color", key[1])
            tag_key.appendChild(self.doc.createTextNode(key[0]))

        self.tag_key = tag_keys.getElementsByTagName("key")

        tag_pw = self.doc.createElement("PWidth")
        tag_parameters.appendChild(tag_pw)
        tag_pw.appendChild(self.doc.createTextNode(str(self.PIECE_WIDTH)))
        tag_parameters.appendChild(tag_pw)

        tag_sv = self.doc.createElement("SView")
        tag_parameters.appendChild(tag_sv)
        tag_sv.appendChild(self.doc.createTextNode(str(self.scale_value)))
        tag_parameters.appendChild(tag_sv)

        file = open(self.path_xml, "w+")
        file.write(self.doc.toprettyxml(indent='\t'))

    # initial
    def initial_it(self):
        self.doc = minidom.parse(self.path_xml)
        tag_root = self.doc.documentElement

        self.tag_piece = tag_root.getElementsByTagName("image")[0].getElementsByTagName("piece")
        PIECE_WIDTH = tag_root.getElementsByTagName("parameters")[0].getElementsByTagName("PWidth")[0].childNodes[
            0].data
        scale_view = tag_root.getElementsByTagName("parameters")[0].getElementsByTagName("SView")[0].childNodes[0].data
        self.tag_key = tag_root.getElementsByTagName("parameters")[0].getElementsByTagName("keys")[
            0].getElementsByTagName("key")

        del self.keys
        self.keys = []
        for key in self.tag_key:
            self.keys.append([str(key.childNodes[0].data), str(key.getAttribute("color"))])

        self.keys[1].append(int(self.tag_key[1].getAttribute("current")))

        for i in range(2, len(self.keys)): self.keys[i].append([])

        if self.PIECE_WIDTH != int(PIECE_WIDTH):
            self.PIECE_WIDTH = int(PIECE_WIDTH)
            self.new_PIECE_WIDTH()

        self.scale_value = float(scale_view)

    def get_position(self, i):
        return i % self.COLUMNS, i / self.COLUMNS

    def get_piece_path(self, i):
        return self.path_img_name + "_" + self.hashcode + "_" + str(i).rjust(self.str_len, '0') + '.jpg'


app = MyApplication()
app.run()
app.quit()
