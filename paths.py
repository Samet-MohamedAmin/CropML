#!/bin/python3

from __future__ import print_function

import gi


gi.require_version('Gtk', '3.0')

import hashlib, os, io
from shutil import move, copyfile


class Paths():
    def __init__(self):
        self.img_name_original = ''

        #
        self.results = './results'
        self.keys = './keys'
        self.tmp = './tmp'


        ##
        self.results_final = os.path.join(self.results, 'final_results')
        self.conf = os.path.join(self.results, 'conf')

        ##.#
        self.tmp_open_image = os.path.join(self.tmp, 'open_image.jpg')
        self.tmp_original_preview = os.path.join(self.tmp, 'original_preview.jpg')
        self.tmp_labels_preview = os.path.join(self.tmp, 'labels_preview.jpg')
        self.tmp_current = os.path.join(self.tmp, 'current_img.jpg')
        self.tmp_scale_preview = os.path.join(self.tmp, 'scale_preview.jpg')

        self.conf_file = os.path.join(self.conf, 'conf.json')


        ###
        self.ground_truth = os.path.join(self.results_final, 'ground_truth')

    def initiate_img_paths(self, img_name_original='original.jpg'):
        print('initiate_img_paths', '-------')
        if not self.img_name_original: self.img_name_original = img_name_original
        self.img_name, self.img_ext = os.path.basename(self.img_name_original).split(".")

        self.img_abs_path = os.path.abspath(self.img_name_original)

        self.img_stamp = '_'.join([self.img_name, self.get_img_hashcode()])

        ###
        self.path_img = os.path.join(self.results, self.img_name, self.get_img_hashcode())

        ###.#
        self.ground_truth_img = os.path.join(self.ground_truth, self.img_stamp + '_GT.jpg')
        self.img_sample = os.path.join(self.results, self.img_name, self.get_img_hashcode() + '.jpg')

        ####
        self.data = os.path.join(self.path_img, 'json')

        ####.#
        self.data_file = os.path.join(self.data, '_'.join([self.img_name, self.get_img_hashcode(), 'data']) + '.json')
        self.params_file = os.path.join(self.data, '_'.join([self.img_name, self.get_img_hashcode(), 'params']) + '.json')

        self.create_img_dirs()

    def get_img_hashcode(self):
        hasher = hashlib.md5()
        with open(self.img_name_original, 'rb') as afile:
            buf = afile.read()
            hasher.update(buf)
        return hasher.hexdigest()[:8]

    def set_config(self, config):
        self.config = config

    def set_JSON_mod(self, JSON_mod):
        self.JSON_mod = JSON_mod

    def get_piece_path(self, key, i):
        str_len = len(str(self.config.LINES * self.config.COLUMNS))
        img_piece_name = '_'.join([self.img_name, self.get_img_hashcode(), str(i).rjust(str_len, '0') + '.jpg'])
        return os.path.join(self.get_key_results_path(key), img_piece_name)

    def get_key_results_path(self, key):
        return os.path.join(self.results_final, key)

    def get_key_icon_path(self, key):
        return os.path.join(self.keys, ''.join(['key_', key, '.png']))

    def create_dirs(self):
        s_err = ' is already exist'
        try: os.makedirs(self.results)
        except OSError: print('## results' + s_err)

        try: os.makedirs(self.tmp)
        except OSError: print('## tmp' + s_err)

        try: os.makedirs(self.keys)
        except OSError: print('## keys' + s_err)

        try: os.makedirs(self.conf)
        except OSError: print('## conf' + s_err)

        try: os.makedirs(self.ground_truth)
        except OSError: print('## GT' + s_err)


    def create_keys_dirs(self):
        s_err = ' is already exist'

        for key in self.config.keys[1:]:
            try: os.makedirs(self.get_key_results_path(key[0]))
            except OSError: print('## %s label + %s' %(key[0],s_err))

    def create_img_dirs(self):
        s_err = ' is already exist'

        try: os.makedirs(self.data)
        except OSError: print('## data' + s_err)


    def move_pieces(self, changed_values):
        print(changed_values)
        for i, value in changed_values.items():
            src = self.get_piece_path(self.config.keys[value[0] + 1][0], i)
            dst = self.get_piece_path(self.config.keys[value[2] + 1][0], i)
            try: move(src, dst)
            except IOError: print(src, dst)



paths = Paths()
