# EDM Exporter Project Settings File and UI
# Why do this?
# 1) LOD models, why have different blender files.
# 2) Information that might feed into other DCS files about your mod.
# 3) Creating things like Materials - Blender materials can be made to act like the material system used in DCS but it's a pain to do by hand.

import bpy
import json
import os

from bpy.props import FloatProperty, EnumProperty, IntProperty, BoolProperty, StringProperty, FloatVectorProperty
from bpy.app.handlers import persistent

# Filepaths we need to know about
thePluginPath = None
thePluginStaticDataPath = None

# Draw Arguments
# DCS has some common Draw Arguments for Aircraft, cockpits etc etc. 
# With this the user can select what type of project they are creating 
class EDM_EXPORTER_Draw_Argument_Key:
  def __init__( self, val, desc ):
    self.value = val;
    self.description = desc

class EDM_EXPORTER_Draw_Argument:
  def __init__( self, indexNum ):
    self.argumentNumber = indexNum
    self.description = ""
    self.keys = []
  
  def load( self, argItem ):
    
    self.description = argItem.get( "desc" )
    self.isDamage = argItem.get( "damage" )
    self.controlType = argItem.get( "controltype" )
    levels = argItem.get( "level" )

    for eachLevel in levels:
      keyLevel = EDM_EXPORTER_Draw_Argument_Key( eachLevel.get( "value" ), eachLevel.get( "desc" ) )
      self.keys.append( keyLevel )

class EDM_EXPORTER_Draw_Arguments:
  def __init__( self, argListName ):
    # The name of the draw args list
    self.name = argListName
    # The list of draw args
    self.draw_arguments = {}
    
  def load( self, filepath ):
    fixedFilepath = os.path.abspath( filepath )

    try:
      f = open( fixedFilepath, "r" )
      loadStr = f.read()
      loadStr.strip()
      rawData = json.loads( loadStr )

      for argItem in rawData[ "args" ]:
        counter = 0
        counter += 1
        range = EDM_EXPORTER_Draw_Argument( counter )
        range.load( argItem )

      print( "We Loaded:", fixedFilepath )  

    except( IOError, OSError ) as e:
      print( "There was a problem loading :", fixedFilepath )

class EDM_EXPORTER_Draw_Arguments_Collections:
  InBuiltTypes = [ 
    "Aircraft",
    "Vehicle",
    "Weapon",
    "Cockpit"
  ]

  def __init__( self ):
    print( "Creating Draw Arguments object" )
    self.list = []
    self.selected = "none";
  
  def isUserDefined( self, drawsTypeOf ):
    for eachDrawArgSet in EDM_EXPORTER_Draw_Arguments_Collections.InBuiltTypes:
      if drawsTypeOf == eachDrawArgSet.lower() :
        return False
        
    if drawsTypeOf == "none":
      return False
        
    return True
  
  def load( self, plugin_path_static_data ):
    print( "Loading draw args from path:", plugin_path_static_data )
    
    # Try to load any in built draw argument files. 
    for eachDrawArgSet in EDM_EXPORTER_Draw_Arguments_Collections.InBuiltTypes:

      newDrawArgs = EDM_EXPORTER_Draw_Arguments( eachDrawArgSet )
      self.list.append( newDrawArgs )

      filepath = plugin_path_static_data + "/draw_args_" + eachDrawArgSet.lower() + ".json"
      newDrawArgs.load( filepath )
    # Done
    
  def loadExternal( self, filepath ):
    print( "Loading draw args from external filepath:", filepath )

  # The know types of Draw Arguments list
  def uiEnumPropItems( self ):
    r = [];
    jj = ( "none", "None Selected", "No draw arguments selected" );
    r.append( jj )
    
    for each in self.list:
      j = ( each.name.lower(), each.name, each.name )
      r.append( j )

    jj = ( "user", "User Defined", "Use a user defined draw argument file" );
    r.append( jj )
    
    return r

@persistent
def EDMEXPORTER_Project_Blend_Loaded( dummy ):
  bpy.context.window_manager.edm_export_projectsettings.init()

class EDMEXPORTER_OT_Project_Populate( bpy.types.Operator ):
  bl_idname = "edmexport.project_populate"
  bl_label = "DCS Export Project Properties"

  def invoke(self, context, event):
    context.window_manager.edm_export_projectsettings.create()
    return{"FINISHED"}

def EDMEXPORTER_Project_Settings_Update_ProjectType( self, context ):
  context.window_manager.edm_export_projectsettings.sync()

