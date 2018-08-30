from __future__ import print_function

import gi


from image_preview import ImagePreview
from window_parameters import WindowParameters

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, Gio, GObject, GdkPixbuf
from PIL import Image, ImageDraw



from image_manipulate import imageManipulate
from config import config
from paths import paths
from JSON_mod import JSON_mod


##################################################
# syntax changes:
#################
#
# self.p => config
# deal_with_xml() => JSON_mod.save_data()
# open_original() => show_preview()
# self.crop() => imageManipulate.crop_pieces()
# change_position_image => imageManipulate.refresh_preview_part()
# change_value => menu_popup_clicked
# DialogExample => ImagePreview
# path_2 => config.path_tmp_openImage
# MyWindow => window_parameters.WindowParameters
#
#### WindowParameters
# on_changed_2 => on_change_scale
# on_chnaged => on_change_pw
#
###################################################


###################### TODOs: #####################
########## config
# (3) fix paths :use dictionary *
# (4) fix keys : use dictionary (no)
# (3.01) pieces position *
# (3.001) fix new img params
#
########## windows
# (5) use glade
#
########## xml_mod
# (1) save to xml (if easy to do that) or use json *
# (1.1) save configs to json *
# (2) recapture saved data *
#
########## main_window
# (?) add clear keys *
# (3.1) open new image *
#
########## window parameters
# (6) fix labeling parameters
# (6.1) fix new p_w error
#
########## executable
# - lightweight executable file
#
########## additional features
# - add new project / export project / import project
# - add choose type of project: may pictures / cropped pieces
# - add ML steps and select between them
# - add chart of results at the end
#
###################################################

