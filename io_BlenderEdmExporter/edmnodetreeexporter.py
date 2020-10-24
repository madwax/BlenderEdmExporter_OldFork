import bpy
import json
import os
import io

from .edmmessagebox import EDMUiMessageBox

from bpy.props import FloatProperty, EnumProperty, IntProperty, BoolProperty, StringProperty, FloatVectorProperty

EDMNodeTreeExportMsgBoxTitle = "EDM Material NodeTree Exporter"
EDMNodeTreeImportMsgBoxTitle = "EDM Material NodeTree Importer"


class EDMMaterialNodeJSON( ):
    
    def __init__( self, theMaterial, filepath ):
        self.theMaterial = theMaterial
        self.theFilepath = filepath
        self.data = {}
        self.nodeIdMap = {}
        self.nodeIdMapCounter = 0;

    def createNodeId( self, theNode ):
        self.nodeIdMapCounter += 1
        idIs = str( self.nodeIdMapCounter );
        self.nodeIdMap[ theNode ] = idIs;
        return idIs

    def getNodeId( self, theNode ):
        return self.nodeIdMap[ theNode ]

    def getNodeFromNodeId( self, nodeId ):
        for theNode in self.nodeIdMap:
            if self.nodeIdMap[ theNode ] == nodeId:
                return theNode
        return None      

    def createJsonType( self, obj, jsObj ):
        ret = {}
        # every nodesocket has an identifer
        ret[ "identifier" ] = obj.identifier

        theType = obj.type
        if theType == "VECTOR":
            theValue = obj.default_value
            ret[ "x" ] = theValue[ 0 ]
            ret[ "y" ] = theValue[ 1 ]
            ret[ "z" ] = theValue[ 2 ]
            jsObj[ "default_value"] = ret

        if theType == "RGBA":
            theValue = obj.default_value
            ret = {}
            ret[ "r" ] = theValue[ 0 ]
            ret[ "g" ] = theValue[ 1 ]
            ret[ "b" ] = theValue[ 2 ]
            ret[ "a" ] = theValue[ 3 ]
            jsObj[ "default_value"] = ret

        if theType == "VALUE":
            theValue = obj.default_value
            jsObj[ "default_value"] = theValue

    def exportNodes( self ):
        print( "Exporting Nodes" )

        nodesList = self.theMaterial.node_tree.nodes.items();
        for theKey, theNode in nodesList:

            # If we get to this point there do the common stuff.
            nodeObj = {}
            nodeObj[ "nodeId" ] = self.createNodeId( theNode )
            nodeObj[ "type" ] = theNode.bl_idname
            nodeObj[ "name" ] = theNode.name
            nodeObj[ "label" ] = theNode.label
            nodeObj[ "description" ] = theNode.bl_description
            nodeObj[ "x" ] = str( int( theNode.location[ 0 ] ) )
            nodeObj[ "y" ] = str( int( theNode.location[ 1 ] ) )
            nodeObj[ "width" ] = str( int( theNode.width ) )
            nodeObj[ "height" ] = str( int( theNode.height ) )

            # Do the inputs first
            inputNodes = []

            for index, theInput in enumerate( theNode.inputs ):
                #print( "  Input[ " + str( index ) + " ] Type:" + theInput.type )
                #print( "      is:" + str(  theInput.bl_idname ) )
                inputNode = {}
                inputNode[ "type" ] = theInput.type
                self.createJsonType( theInput, inputNode )
                inputNodes.append( inputNode )

            nodeObj[ "inputs" ] = inputNodes;

            # Do the outputs
            outputNodes = []

            for index, theOutput in enumerate( theNode.outputs ):
                #print( "  Input[ " + str( index ) + " ] Type:" + theInput.type )
                #print( "      is:" + str(  theInput.bl_idname ) )
                outputNode = {}
                outputNode[ "type" ] = theOutput.type
                self.createJsonType( theOutput, outputNode )
                outputNodes.append( outputNode )

            nodeObj[ "outputs" ] = outputNodes;

            self.data[ "nodes" ].append( nodeObj )

    def importNodes( self ):
        theJsonNodes = self.data[ "nodes" ]
        matNodes = self.theMaterial.node_tree.nodes

        for theJsonNode in theJsonNodes:
            print( "  Loading node type:" + theJsonNode[ "type" ] + " name:" + theJsonNode[ "name" ] + " label:" + theJsonNode[ "label" ])

            theNode = matNodes.new( type= theJsonNode[ "type" ] )            
            theNode.name = theJsonNode[ "name" ]
            theNode.label = theJsonNode[ "label" ]
            theNode.bl_description = theJsonNode[ "description" ]
            theNode.location[ 0 ] = int( theJsonNode[ "x" ] )
            theNode.location[ 1 ] = int( theJsonNode[ "y" ] )
            theNode.width = int( theJsonNode[ "width" ] )
            theNode.height = int( theJsonNode[ "height" ] )
            # build up nodeId <> node
            self.nodeIdMap[ theNode ] = theJsonNode[ "nodeId" ]

    def exportLinks( self ):
        print( "Exporting links" )
        # The links are nodeId:output => nodeId:input
        # we use the key name of the inputs/outputs so with any luck ay blender future versions will not mess things up for us

        linksList = self.theMaterial.node_tree.links.items();
        for theKey, theLink in linksList:
            
            theJsonLink = {}
            theJsonLink[ "from" ] = self.getNodeId( theLink.from_node )
            for keyObj,outputObj in theLink.from_node.outputs.items():
                if outputObj == theLink.from_socket:
                    print( "  found output socket of:" + keyObj )
                    theJsonLink[ "output" ] = keyObj

            theJsonLink[ "to" ] = self.getNodeId( theLink.to_node )
            for keyObj,inputObj in theLink.to_node.inputs.items():
                if inputObj == theLink.to_socket:
                    print( "  found input socket of:" + keyObj )
                    theJsonLink[ "input" ] = keyObj

            self.data[ "links" ].append( theJsonLink )

    def importLinks( self ):
        print( "Importing links" )
        # By this point we have all nodes loaded and nodeIdMap will be populated.
        theJsonLinks = self.data[ "links" ];
        for theJsonLink in theJsonLinks: 
            fromNode = self.getNodeFromNodeId( theJsonLink[ "from" ] )
            toNode = self.getNodeFromNodeId( theJsonLink[ "to" ] )

            fromOutputName = theJsonLink[ "output" ]
            toInputName = theJsonLink[ "input" ]

            print( " from: " + fromNode.name + " " + fromNode.bl_idname + " > " + fromOutputName )
            print( "   to: " + toNode.name + " " + toNode.bl_idname + " > " + toInputName )

            outputObj = fromNode.outputs[ fromOutputName ]
            inputObj = toNode.inputs[ toInputName ]

            self.theMaterial.node_tree.links.new( outputObj, inputObj )

            #self.theMaterial.node_tree.links.new( toNode.inputs[ theJsonLink[ "input" ] ], fromNode[ theJsonLink[ "output" ] ] )

    def writeFile( self ):
        print( "Saving to file:" + self.theFilepath )

        with io.open( self.theFilepath, "w", encoding="utf-8" ) as outputFile:
            strJson = json.dumps( self.data, ensure_ascii=False );
            outputFile.write( strJson )

    def readFile( self ):
        print( "Loading file: " + self.theFilepath )
        try:
            with io.open( self.theFilepath, "r", encoding="utf-8" ) as inputFile:
                self.data = json.load( inputFile )
        except OSError:
            EDMUiMessageBox( EDMNodeTreeImportMsgBoxTitle, "Unable to read import file:" + self.theFilepath )
            return False

        return True

    def toFile( self ):
        print( "Starting to export Material NodeTree to :" + self.theFilepath )

        # clear the json object
        self.data = {};

        versionJson = {}
        versionJson[ "major" ] = int( bpy.app.version[ 0 ] )
        versionJson[ "minor" ] = int( bpy.app.version[ 1 ] )
        versionJson[ "patch" ] = int( bpy.app.version[ 2 ] )
        self.data[ "version" ] = versionJson;
        
        self.data[ "nodes" ] = []
        self.data[ "links" ] = [] 

        self.exportNodes()
        self.exportLinks()
        
        if self.writeFile() == False:
            return False

        print( "Finished Export" )
        return True;

    def fromFile( self, clearCurrentNodeTree ):
        print( "Starting Import of Material NodeTree from :" + self.theFilepath )

        if clearCurrentNodeTree == True:
            self.theMaterial.node_tree.links.clear()
            self.theMaterial.node_tree.nodes.clear()

        self.data = {};

        if self.readFile() == False:
            return False
        
        self.importNodes( )
        self.importLinks( )
        
        return True

