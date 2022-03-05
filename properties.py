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
from bpy.types import PropertyGroup, WindowManager
from bpy.props import *
from .functions import *


class ALP_Properties(PropertyGroup):
    layers_preset_new_name: StringProperty(
        name="Name",
        default="New Preset"
    )
    local_layer_preset: BoolProperty(
        name="Local Preset",
        description='Save preset in the current file only, otherwise save to .json file as a global preset',
        default=False
    )


class Preset_list_coll(PropertyGroup):
    preset_name: StringProperty(name="name")
    bools: StringProperty(name="layers")


classes = (
    ALP_Properties,
    Preset_list_coll,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    wm = bpy.types.WindowManager
    wm.armature_layer_presets_props = PointerProperty(type=ALP_Properties)
    bpy.types.Scene.alp_skeleton_layer_preset_coll = CollectionProperty(type=Preset_list_coll)


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)

    del bpy.types.WindowManager.armature_layer_presets_props
    del bpy.types.Scene.alp_skeleton_layer_preset_coll
