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
from bpy.types import Operator
from .functions import *


class ALP_OT_save_skeleton_layers_preset(Operator):
    bl_idname = "alp.save_layers_preset"
    bl_label = "Save Skeleton Layers Preset"
    bl_description = "Save the preset as global into the .json file or as local for the current file only"

    name: bpy.props.StringProperty(name="Name")
    local: bpy.props.BoolProperty(
        name="Local",
        default=False
    )

    def execute(self, context):
        presets = context.scene.alp_skeleton_layer_preset_coll
        obj = context.active_object
        layer_bools = get_layer_bools(obj)
        if self.name == "":
            self.report({'ERROR'}, "Preset name can't be empty!")
            return {'FINISHED'}
        if self.local:
            save_layers_preset(context, self.name, layer_bools)
            return {'FINISHED'}
        presets_path = get_layer_presets_path()
        file_path = os.path.join(presets_path, self.name + ".json")
        save_preset_to_file(layer_bools, file_path)
        msg = "Armature Layer Presets: The preset has been saved to " + file_path
        self.report({'INFO'}, msg)

        return {'FINISHED'}


class ALP_OT_load_skleton_layers_preset(Operator):
    bl_idname = "alp.load_layers_preset"
    bl_label = "Load Skeleton Layers Preset"
    bl_description = "Load the preset of the state of selection for the armature layers"
    bl_options = {'UNDO'}

    name: bpy.props.StringProperty(name="Name")
    label: bpy.props.StringProperty(name="Label")

    def execute(self, context):
        if self.label == 'L':
            load_layers_preset(context, self.name)
            return {'FINISHED'}
        presets_path = get_layer_presets_path()
        file_path = os.path.join(presets_path, self.name + ".json")
        if not os.path.isfile(file_path):
            msg = "Armature Layer Presets: The preset file '" + self.name + "' does not exist"
            self.report({'ERROR'}, msg)
            return {'FINISHED'}
        load_preset_from_file(context, file_path)
        msg = "Armature Layer Presets: The preset has been loaded from " + file_path
        self.report({'INFO'}, msg)
        return {'FINISHED'}


class ALP_OT_remove_skleton_layers_preset(Operator):
    bl_idname = "alp.remove_layers_preset"
    bl_label = "Remove Skeleton Layers Preset"
    bl_description = "Delete the preset, can't be undone"

    name: bpy.props.StringProperty(name="Name")
    label: bpy.props.StringProperty(name="Label")

    def execute(self, context):
        if self.label == 'L':
            remove_layers_preset(context, self.name)
            return {'FINISHED'}
        presets_path = get_layer_presets_path()
        file_path = os.path.join(presets_path, self.name + ".json")
        if os.path.isfile(file_path):
            os.remove(file_path)
            return {'FINISHED'}

        msg = "Armature Layer Presets: The preset file '" + self.name + "' does not exist"
        self.report({'ERROR'}, msg)
        return {'FINISHED'}


class ALP_OT_browse_folder(Operator):
    bl_idname = "alp.browse_folder"
    bl_label = "Browse Folder"
    bl_description = "Open the folder in the file browser"

    directory: bpy.props.StringProperty()

    def execute(self, context):
        import sys
        directory = self.directory

        if sys.platform == "win32":
            os.startfile(directory)
        else:
            if sys.platform == "darwin":
                command = "open"
            else:
                command = "xdg-open"
            subprocess.call([command, directory])

        return {'FINISHED'}


class ALP_OT_register_in_supported_panel(Operator):
    bl_idname = "alp.register_presets_popover"
    bl_label = "Force Register Presets Popover"
    bl_description = "Manualy register the presets popover in just recently created suppopted panel"

    def execute(self, context):
        from .handler import alp_presets_in_supported_panels_register as alp_register
        alp_register(context.scene)
        return {'FINISHED'}


class WM_OT_Show_Preferences(Operator):
    bl_label = 'Show Preference Settings'
    bl_idname = 'alp.show_pref_settings'
    bl_description = "Show add-on preference settings"

    def execute(self, context):
        import addon_utils

        addons = [
            (mod, addon_utils.module_bl_info(mod))
            for mod in addon_utils.modules(refresh=False)
        ]

        for mod, info in addons:
            # if mod.__name__ == "":
            if info['name'] == "Armature Layer Presets":
                info['show_expanded'] = True

        bpy.context.preferences.active_section = 'ADDONS'
        bpy.data.window_managers["WinMan"].addon_filter = 'Interface'
        bpy.data.window_managers["WinMan"].addon_search = "Armature Layer Presets"

        bpy.ops.screen.userpref_show()
        return {'FINISHED'}


classes = [

    ALP_OT_save_skeleton_layers_preset,
    ALP_OT_load_skleton_layers_preset,
    ALP_OT_remove_skleton_layers_preset,
    ALP_OT_browse_folder,
    ALP_OT_register_in_supported_panel,
    WM_OT_Show_Preferences,
]


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in classes[::-1]:
        bpy.utils.unregister_class(cls)
