# EDM Exporter Project Materials Blender/UI stuff
# 
import bpy
import json
import os

from bpy.props import FloatProperty, EnumProperty, IntProperty, BoolProperty, StringProperty, FloatVectorProperty
from bpy.app.handlers import persistent


class EDMEXPORTER_PT_EDMMaterial( bpy.types.Panel ):
    bl_label = "EDM Materials"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "material"

    def draw(self, context):
        layout = self.layout
        row = layout.row()
        row.label( text="This is some little test" )


def registerEDMMaterialsStuff():
    bpy.utils.register_class( EDMEXPORTER_PT_EDMMaterial )


def unregisterEDMMaterialsStuff():
    bpy.utils.unregister_class( EDMEXPORTER_PT_EDMMaterial )