class EDMEXPORTER_Project_Settings( bpy.types.PropertyGroup ):
  _isLoaded=False
  _projectType=""
  
  projectType = bpy.props.EnumProperty( name="Project Type", items=[("Not Loaded","Not Loaded","Not Loaded")] )
  
  def init( self ):
    self.load()
    self.enabled()
    
    del EDMEXPORTER_Project_Settings.projectType
    
    listOfTypes = bpy.context.window_manager.edmexport_drawargs_collection.uiEnumPropItems()
    
    EDMEXPORTER_Project_Settings.projectType = bpy.props.EnumProperty( 
      name="Project Type", 
      items=listOfTypes,
      update=EDMEXPORTER_Project_Settings_Update_ProjectType
    )  
    
    EDMEXPORTER_Project_Settings.customDrawArgumentFilePath = StringProperty(
      name="File Path",
      description="Filepath used for importing the file",
      maxlen=1024,
      subtype='FILE_PATH',
      update=EDMEXPORTER_Project_Settings_Update_ProjectType
    )
    
  # Load from JSON Object  
  def load_from( self, source ):
    asJSON = json.loads( source )
    
    loadVersion = asJSON[ "version" ]
    print( "   Loading Project Settings Version:", loadVersion )
  
    self.projectType = asJSON[ "projectType" ]
    self.customDrawArgumentFilePath = asJSON[ "customDrawArgumentFilePath" ]
  
  # Save to JSON
  def save_to( self ):
    
    obj = {}
    
    obj[ "version" ] = 1
    obj[ "projectType" ] = self.projectType
    obj[ "customDrawArgumentFilePath" ] = self.customDrawArgumentFilePath
        
    r = json.dumps( obj )    
    return r;
     
  def enabled( self ):
   return EDMEXPORTER_Project_Settings._isLoaded
    
  def create( self ):
    # Create the settings file first
    settingsFile = bpy.data.texts.new( "edmprojectsettings" )
    
    # Now set the defaults we want for the base project
    
    # Save the settings file back
    self.save()
        
    EDMEXPORTER_Project_Settings._isLoaded = True
    
  # Save the settings back to the store
  def save( self ):
    index = bpy.data.texts.find( "edmprojectsettings" )
    if index == -1:
      print( "   No EDM Export Project Settings file" )
      return

    setting = self.save_to()
    bpy.data.texts[ index ].from_string( setting )    
    
  # Load the settings from store into settings    
  def load( self ):
    print( "Loading settings text file from data store" )
    index = bpy.data.texts.find( "edmprojectsettings" )
    if index == -1:
      print( "   No EDM Export Project Settings file" )
      return

    settings = bpy.data.texts[ index ]
    self.load_from( settings.as_string() )

    EDMEXPORTER_Project_Settings._isLoaded = True
    
  def sync( self ):
    self.save()

class EDMEXPORTER_PT_Project( bpy.types.Panel ):
  bl_label = "DCS Export Project Properties"
  bl_idname = "EDMEXPORT_PT_Project"
  #bl_space_type = 'PROPERTIES'
  #bl_region_type = 'WINDOW'
  #bl_context = ".workspace"
  bl_space_type = "VIEW_3D"
  bl_region_type = "UI"
  bl_category = "Tool"
  bl_label = "EDM Project Settings"

  def draw_no_project( self, context ):
    layout = self.layout
    box = layout.row()
    box.label( text="This blend file needs to be setup for EDM Export" )
    box = layout.row()
    box.operator( "edmexport.project_populate", text="Enable EDM Export Options" )
      
  def draw_project( self, context ):
    layout = self.layout
    row = layout.row()
    row.prop( context.window_manager.edm_export_projectsettings, "projectType" )   

    if context.window_manager.edm_export_projectsettings.projectType == "user" :
      row = layout.row()
      row.prop( context.window_manager.edm_export_projectsettings, "customDrawArgumentFilePath" )   

  def draw( self, context ):
    layout = self.layout
    row = layout.row()
    
    if bpy.context.window_manager.edm_export_projectsettings.enabled() :
      self.draw_project( context )
    else:
      self.draw_no_project( context )


def registerProjectSettings():
  thePluginPath = os.path.abspath( os.path.dirname( __file__ ) )
  thePluginStaticDataPath = os.path.abspath( thePluginPath + "/data" )
  bpy.types.WindowManager.edmexport_drawargs_collection = EDM_EXPORTER_Draw_Arguments_Collections()
  bpy.context.window_manager.edmexport_drawargs_collection.load( thePluginStaticDataPath )
  bpy.utils.register_class( EDMEXPORTER_PT_Project )
  bpy.utils.register_class( EDMEXPORTER_OT_Project_Populate )
  bpy.utils.register_class( EDMEXPORTER_Project_Settings ) 
  bpy.types.WindowManager.edm_export_projectsettings = bpy.props.PointerProperty( type=EDMEXPORTER_Project_Settings )
  bpy.context.window_manager.edm_export_projectsettings.init()
  bpy.app.handlers.load_post.append( EDMEXPORTER_Project_Blend_Loaded ) 

  
def unregisterProjectSettings():
  del bpy.types.WindowManager.edmexportprojectsettings  
  bpy.utils.unregister_class( EDMEXPORTER_PT_Project )
  bpy.utils.unregister_class( EDMEXPORTER_OT_Project_Populate )
  bpy.utils.unregister_class( EDMEXPORTER_Project_Settings )

