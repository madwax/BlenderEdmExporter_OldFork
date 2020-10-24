# EDM Exporter Project Materials Blender/UI stuff
# 
import bpy
import json
import os


from bpy.props import FloatProperty, EnumProperty, IntProperty, BoolProperty, StringProperty, FloatVectorProperty
from bpy.app.handlers import persistent

from .edmmessagebox import EDMUiMessageBox

SupportedEDMMaterialTypes = [
    ( "None", "None", "None" ),
    ( "def_material","def_material","def_material" ),
    ( "glass_material","glass_material","glass_material" ),
    ( "self_illum_material", "self_illum_material", "self_illum_material")
]

CreateTextureSizes = [
    ( "1024x1024", "1024x1024", "1024x1024" ),
    ( "2048x2048", "2048x2048", "2048x2048" ),
    ( "4096x4096", "4096x4096", "4096x4096" )
]

class EDM_OT_MaterialsCreateDialog( bpy.types.Operator ):
    bl_idname = "edm.op_ui_materials_dialog"
    bl_label = "Create Material for EDM Export"

    # What type of material we are creating
    materialType : bpy.props.EnumProperty( name="Material Type", items = SupportedEDMMaterialTypes )
    # The name of the material.
    materialName : bpy.props.StringProperty( name="Name", description="The name of the material" )
    # If we are to create blank textures for the newley created material.
    createTextures : bpy.props.BoolProperty( name="Create Textures", description="Create blank textures that are usable as a starting point", default=True )
    # If we are to create blank textures what size to use
    createTexturesOfSize : bpy.props.EnumProperty( name="Textures Size", description="The size of textures to be created", items=CreateTextureSizes )
    # If we are to support roughMet or not?
    # currently we don't support the old spec system so if you don't do roughMet then you just get simple diffuse texture mapping
    useRoughMet : bpy.props.BoolProperty( name="RoughMet Support", description="Does the material support RoughMet", default=False )
    # if we are to support Damage Textures or not?
    useDamageTextures : bpy.props.BoolProperty( name="Damage Texture Support", description="Does the material support Damage Textures", default=False )
    # If we are to support Decal Textures or not?
    useDecalTexture : bpy.props.BoolProperty( name="Decal Support", description="Does the material support Decal Textures", default=False )
    
    # If the current material type supports RoughMet.
    # I think there are number of others that support it but I need to work out what.
    def SupportRoughMet( self ):
        if self.materialType == "def_material":
            return True
        if self.materialType == "glass_material":
            return True
        return False

    # If the current material type supports Damage textures
    def SupportDamageTextures( self ):
        if self.materialType == "def_material":
            return True
        if self.materialType == "glass_material":
            return True
        return False

    # If the current material type supports Decal textures
    def SupportDecal( self ):
        if self.materialType == "def_material":
            return True
        return False

    def draw(self, context):
        #layout = self.layout

        if( self.materialType == "None" ):
            self.layout.row().label( text="Pease Select a EDM Material Type " )
            self.layout.row().prop( self, "materialType" )
            return
        
        self.layout.row().label( text="Type: " + str( self.materialType ) )

        # Common stuff used not matter what type of material we have
        self.layout.row().prop( self, "materialName" )
        self.layout.row().prop( self, "createTextures" )
        if self.createTextures == True:
            # User want to create the textures for them.
            self.layout.row().prop( self, "createTexturesOfSize" )

        if self.SupportDecal( ):
            self.layout.row().prop( self, "useDecalTexture" )

        if self.SupportRoughMet( ):
            self.layout.row().prop( self, "useRoughMet" )

        if self.SupportDamageTextures( ):
            self.layout.row().prop( self, "useDamageTextures" )

    def invoke( self, context, event ):
        wm = context.window_manager
        return wm.invoke_props_dialog( self )

    def createDefMaterial( self, theMaterial ):
        print( "there there ")

    def createGlassMaterial( self, theMaterial ):
        print( "Was there" )

    def createMaterial( self ):
        # Basic checks first!
        if self.materialName == "":
            self.materialName = "EDM Materail"

        # now times to create the material
        theMaterial = bpy.data.materials.new( name=self.materialName )
        theMaterial.use_nodes = True
        # remove any nodes in the default
        theMaterial.node_tree.links.clear()
        theMaterial.node_tree.nodes.clear()

        # Set some common edm params on the material. 
        theMaterial.edmMaterialType = self.materialType
        theMaterial.edmExportable = True;

        # Now we need to create the nodes for the different types of material we are using.
        if self.materialType == "def_material":
            self.createDefMaterial( theMaterial )
        elif self.materialType == "glass_material":
            self.createGlassMaterial( theMaterial )
        else:
            EDMUiMessageBox( "Failed to create Material", "Selected Material Type of " + self.materialType + " is currently not supported" )
            return

    def execute( self, context ):
        self.createMaterial()
        return {'FINISHED'}

# The EDM Export Materials Panel
# This panel is used to create a blender material with everything we need to do the exporting.
# Were possible we hold there hand. 
class EDM_PT_Material( bpy.types.Panel ):
    bl_label = "EDM Material"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "material"

    def draw(self, context):
        self.layout.row().operator( "edm.op_ui_materials_dialog" )
        self.layout.row().operator( "edm.op_ui_exportnodetree" )
        self.layout.row().operator( "edm.op_ui_importnodetree" )


def registerEDMMaterialsStuff():

    # We need to register some of are own properties to material
    bpy.types.Material.edmExportable = bpy.props.BoolProperty( 
            name="Export", 
            description="Should the Materail be exportable into an EDM file", 
            default=False 
    )

    # what type of material this will be exported as 
    # see SupportedEDMMaterialTypes
    bpy.types.Material.edmMaterialType = bpy.props.StringProperty( 
        name="EMD Material type",
        description="The EDM Material Name/Type to be exported as",
        default="None"
    )

    
    bpy.utils.register_class( EDM_OT_MaterialsCreateDialog )
    bpy.utils.register_class( EDM_PT_Material )

def unregisterEDMMaterialsStuff():
    bpy.utils.unregister_class( EDM_OT_MaterialsCreateDialog )
    bpy.utils.unregister_class( EDM_PT_Material )