class EDM_OT_NodeTreeExporter( bpy.types.Operator ):
    bl_idname = "edm.op_ui_exportnodetree"
    bl_label = "Export Material node tree to JSON"

    # Ok this is nuts but what the hell.
    # File or Dir path is done through the string prop ( see subtype = "FILE_PATH" or subtype = "DIR_PATH")
    outputFilePath : bpy.props.StringProperty( 
        name = "Output Filepath",
        description = "Where the output file will be written to: Blender-BUG you need to copy-paste in the file path as there UI is broken, soz!",
        default = ""
    )

    def exportMaterial( self, theMaterial ):
        print( "Exporting the material named:" + theMaterial.name )
        if theMaterial.use_nodes == False:
            EDMUiMessageBox( EDMNodeTreeExportMsgBoxTitle, "Material does not support nodes" )
            return

        outFP = self.outputFilePath;
        if outFP == "":
            outFP = "/tmp/edm.material.nodetree.json"

        theExporter = EDMMaterialNodeJSON( theMaterial, outFP )

        if theExporter.toFile( ) == False:
            EDMUiMessageBox( EDMNodeTreeExportMsgBoxTitle, "Failed to Export the NodeTree" )

        print( "Finished the export" )

    def invoke( self, context, event ):
        wm = context.window_manager
        return wm.invoke_props_dialog( self )

    def execute( self, context ):
        self.exportMaterial( context.material )
        # EDMUiMessageBox( "Node Tree Export", "Exporting Material Named:" + currentMaterial.name )

        return {'FINISHED'}

