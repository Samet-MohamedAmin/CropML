from __future__ import print_function

import gi

gi.require_version('Gtk', '3.0')

from PIL import Image, ImageDraw

from config import config
from paths import paths
from JSON_mod import JSON_mod


class ImageManipulate():
    def refresh_preview_part(self, x, y):
        p_w_v = config.P_W_viewed
        c, l = x, y

        if c != 0:
            if c == config.COLUMNS - 1:
                c -= 2
            else:
                c -= 1

        if l != 0:
            if l == config.LINES - 1:
                l -= 2
            else:
                l -= 1

        img_current_tmp = config.img_cropped.crop((c * config.PIECE_WIDTH,
                                                   l * config.PIECE_WIDTH,
                                                   (c + 3) * config.PIECE_WIDTH,
                                                   (l + 3) * config.PIECE_WIDTH)) \
            .resize((3 * p_w_v, 3 * p_w_v), Image.ANTIALIAS)
        draw = ImageDraw.Draw(img_current_tmp)

        for i in range(9):
            x_i, y_i = i % 3, i / 3
            # TODO: get value from xml
            # r = int(config.tag_piece[c + x_i + (l + y_i) * config.COLUMNS].childNodes[0].data)
            r = JSON_mod.data[c + x_i + (l + y_i) * config.COLUMNS]
            if r > 0:
                fill = config.keys[r + 1][1]
                if fill.upper() == "GREEN":
                    fill = "#4caf50"
                elif fill.upper() == "YELLOW":
                    fill = "#ffeb3b"
                elif fill.upper() == "RED":
                    fill = "#f44336"
                draw.line([x_i * p_w_v, y_i * p_w_v, (x_i + 1) * p_w_v, (y_i + 1) * p_w_v], fill, config.pp)
                draw.line([(x_i + 1) * p_w_v, y_i * p_w_v, x_i * p_w_v, (y_i + 1) * p_w_v], fill, config.pp)

        for i in (config.pp / 2 - 1, p_w_v, 2 * p_w_v, 3 * p_w_v - config.pp / 2 - 1):
            draw.line([i, 0, i, 3 * p_w_v], config.black, config.pp)
        for i in (config.pp / 2 - 1, p_w_v, 2 * p_w_v, 3 * p_w_v - config.pp / 2 - 1):
            draw.line([0, i, 3 * p_w_v, i], config.black, config.pp)

        # draw.line([(x - c) * p_w_v, 0, (x - c) * p_w_v, p_w_v], config.keys[1][1], config.pp)
        # draw.line([(x - c + 1) * p_w_v, 0, (x - c + 1) * p_w_v, p_w_v], config.keys[1][1], config.pp)
        # draw.line([0, (y - l) * p_w_v, p_w_v, (y - l) * p_w_v], config.keys[1][1], config.pp)
        # draw.line([0, (y - l + 1) * p_w_v, p_w_v, (y - l + 1) * p_w_v], config.keys[1][1], config.pp)

        for i in range(-1, config.pp, 1):
            draw.rectangle(
                [(x - c) * p_w_v + i, (y - l) * p_w_v + i, (x - c + 1) * p_w_v - i + 1, (y - l + 1) * p_w_v - i + 1],
                outline=config.keys[0][1])

        img_current_tmp.save(paths.tmp_current)

    def crop_pieces(self):
        # change_it: piece_width in main window
        config.img_cropped.save(paths.img_sample, 'JPEG', quality=100)
        i = 0
        print(JSON_mod.data)
        for y in range(0, config.h, config.PIECE_WIDTH):
            for x in range(0, config.w, config.PIECE_WIDTH):
                area = (x, y, x + config.PIECE_WIDTH, y + config.PIECE_WIDTH)
                cropped_img = config.img_cropped.crop(area)
                # cropped_img = cropped_img.resize((config.P_W_viewed,config.P_W_viewed), Image.ANTIALIAS)
                key = config.keys[JSON_mod.data[i]+1][0]
                cropped_img.save(paths.get_piece_path(key, i), 'JPEG', quality=100)
                i += 1

    def image_preview_draw_rectangles(self, draw, hide):
        p_w = config.PIECE_WIDTH
        for i in range(config.LINES):
            for j in range(config.COLUMNS):

                r = JSON_mod.data[config.COLUMNS * i + j]
                r += 1
                fill, outline = config.keys[r][1], config.black
                if hide == r:
                    fill = None
                elif r == 1:
                    outline = None
                if fill:
                    if fill.upper() == "GREEN":
                        fill = "#4caf50"
                    elif fill.upper() == "YELLOW":
                        fill = "#ffeb3b"
                    elif fill.upper() == "RED":
                        fill = "#f44336"
                draw.rectangle([j * p_w, i * p_w, p_w * (j + 1) - 1, p_w * (i + 1) - 1], fill=fill, outline=outline)

    def image_preview_draw_current_pos(self, draw):
        keys = config.keys
        pp = config.pp
        p_w = config.PIECE_WIDTH
        l, c = config.get_position(config.current_position)
        x1, y1, x2, y2 = l * p_w + pp / 2 - 1, c * p_w - 1, p_w * (l + 1) - pp / 2, p_w * (c + 1)

        draw.line([x1, y1, x2, y1], keys[0][1], pp)
        draw.line([x2, y1, x2, y2], keys[0][1], pp)
        draw.line([x2, y2, x1, y2], keys[0][1], pp)
        draw.line([x1, y2, x1, y1], keys[0][1], pp)

    def image_preview_save_draw(self, img):
        WIDTH = int(config.w * config.scale_value)
        HEIGHT = int(config.h * config.scale_value)
        img = img.resize((WIDTH, HEIGHT), Image.ANTIALIAS)
        img.save(paths.tmp_open_image, 'JPEG', quality=100)

    def image_preview_generate_keys(self, hide):
        keys = config.keys
        for i in range(2, len(keys)):
            fill = keys[i][1]
            if hide == i: fill = keys[1][1]

            if fill.upper() == "GREEN":
                fill = "#4caf50"
            elif fill.upper() == "YELLOW":
                fill = "#ffeb3b"
            elif fill.upper() == "RED":
                fill = "#f44336"

            im = Image.new("RGB", (20, 20), fill)
            ImageDraw.Draw(im).rectangle([0, 0, 19, 19], outline="#212121")
            ImageDraw.Draw(im).rectangle([1, 1, 18, 18], outline="#212121")

            im.save(paths.get_key_icon_path(str(i - 1)))

        im = Image.new("RGBA", (20, 20), (0, 0, 0, 0))
        im_draw = ImageDraw.Draw(im)
        w, h = im.size
        im_draw.rectangle([0, 0, w - 1, h - 1], outline=keys[0][1])
        im_draw.rectangle([1, 1, w - 2, h - 2], outline=keys[0][1])
        del (im_draw)
        im.save(paths.get_key_icon_path('current'))

    def window_parameters_draw_image(self):
        img = Image.open(paths.img_sample)
        w, h = img.size

        draw = ImageDraw.Draw(img)

        for i in range(0, w, config.PIECE_WIDTH):
            draw.line([i, 0, i, h], config.black, 1)
        for i in range(0, h, config.PIECE_WIDTH):
            draw.line([0, i, w, i], config.black, 1)

        # for path in range(2, len(config.keys)):
        #     for i in config.keys[path][2]:
        #         x1, y1 = config.get_position(i)
        #         x1, y1 = x1 * config.PIECE_WIDTH, y1 * config.PIECE_WIDTH
        #         draw.rectangle([x1, y1, x1 + config.PIECE_WIDTH, y1 + config.PIECE_WIDTH],
        #                        fill=config.keys[path][1],
        #                        outline=config.black)

        x1, y1 = int((config.COLUMNS - 1) / 2) * config.PIECE_WIDTH, int((config.LINES - 1) / 2) * config.PIECE_WIDTH
        x2, y2 = x1 + config.PIECE_WIDTH, y1 + config.PIECE_WIDTH
        draw.line([x1, y1, x2, y1], config.keys[0][1], 5)
        draw.line([x2, y1, x2, y2], config.keys[0][1], 5)
        draw.line([x2, y2, x1, y2], config.keys[0][1], 5)
        draw.line([x1, y2, x1, y1], config.keys[0][1], 5)

        img = img.resize((int(w * config.scale_min), int(h * config.scale_min)), Image.ANTIALIAS)
        img.save(paths.tmp_labels_preview, "JPEG", quality=100)


imageManipulate = ImageManipulate()
