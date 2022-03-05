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
import sys
from bpy.app.handlers import persistent
from .functions import make_tmp_file
from .ui import *
import importlib


def get_panel_from_module(script_name, file_path=None):
    if file_path is not None:
        import imp
        imp.load_source(script_name, file_path)
    module = importlib.import_module(script_name)
    scripts = get_supported_scripts()
    return getattr(module, scripts.get(script_name))


def get_supported_scripts():
    scripts = {}
    prefs = bpy.context.preferences.addons[__package__].preferences
    script_list = prefs.support_script_list
    for item in script_list:
        if not item.use:
            continue
        scripts[item.name] = item.panel_class_name
    return scripts


@persistent
def alp_presets_in_supported_panels_register(scene):
    scripts = get_supported_scripts()
    for name, text in bpy.data.texts.items():
        if name not in scripts or not text.use_module:
            continue
        if name in sys.modules:
            del sys.modules[name]
        file_path = make_tmp_file(name, text.as_string())
        panel = get_panel_from_module(name, file_path=file_path)
        register_header_preset(panel)


def register_popover(script_name):
    if script_name not in sys.modules:
        return None
    panel = get_panel_from_module(script_name)
    register_header_preset(panel)


def unregister_popover(script_name):
    if script_name not in sys.modules:
        return None
    panel = get_panel_from_module(script_name)
    unregister_header_preset(panel)


def register():
    bpy.app.handlers.load_post.append(alp_presets_in_supported_panels_register)
    for script in get_supported_scripts():
        register_popover(script)


def unregister():
    try:
        bpy.app.handlers.load_post.remove(alp_presets_in_supported_panels_register)
    except ValueError:
        pass
    for script in get_supported_scripts():
        unregister_popover(script)
