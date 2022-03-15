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
from bpy.types import Panel
from .functions import *
from bl_ui.properties_data_armature import DATA_PT_skeleton


class POPOVER_PT_Skeleton_Layer_Presets(Panel):
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'HEADER'
    bl_label = "Skeleton Layer Presets"
    bl_idname = "POPOVER_PT_skeleton_layer_presets"

    def draw(self, context):
        props = context.window_manager.armature_layer_presets_props
        layout = self.layout
        layout.emboss = 'PULLDOWN_MENU'
        preset_names = skeleton_layer_presets(context)
        for label, name in preset_names:
            row = layout.row(align=True)
            sub_row = row.row(align=True)
            sub_row.scale_x = 0.35
            sub_row.label(text=label)
            op = row.operator('alp.load_layers_preset', text=name)
            op.name = name
            op.label = label
            op = row.operator('alp.remove_layers_preset', text='', icon='REMOVE')
            op.name = name
            op.label = label
        row = layout.row(align=True)
        row.emboss = 'NORMAL'
        row.operator("alp.register_presets_popover", text='', icon='MENU_PANEL')
        row.operator("alp.show_pref_settings", text='', icon='PREFERENCES')
        row.prop(props, "layers_preset_new_name", text='')
        sub_row = row.row(align=True)
        sub_row.scale_x = 0.34
        sub_row.prop(props, "local_layer_preset", text='L', toggle=True)
        sub_row = row.row(align=False)
        sub_row.emboss = 'PULLDOWN_MENU'
        op = sub_row.operator('alp.save_layers_preset', text='', icon='ADD')
        op.name = props.layers_preset_new_name
        if props.local_layer_preset:
            op.local = True
        else:
            op.local = False


def draw_header_preset(self, context):
    layout = self.layout
    layout.emboss = 'NONE'
    layout.popover("POPOVER_PT_skeleton_layer_presets", text='Layers', icon='PRESET')


def get_panel_subclasses(cls):
    subclasses = []
    for scls in bpy.types.Panel.__subclasses__():
        if hasattr(scls, "bl_parent_id"):
            if not scls.bl_parent_id == cls.__name__:
                continue
            subclasses.append(scls)
    return subclasses


def register_header_preset(cls):
    classes = [cls] + get_panel_subclasses(cls)
    for c in classes:
        if "bl_rna" in c.__dict__:
            bpy.utils.unregister_class(c)
    setattr(cls, 'draw_header_preset', staticmethod(draw_header_preset))
    for c in classes:
        bpy.utils.register_class(c)


def unregister_header_preset(cls):
    classes = [cls] + get_panel_subclasses(cls)
    for c in classes:
        if "bl_rna" in c.__dict__:
            bpy.utils.unregister_class(c)
    if hasattr(cls, 'draw_header_preset'):
        del cls.draw_header_preset
    for c in classes:
        bpy.utils.register_class(c)


classes = [
    POPOVER_PT_Skeleton_Layer_Presets,
]


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    register_header_preset(DATA_PT_skeleton)


def unregister():
    unregister_header_preset(DATA_PT_skeleton)
    for cls in classes[::-1]:
        bpy.utils.unregister_class(cls)