class MainWindow(Gtk.ApplicationWindow):
    def __init__(self, app):
        Gtk.Window.__init__(self, title="CropML", application=app)
        self.menu_popup_items = []
        self.set_default_icon_from_file("logo.png")

        self.parent = app


        Gtk.Window.__init__(self, title="Project")

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

        layout = Gtk.VBox()

        # main box
        main_box = Gtk.Box(spacing=20)
        # menu
        btn_save = Gtk.Button(label="save")
        btn_save.connect("clicked", JSON_mod.save_data)

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
        i_spin.set_adjustment(config.i_adj)
        i_spin.set_wrap(True)

        # event i_adj
        config.i_adj.connect("value_changed", self.change_position_i)

        hbox1_postion.pack_start(i_label, False, False, 0)
        hbox1_postion.pack_start(i_spin, False, False, 0)
        # this is x
        x_label = Gtk.Label("x :")
        x_spin = Gtk.SpinButton()
        x_spin.set_adjustment(config.x_adj)
        x_spin.set_wrap(True)
        # this is y
        y_label = Gtk.Label("y :")
        y_spin = Gtk.SpinButton()
        y_spin.set_adjustment(config.y_adj)
        y_spin.set_wrap(True)

        # event x_adj & y_adj
        config.x_adj.connect("value_changed", self.change_position_x)
        config.y_adj.connect("value_changed", self.change_position_y)

        hbox_postion.pack_start(x_label, False, False, 0)
        hbox_postion.pack_start(x_spin, False, False, 0)
        hbox_postion.pack_start(y_label, False, False, 0)
        hbox_postion.pack_start(y_spin, False, False, 0)

        self.button3 = hbox_postion

        hbox = Gtk.Box(spacing=4)
        # radio buttons
        self.radio_buttons = []

        self.noneButton = Gtk.RadioButton.new_with_label_from_widget(None, "None")
        self.noneButton.connect("toggled", self.on_radio_btn_toggled)
        hbox.pack_start(self.noneButton, False, False, 0)

        for key in config.keys[2:]:
            self.radio_buttons.append(Gtk.RadioButton.new_with_label_from_widget(self.noneButton, key[0]))
            self.radio_buttons[-1].connect("toggled", self.on_radio_btn_toggled)
            hbox.pack_start(self.radio_buttons[-1], False, False, 0)

        self.button4 = hbox

        right_widget.pack_start(hbox1_postion, False, False, 0)

        hbox1_postion.set_halign(3)
        right_widget.pack_start(self.button3, False, False, 0)
        right_widget.pack_start(self.button4, False, False, 0)
        right_widget.pack_end(btn_save, False, False, 0)

        # left widget

        self.center_image_e = Gtk.EventBox()
        self.center_image_e.set_tooltip_text("hello")

        self.myImage = Gtk.Image.new_from_file(paths.tmp_current)
        self.button_center = self.myImage

        self.center_image_e.add(self.button_center)

        # packing..........

        main_box.pack_start(self.center_image_e, False, False, 0)
        main_box.pack_end(right_widget, False, False, 0)
        layout.pack_end(main_box, False, False, 0)
        self.add(layout)

        # self.center_image_e.connect("button_press_event", self.show_preview, ("original"))
        # self.center_image_e.connect("button_press_event", self.press_current_img)
        self.center_image_e.connect_object("button_press_event", self.press_current_img, self.menu_popup)
        self.center_image_e.connect("motion-notify-event", self.set_tooltip_text)

        # now I can change position


        self.change_position()



    def first_initiate(self):
        self.parent.first_initiate()

        self.change_position()


    ######################### make menu #############################

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
        for key in config.keys[2:]:
            submenu2.append(key[0], "win.view_" + key[0])
            # the action related to the window (view label)
            self.view_label_action.append(Gio.SimpleAction.new("view_" + key[0], None))
            self.view_label_action[-1].connect("activate", self.show_preview, (key[0]))
            self.add_action(self.view_label_action[-1])
        submenu.append_section("specific", submenu2)
        menu_model.append_submenu("View", submenu)

        # the action related to the window (view_original)
        view_original_action = Gio.SimpleAction.new("view_original", None)
        view_original_action.connect("activate", self.show_preview)
        self.add_action(view_original_action)

        # a submenu with one action for the menu
        submenu = Gio.Menu()
        submenu.append("All", "win.clear_all")
        submenu2 = Gio.Menu()
        for key in config.keys[2:]:
            submenu2.append(key[0], "win.clear_" + key[0])
            # the action related to the window (clear label)
            self.test_clear_action.append(Gio.SimpleAction.new("clear_" + key[0], None))
            self.test_clear_action[-1].connect("activate", self.clear_key)
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
        clear_all_action.connect("activate", self.clear_all)
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
        menu_about = Gtk.Button()
        menu_about.add(Gtk.Image.new_from_icon_name("help-about-symbolic", Gtk.IconSize.MENU))
        menu_about.connect("clicked", self.open_about)

        self.header.pack_end(menu_about)

    def make_menu_popup(self):
        menu_item_none = Gtk.MenuItem(config.keys[1][0])
        menu_item_none.connect("activate", self.menu_popup_clicked, 0)
        self.menu_popup.append(menu_item_none)
        self.menu_popup.append(Gtk.SeparatorMenuItem())
        # remove wayland ugly warnings
        self.menu_popup.attach_to_widget(self)
        value = 1
        for key in config.keys[2:]:
            menu_item = Gtk.MenuItem(key[0])
            menu_item.connect("activate", self.menu_popup_clicked, value)
            self.menu_popup_items.append(menu_item)
            value += 1

        for menu_item in self.menu_popup_items:
            self.menu_popup.append(menu_item)
        self.menu_popup.show_all()

    # menu popup
    def menu_popup_clicked(self, *args):
        print(args[1])
        config.current_position = self.clicked_area
        #if args[1] == 0:
        if args[1]: self.radio_buttons[args[1] - 1].set_active(True)
        else : self.noneButton.set_active(True)
        self.set_radio_btn_active(args[1])
        self.change_position()

        # TODO: self.xml_save_changes() = 0

    # menu_file methods
    def export_ground_truth(self,*args):
        img = config.img_cropped.copy()
        draw = ImageDraw.Draw(img)
        for i in range(config.LINES):
            for j in range(config.COLUMNS):
                x1 = j * config.PIECE_WIDTH
                y1 = i * config.PIECE_WIDTH
                x2 = x1 + config.PIECE_WIDTH
                y2 = y1 + config.PIECE_WIDTH
                try:
                    r = JSON_mod.data[config.COLUMNS * i + j]
                    if r: draw.rectangle([x1, y1, x2, y2], fill=config.keys[r + 1][1])
                except:
                    print("baddd exception!! (out of the dialog class)")

        img.save(paths.ground_truth_img, 'JPEG', quality=100)
        Image.open(paths.ground_truth_img).show()



    def open_image(self, *args):
        dlg = Gtk.FileChooserDialog("Open Image", self, Gtk.FileChooserAction.OPEN,
                                    (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OPEN, Gtk.ResponseType.OK))
        dlg.set_attached_to(self)


        # response = dlg.run()
        dlg.run()
        path = dlg.get_filename()
        if path:
            paths.img_name_original = path
            config.PIECE_WIDTH = 0
            self.first_initiate()
            dlg.destroy()
        else:
            dlg.destroy()

    def clear_all(self, *args):
        JSON_mod.clear_all()
        paths.move_pieces(JSON_mod.changed_values)
        self.noneButton.set_active(True)
        self.refresh_preview()

    def clear_key(self, menu_item, *args):
        name = menu_item.get_name().split("_")[1]
        label_id = self.get_index_label(name)
        JSON_mod.clear_key(label_id)
        paths.move_pieces(JSON_mod.changed_values)
        if config.current_value == label_id: self.noneButton.set_active(True)
        self.refresh_preview()


    # menu_parameters
    def open_parameters(self, *args):
        self.append_index_keys()
        old_piece_width = config.PIECE_WIDTH
        windowParameters = WindowParameters(self)
        windowParameters.run()
        windowParameters.destroy()
        self.refresh_preview()

    def append_index_keys(self):
        pass

    # menu about
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
        about_dialog.set_version("0.2.1 beta")
        about_dialog.set_copyright("Copyright \xc2\xa9 2017 SAMET MohamedAmin")
        about_dialog.set_authors(["SAMET MohamedAmin"])
        about_dialog.set_title("this is the title")
        about_dialog.set_comments("This is surely an unfinished job")

        logo = GdkPixbuf.Pixbuf.new_from_file("logo.png")
        about_dialog.set_logo(logo)

        about_dialog.run()
        about_dialog.destroy()


    ############################### change position methods  #############################
    def change_position(self, *args):
        # supposing that the width > height always
        config.i_adj.set_value(config.current_position)
        x, y = config.get_position(config.current_position)
        config.x_adj.set_value(x)
        config.y_adj.set_value(y)

        config.current_value = 0
        try:
            config.current_value = JSON_mod.data[config.current_position]
        except:
            if (config.tag_piece * config.current_value != 0):
                config.current_value = int(config.tag_piece[config.current_position].childNodes[0].data)

        n = config.current_value - 1
        if n < 0: self.noneButton.set_active(True)
        else: self.radio_buttons[n].set_active(True)

        self.refresh_preview()



    def refresh_preview(self):
        x, y = config.get_position(config.current_position)
        imageManipulate.refresh_preview_part(x, y)
        self.button_center.set_from_file(paths.tmp_current)


    def change_position_i(self, *args):
        if config.current_position != int(args[0].get_value()):
            config.current_position = int(args[0].get_value())
            self.change_position()

    def change_position_x(self, widget):
        x, y = config.get_position(config.current_position)
        if x != widget.get_value():
            config.current_position = int(widget.get_value()) + y * config.COLUMNS

            self.change_position()

    def change_position_y(self, widget):
        x, y = config.get_position(config.current_position)
        if y != widget.get_value():
            config.current_position = x + int(widget.get_value()) * config.COLUMNS

            self.change_position()


    def press_current_img(self, widget, event):
        x, y = (int(event.x / config.P_W_viewed),
                int(event.y / config.P_W_viewed))

        x_c, y_c = config.get_position(config.current_position)
        if x_c == config.COLUMNS - 1: x_c -= 2
        elif x_c != 0: x_c -= 1

        if y_c == config.LINES - 1: y_c -= 2
        elif y_c != 0: y_c -= 1
        self.clicked_area = (x_c + x) + (y_c + y) * config.COLUMNS

        if event.get_button()[1] == Gdk.BUTTON_SECONDARY:
            self.menu_popup.popup(None, None, None, None, 0, Gtk.get_current_event_time())
        else:
            if   (x, y) == (1, 1): self.show_preview(config.keys[config.current_value + 1][0])
            elif (x, y) == (1, 0): self.move_up()
            elif (x, y) == (2, 1): self.move_right()
            elif (x, y) == (1, 2): self.move_down()
            elif (x, y) == (0, 1): self.move_left()
            else: self.show_preview("None")

    def move_up(self):
        m = config.current_position - config.COLUMNS
        if m < 0:
            self.no_more("LINES")
        else:
            config.current_position = m
            self.change_position()

    def move_right(self):
        if (config.current_position + 1) % config.COLUMNS == 0:
            self.no_more("COLUMNS")
        else:
            config.current_position += 1
            self.change_position()

    def move_down(self):
        m = config.current_position + config.COLUMNS
        if m > config.COLUMNS * config.LINES - 1:
            self.no_more("LINES")
        else:
            config.current_position = m
            self.change_position()

    def move_left(self):
        if (config.current_position) % config.COLUMNS == 0:
            self.no_more("COLUMNS")
        else:
            config.current_position -= 1
            self.change_position()

    def move_forward(self):
        if config.current_position < (config.LINES * config.COLUMNS - 1):
            config.current_position += 1
            self.change_position()
        else:
            self.no_more("pieces")

    def move_backward(self):
        if config.current_position > 0:
            config.current_position -= 1
            self.change_position()
        else:
            self.no_more("pieces")

    def no_more(self, s):
        dialog = Gtk.MessageDialog(self, 0, Gtk.MessageType.ERROR, Gtk.ButtonsType.OK,
                                   "no more " + s)
        dialog.format_secondary_text("you've exceeded the LIMIT of " + s)
        dialog.run()

        dialog.destroy()

    #################################### show preveiw #########################################
    def show_preview(self, *args):
        index = self.get_index_label(args[-1]) + 1

        imagePreview = ImagePreview(self, index)

        imagePreview.connect("key_press_event", imagePreview.press_key_event)
        imagePreview.run()
        imagePreview.destroy()

        self.change_position()


    ##################################### other ###############################################
    def on_radio_btn_toggled(self, button):
        if button.get_active():
            n = self.get_index_label(button.get_label())
            self.set_radio_btn_active(n)


    def get_index_label(self, s):
        for i in range(1, len(config.keys)):
            if config.keys[i][0] == s: return i - 1
        return -1

    def set_tooltip_text(self, widget, event):
        x, y = (int(event.x / config.P_W_viewed),
                int(event.y / config.P_W_viewed))
        text = "open original"
        if   (x, y) == (1, 0): text = "move Up"
        elif (x, y) == (2, 1): text = "move Right"
        elif (x, y) == (1, 2): text = "move Down"
        elif (x, y) == (0, 1): text = "move Left"
        self.center_image_e.set_tooltip_text(text)

    def set_radio_btn_active(self, n):
        # if n == -1 : noneButtn
        if(JSON_mod.data[config.current_position] != n):
            JSON_mod.set_changed_values(config.current_position, n)
            JSON_mod.data[config.current_position] = n
        config.current_value = n
        self.refresh_preview()

    def press_key_event(self, widget, event):
        list_labels = ["A", "Z", "E", "R"]
        if   event.keyval == Gdk.KEY_Up:    self.move_up()
        elif event.keyval == Gdk.KEY_Right: self.move_right()
        elif event.keyval == Gdk.KEY_Down:  self.move_down()
        elif event.keyval == Gdk.KEY_Left:  self.move_left()

        elif event.keyval == Gdk.KEY_Page_Down: self.move_forward()

        elif event.keyval == Gdk.KEY_Page_Up: self.move_backward()

        elif event.keyval == Gdk.KEY_Control_R:
            self.move_forward()
            # TODO: self.xml_save_changes()

        elif event.string == "o": self.show_preview("original")
        elif event.string == "O": self.show_preview((config.keys[config.current_value + 1][0]))

        elif event.string.upper() in list_labels:
            if event.string.upper() == list_labels[0]:
                self.noneButton.set_active(True)
            else:
                n = list_labels.index(event.string.upper())
                if event.string.islower():
                    self.radio_buttons[n-1].set_active(True)
                else:
                    self.show_preview((config.keys[n + 1][0]))
