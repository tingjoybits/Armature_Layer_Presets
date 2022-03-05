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
from bpy.types import AddonPreferences
from .functions import *


class Support_layers_panel_coll(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty()
    panel_class_name: bpy.props.StringProperty()
    path: bpy.props.StringProperty()
    use: bpy.props.BoolProperty(default=True)


class ALP_OT_add_support_layers_panel_class(bpy.types.Operator):
    bl_idname = "alp.add_support_layers_panel_class"
    bl_label = "Add Support Layers Panel"
    bl_description = "Save the .json config file to support the specified layers panel"

    def execute(self, context):
        prefs = context.preferences.addons[__package__].preferences
        script_list = prefs.support_script_list
        name = prefs.script_name
        panel = prefs.layers_panel_class_name
        if name == "" or panel == "":
            self.report({'ERROR'}, "The script name or the panel name can't be empty!")
            return {'FINISHED'}
        if not name.endswith('.py'):
            name += '.py'
        support_panels_path = os.path.join(get_config_path(), "layer_panels")
        validate_path(support_panels_path)
        file_path = os.path.join(support_panels_path, name[:-3] + ".json")
        save_json_data(file_path, {name: panel})
        add_support_panel_to_list(name, panel, file_path, True)
        msg = "Armature Layer Presets: The panel config file saved to " + file_path
        self.report({'INFO'}, msg)

        return {'FINISHED'}


class ALP_OT_remove_supported_layers_panel_class(bpy.types.Operator):
    bl_idname = "alp.remove_supported_layers_panel_class"
    bl_label = "Remove Supported Layers Panel"
    bl_description = "Delete the config file of the supported layers panel"

    name: bpy.props.StringProperty()
    panel: bpy.props.StringProperty()
    path: bpy.props.StringProperty()

    def execute(self, context):
        prefs = context.preferences.addons[__package__].preferences
        script_list = prefs.support_script_list
        for i, item in enumerate(script_list):
            if item.name != self.name or\
                    item.panel_class_name != self.panel:
                continue
            script_list.remove(i)
            if os.path.isfile(self.path):
                os.remove(self.path)
        msg = "Armature Layer Presets: The config file has been removed " + self.path
        self.report({'INFO'}, msg)

        return {'FINISHED'}


class PREF_UL_support_panel_list(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            if item:
                row = layout.row()
                if item.use:
                    icon = 'CHECKBOX_HLT'
                else:
                    icon = 'CHECKBOX_DEHLT'
                row.prop(item, "use", text="", icon=icon, emboss=False)
                row.prop(item, "name", text="", emboss=False)
                row = layout.row()
                row.prop(item, "panel_class_name", text="", emboss=False)
                row.operator(
                    "alp.browse_folder", text='',
                    icon='FILEBROWSER', emboss=False
                ).directory = os.path.dirname(item.path)
                op = row.operator(
                    "alp.remove_supported_layers_panel_class",
                    text='', icon='PANEL_CLOSE', emboss=False
                )
                op.name = item.name
                op.panel = item.panel_class_name
                op.path = item.path
            else:
                layout.label(text="", translate=False)
        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            layout.label(text="")  # icon_value=icon


class ALP_Preferences(AddonPreferences):
    bl_idname = __package__

    support_script_list: bpy.props.CollectionProperty(type=Support_layers_panel_coll)
    support_script_list_index: bpy.props.IntProperty(name='Active Item')
    script_name: bpy.props.StringProperty(
        name="Script Name",
        description="Type a name of the UI script with .py in the end stored in the texts data that gonna be loaded on open .blend file"
    )
    layers_panel_class_name: bpy.props.StringProperty(
        name="Layers Panel Class Name",
        description="Type a class name of the layers panel defined in the script"
    )

    def draw(self, context):
        load_supported_panel_list()
        layout = self.layout

        layout.label(text="Support Rig's Layers Panel:")

        row = layout.row()
        row.template_list(
            "PREF_UL_support_panel_list",
            "support_script_list",
            self, "support_script_list",
            self, 'support_script_list_index',
            rows=3
        )
        self.support_script_list_index = max(
            0, min(self.support_script_list_index, len(self.support_script_list)-1)
        )
        row = layout.row()
        box = row.box()
        row = box.row()
        col = row.column()
        col.label(text="Script Name:")
        col.prop(self, "script_name", text='')
        col = row.column()
        col.label(text="Layers Panel Class Name:")
        subrow = col.row()
        subrow.prop(self, "layers_panel_class_name", text='')
        subrow.operator("alp.add_support_layers_panel_class", text='', icon='ADD')


def add_support_panel_to_list(script_name, panel_name, path, use):
    prefs = bpy.context.preferences.addons[__package__].preferences
    script_list = prefs.support_script_list
    item = script_list.add()
    item.name = script_name
    item.panel_class_name = panel_name
    item.path = path
    if use is not None:
        item.use = use


def load_supported_panel_list():
    prefs = bpy.context.preferences.addons[__package__].preferences
    use_items = {}
    script_list = prefs.support_script_list
    for item in script_list:
        use_items[item.name] = item.use
    script_list.clear()
    native_panels_path = os.path.join(os.path.dirname(__file__), "layer_panels")
    config_panels_path = os.path.join(get_config_path(), "layer_panels")
    validate_path(config_panels_path)
    native_files = [(f, native_panels_path) for f in get_file_list_names(native_panels_path)]
    config_files = [(f, config_panels_path) for f in get_file_list_names(config_panels_path)]
    for file_name, location in native_files + config_files:
        name = file_name + '.py'
        path = os.path.join(location, file_name + '.json')
        data = get_json_data(path)
        add_support_panel_to_list(name, data.get(name), path, use_items.get(name))


classes = [
    Support_layers_panel_coll,
    ALP_OT_add_support_layers_panel_class,
    ALP_OT_remove_supported_layers_panel_class,
    PREF_UL_support_panel_list,
    ALP_Preferences,
]


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    load_supported_panel_list()


def unregister():
    for cls in classes[::-1]:
        bpy.utils.unregister_class(cls)
