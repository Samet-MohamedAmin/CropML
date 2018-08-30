from __future__ import print_function

import ast
import json

from config import config
from paths import paths
import os


class JSONMod():
    def __init__(self):
        self.data = {}
        self.changed_values = {}

    def data_init(self):
        self.data = {k: 0 for k in range(config.LINES * config.COLUMNS)}
        with open(paths.data_file, 'w') as f:
            json.dump(self.data, f, indent=4, sort_keys=True, separators=(',', ': '), ensure_ascii=True)

    def save_data(self, *args):
        with open(paths.data_file, 'w') as f:
            json.dump(self.data, f, indent=4, sort_keys=True, separators=(',', ': '), ensure_ascii=True)

        self.update_key_total()
        self.conf_save()
        self.params_update_others()
        self.params_save()

        paths.move_pieces(self.changed_values)
        del self.changed_values
        self.changed_values = {}

    def import_data(self):
        try:
            with open(paths.data_file) as f:
                self.data = {int(k): v for k, v in json.load(f).items()}
            return True
        except:
            config.new_image()
            self.data_init()
            return False

    def set_changed_values(self, k, v):
        if self.data[k] != v:
            # try : just to store the initial value
            # because self.data always change
            # 0 => initial value before save
            # 1 => previous value
            # 2 => last value
            try:
                self.changed_values[k]
            except KeyError:
                self.changed_values[k] = {0: self.data[k]}

            if self.changed_values[k][0] != v:
                self.changed_values[k][1] = self.data[k]
                self.changed_values[k][2] = v
            else:
                del self.changed_values[k]

        print(self.changed_values)

    def clear_all(self):
        for k, v in self.data.items():
            if v != 0:
                self.set_changed_values(k, 0)
        del self.data
        self.data_init()

    def clear_key(self, label_id):
        for k, v in self.data.items():
            if v == label_id:
                self.set_changed_values(k, 0)
                self.data[k] = 0

        self.save_data()

    def conf_save(self):
        with open(paths.conf_file, 'w') as f:
            json.dump(self.conf, f, indent=4, sort_keys=True, separators=(',', ': '), ensure_ascii=False)

    def conf_create_or_import_conf_file(self):
        if os.path.isfile(paths.conf_file):
            with open(paths.conf_file) as f:
                self.conf = ast.literal_eval(json.dumps(json.load(f)))


            for i in range(len(config.keys)):
                config.keys[i][0] = self.conf['keys'][i]['name']
                config.keys[i][1] = self.conf['keys'][i]['color']

        else:
            self.conf = {'imgs': [],
                         'keys': [{'name': key[0], 'color': key[1], 'total': 0} for key in config.keys]}
        self.conf_add_current_img()
        self.conf_save()

    def conf_get_obj(self):
        for img in self.conf['imgs']:
            if img['name'] == paths.img_name:
                img_obj = img['objs']
                for item in img_obj:
                    if item['hashcode'] == paths.get_img_hashcode():
                        return item

    def conf_add_current_img(self):
        img_obj = None
        try:
            for img in self.conf['imgs']:
                if img['name'] == paths.img_name:
                    img_obj = img['objs']
                    for item in img_obj:
                        if item['hashcode'] == paths.get_img_hashcode():
                            return
        except:
            pass

        if img_obj is None:
            img_obj = []
            self.conf['imgs'].append({
                'name': paths.img_name,
                'objs': img_obj
            })

        img_obj.append({
            'hashcode': paths.get_img_hashcode(),
            'info': {
                'lines': config.LINES,
                'cols': config.COLUMNS
            }
        })

        self.update_key_total(first_time_conf=True)

    def params_save(self):
        with open(paths.params_file, 'w') as f:
            json.dump(self.params, f, indent=4, sort_keys=True, separators=(',', ': '), ensure_ascii=False)

    def params_create_or_import_params_file(self):
        if os.path.isfile(paths.params_file):
            with open(paths.params_file) as f:
                self.params = ast.literal_eval(json.dumps(json.load(f)))

            config.PIECE_WIDTH = self.params['pieces']['piece_width']
            config.COLUMNS = self.params['pieces']['cols']
            config.LINES = self.params['pieces']['lines']

            config.scale_value = self.params['confs']['scale_preview']

        else:
            self.params = {
                'img': {
                    'name': '',
                    'hashcode': '',
                    'original_width': '',
                    'original_height': '',
                },
                'pieces': {
                    'piece_width': '',
                    'cols': '',
                    'lines': '',
                    'nb_pieces': '',
                },
                'keys': [0 for i in range(len(config.keys) - 1)],
                'confs': {
                    'scale_preview': ''
                },
                'current': 0
            }
            self.params_add_current_img()
            self.params_save()
        print(self.params)

    def params_add_current_img(self):
        self.params['img']['name'] = paths.img_name
        self.params['img']['hashcode'] = paths.get_img_hashcode()
        self.params['img']['original_width'] = config.w
        self.params['img']['original_height'] = config.h

        self.params['pieces']['piece_width'] = config.PIECE_WIDTH
        self.params['pieces']['cols'] = config.COLUMNS
        self.params['pieces']['lines'] = config.LINES
        self.params['pieces']['nb_pieces'] = config.COLUMNS * config.LINES

        self.params['confs']['scale_preview'] = config.scale_value

        self.update_key_total(first_time_params=True)

    def params_update_others(self):
        self.params['pieces']['piece_width'] = config.PIECE_WIDTH
        self.params['pieces']['cols'] = config.COLUMNS
        self.params['pieces']['lines'] = config.LINES
        self.params['pieces']['nb_pieces'] = config.COLUMNS * config.LINES

        self.params['confs']['scale_preview'] = config.scale_value

        self.params['current'] = config.current_position

    def update_key_total(self, first_time_params=False, first_time_conf=False):
        keys_add = [0 for i in range(len(config.keys) - 1)]
        print('-' * 50)
        print()
        if first_time_conf:
            print('update key total conf')
            for k, v in self.data.items():
                self.conf['keys'][v + 1]['total'] += 1

        elif first_time_params:
            print('update key total params')
            for k, v in self.data.items():
                self.params['keys'][v] += 1

        else:
            for k, v in self.changed_values.items():
                keys_add[v[0]] -= 1
                keys_add[v[2]] += 1

            for i in range(len(keys_add)):
                self.conf['keys'][i + 1]['total'] += keys_add[i]
                self.params['keys'][i] += keys_add[i]

        print('keys_add')
        print(keys_add)

    def new_PW(self):
        # keys
        self.conf['keys'][1]['total'] += config.LINES * config.COLUMNS - self.params['keys'][0]
        self.params['keys'][0] = config.LINES * config.COLUMNS
        for i in range(1, len(config.keys)-1):
            self.conf['keys'][i + 1]['total'] -= self.params['keys'][i]
            self.params['keys'][i] = 0

        # params
        self.params['img']['original_width'] = config.w
        self.params['img']['original_height'] = config.h

        self.params['pieces']['piece_width'] = config.PIECE_WIDTH
        self.params['pieces']['cols'] = config.COLUMNS
        self.params['pieces']['lines'] = config.LINES
        self.params['pieces']['nb_pieces'] = config.COLUMNS * config.LINES

        self.params['confs']['scale_preview'] = config.scale_value

        self.params['current'] = 0

        # conf
        for img in self.conf['imgs']:
            if img['name'] == paths.img_name:
                img_obj = img['objs']
                for item in img_obj:
                    if item['hashcode'] == paths.get_img_hashcode():
                        obj = item
        obj['info']['lines'] = config.LINES
        obj['info']['cols'] = config.COLUMNS

        self.conf_save()
        self.params_save()

        # data
        JSON_mod.data_init()



JSON_mod = JSONMod()
