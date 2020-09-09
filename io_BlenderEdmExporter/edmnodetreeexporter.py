import bpy
import json
import os

from .edmmessagebox import EDMUiMessageBox

from bpy.props import FloatProperty, EnumProperty, IntProperty, BoolProperty, StringProperty, FloatVectorProperty

class EDM_OT_NodeTreeExporter( bpy.types.Operator ):
    bl_idname = "edm.op_ui_exportnodetree"
    bl_label = "Export the current Material node tree in EDM Export format"

    # Ok this is nuts but what the hell.
    # File or Dir path is done through the string prop ( see subtype = "FILE_PATH" or subtype = "DIR_PATH")
    outputFilePath : bpy.props.StringProperty( 
        name = "output file",
        description = "Where to generate the export file.",
        default = "",
        subtype = "FILE_PATH"
    )

    def invoke( self, context, event ):
        wm = context.window_manager
        return wm.invoke_props_dialog( self )

    def execute( self, context ):
        # get the current node 
        currentMaterial = context.material 

        EDMUiMessageBox( "Node Tree Export", "Exporting Material Named:" + currentMaterial.name )

        return {'FINISHED'}

def registerEDMNodeExporter():
    bpy.utils.register_class( EDM_OT_NodeTreeExporter )

def unregisterEDMNodeExporter():
    bpy.utils.unregister_class( EDM_OT_NodeTreeExporter )