class EDM_OT_NodeTreeImporter( bpy.types.Operator ):
    bl_idname = "edm.op_ui_importnodetree"
    bl_label = "Import Material node tree from JSON"

    # Ok this is nuts but what the hell.
    # File or Dir path is done through the string prop ( see subtype = "FILE_PATH" or subtype = "DIR_PATH")
    inputFilePath : bpy.props.StringProperty( 
        name = "Input Filepath",
        description = "Where the inout file will be read from: Blender-BUG you need to copy-paste in the file path as there UI is broken, soz!",
        default = ""
    )

    def importMaterial( self, theMaterial ):
        print( "Imorting to material named:" + theMaterial.name )
        if theMaterial.use_nodes == False:
            EDMUiMessageBox( "Material Node Tree Export", "Material does not support nodes" )
            return

        inFP = self.inputFilePath;
        if inFP == "":
            inFP = "/tmp/edm.material.nodetree.json"

        theExporter = EDMMaterialNodeJSON( theMaterial, inFP )

        # control if you want to clear the nodetree already there
        clearCurrentNodeTree = False
        if theExporter.fromFile( clearCurrentNodeTree ) == False:
            EDMUiMessageBox( EDMNodeTreeImportMsgBoxTitle, "Failed to do import" )

        print( "Finished the import" )

    def invoke( self, context, event ):
        wm = context.window_manager
        return wm.invoke_props_dialog( self )

    def execute( self, context ):
        self.importMaterial( context.material )
        return {'FINISHED'}


def registerEDMNodeExporter():
    bpy.utils.register_class( EDM_OT_NodeTreeExporter )
    bpy.utils.register_class( EDM_OT_NodeTreeImporter )

def unregisterEDMNodeExporter():
    bpy.utils.unregister_class( EDM_OT_NodeTreeExporter )
    bpy.utils.unregister_class( EDM_OT_NodeTreeImporter )


