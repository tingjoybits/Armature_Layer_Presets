# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

import bpy
import os
import json


def validate_path(path):
    if not os.path.isdir(path):
        os.mkdir(path, mode=0o777)


def get_config_path():
    user_path = bpy.utils.resource_path('USER')
    config_path = os.path.join(user_path, "config")
    config_path = os.path.join(config_path, "armature_layer_presets")
    validate_path(config_path)
    return config_path


def get_layer_presets_path():
    path = os.path.join(get_config_path(), "layer_presets")
    validate_path(path)
    return path


def get_json_data(json_file_path):
    data = {}
    if not os.path.isfile(json_file_path):
        return None
    f = open(json_file_path)
    file_data = json.load(f)
    for pr in file_data:
        value = file_data.get(pr)
        data[pr] = value
    f.close()
    return data


def save_json_data(json_file_path, save_data):
    with open(json_file_path, 'w', encoding='utf-8') as f:
        json.dump(save_data, f, ensure_ascii=False, indent=4)


def save_layers_preset(context, preset_name, layer_bools):
    presets = context.scene.alp_skeleton_layer_preset_coll
    for p in presets:
        if p.preset_name == preset_name:
            p.bools = ' '.join([str(int(i)) for i in layer_bools])
            return None
    new = presets.add()
    new.preset_name = preset_name
    new.bools = ' '.join([str(int(i)) for i in layer_bools])


def load_layers_preset(context, preset_name):
    obj = context.active_object
    presets = context.scene.alp_skeleton_layer_preset_coll
    bools = None
    for p in presets:
        if p.preset_name == preset_name:
            bools = [int(i) for i in p.bools.split()]
            break
    if not bools:
        return None
    for i, layer in enumerate(obj.data.layers):
        obj.data.layers[i] = bools[i]


def remove_layers_preset(context, preset_name):
    obj = context.active_object
    presets = context.scene.alp_skeleton_layer_preset_coll
    for i, p in enumerate(presets):
        if p.preset_name == preset_name:
            presets.remove(i)
            break


def get_layer_bools(armature):
    return [layer for layer in armature.data.layers]


def set_layer_bools(armature, bools):
    for i in range(len(armature.data.layers)):
        armature.data.layers[i] = bools[i]


def save_preset_to_file(layer_bools, file_path):
    pref_data = {}
    pref_data['Layers'] = layer_bools
    save_json_data(file_path, pref_data)


def load_preset_from_file(context, file_path):
    obj = context.active_object
    pref_data = get_json_data(file_path)
    bools = pref_data.get('Layers')
    if not bools:
        return None
    set_layer_bools(obj, bools)


def get_file_list_names(path, full_name=False, extension='.json'):
    file_names = []
    for file in os.listdir(path):
        if os.path.isfile(os.path.join(path, file)) and\
                file.lower().endswith(extension):
            if full_name:
                file_names.append(file)
                continue
            name = file.split(extension)[0]
            file_names.append(name)
    return file_names


def global_layer_preset_names():
    presets_path = get_layer_presets_path()
    validate_path(presets_path)
    return get_file_list_names(presets_path)


def skeleton_layer_presets(context):
    local_presets = context.scene.alp_skeleton_layer_preset_coll
    local_names = [('L', p.preset_name) for p in local_presets]
    global_names = [('G', p) for p in global_layer_preset_names()]
    return local_names + global_names


def make_tmp_file(file_name, text=None):
    import tempfile
    file_path = os.path.join(tempfile.gettempdir(), file_name)
    module_file = open(file_path, "w")
    if text is not None:
        module_file.write(text)
    module_file.close()
    return file_path
