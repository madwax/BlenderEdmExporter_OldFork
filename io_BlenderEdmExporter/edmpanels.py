import bpy

class EDMObjectContextMenuSubMenu( bpy.types.Menu ):
    bl_idname = "edm.menu.object.context"
    bl_label = "EDM Object Properties"
    bl_options = { "REGUSTER", "UNDO" }

    def draw( self, context ):
        layout = self.layout
        target = context.object
        if target.type == "MESH":
            layout.label( text="Mesh" )
            layout.prop(target, "EDMRenderType" )
        
        if target.type == "EMPTY":
            layout.label( text="Empty" )
            layout.prop(target, "EDMEmptyType" )
        

def EDMObjectContextMenuSubMenuFunc( self, context ):
    self.layout.menu( EDMObjectContextMenuSubMenu.bl_idname )

class EDMObjectPanel(bpy.types.Panel):
    bl_idname = "OBJECT_PT_select"
    bl_label = "EDM"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "object"
    bl_options = {'DEFAULT_CLOSED'}
    
    @classmethod
    def poll(cls, context):
        return (context.object is not None)
        
    def draw_header(self, context):
        layout = self.layout
        #layout.label(text="My Select")
    
    def draw(self, context):
        layout = self.layout
        box = layout.box()
        #print(context.object.type)
        if context.object.type=='ARMATURE':
            box.prop(bpy.context.object.data, 'EDMAutoCalcBoxes')
            if bpy.context.object.data.EDMAutoCalcBoxes==False:
                box2=layout.box()
                box2.label(text="User Box:")
                row = box2.row(align = True)
                colleft=row.column(align=False)
                colleft.prop(bpy.context.object.data,'EDMUserBoxMin')
                colright=row.column(align=False)
                colright.prop(bpy.context.object.data,'EDMUserBoxMax')
                box3=layout.box()
                box3.label(text="Bounding Box:")
                row2 = box3.row(align = True)
                colleft2=row2.column(align=False)
                colleft2.prop(bpy.context.object.data,'EDMBoundingBoxMin')
                colright2=row2.column(align=False)
                colright2.prop(bpy.context.object.data,'EDMBoundingBoxMax')
        
        if context.object.type=='MESH':
            box.prop(bpy.context.object, 'EDMRenderType')
            type=bpy.context.object.EDMRenderType
            if type=='RenderNode' or type=='SkinNode':
                materialBox=layout.box()
                if len(context.object.material_slots)>0:
                    material=context.object.material_slots[0].material
                    materialBox.label(text="Material: "+material.name)
                    materialBox.prop(material, 'EDMMaterialType')
                    col = materialBox.column(align = True)
                    col.label(text="Diffuse colormap:")
                    col.prop(material,'EDMDiffuseMapName')
                    col.prop(material,'EDMDiffuseValue')
                    if material.EDMMaterialType=='Solid':
                        col.prop(material,'EDMUseAlpha')

                    #col.prop(material,'EDMDiffuseShift')
                    #materialBox.separator()
                    col = materialBox.column(align = True)
                    if material.EDMMaterialType=='transp_self_illu':
                        col.prop(material,'EDMSelfIllumination')
                        col.prop(material,'EDMSelfIlluminationArgument')
                    if material.EDMMaterialType=='self_illu':
                        col.prop(material,'EDMSelfIllumination')
                    if material.EDMMaterialType=='bano':
                        col.prop(material,'EDMSelfIllumination')
                    if material.EDMMaterialType=='Solid':
                        col.prop(material,'EDMUseNormalMap')
                        if material.EDMUseNormalMap:
                            col.prop(material,'EDMNormalMapName')
                            col.prop(material,'EDMNormalMapValue')
                    col = materialBox.column(align = True)
                    col.prop(material,'EDMReflectionValue')
                    col.prop(material,'EDMReflectionBlurring')
                    if material.EDMMaterialType=='Solid':
                        col.prop(material,'EDMUseSpecularMap')
                    col.prop(material,'EDMSpecularPower')
                    col.prop(material,'EDMSpecularFactor')
                    if material.EDMUseSpecularMap and material.EDMMaterialType=='Solid':
                        col.prop(material,'EDMSpecularMapName')
                        col.prop(material,'EDMSpecularMapValue')    
                else:
                    materialBox.label(text=context.object.name +" has no material")
        if context.object.type=='EMPTY':
            box.prop(bpy.context.object, 'EDMEmptyType')
            if bpy.context.object.EDMEmptyType=='FakeOmniLight':
                box.prop(bpy.context.object,'FakeLightP1')
                box.prop(bpy.context.object,'FakeLightScale')
                box.label(text="FakeOmniLightTexture:")
                box.prop(bpy.context.object,'FakeOmniLightTextureName')
                box.prop(bpy.context.object,'FakeLightUV1')
                box.prop(bpy.context.object,'FakeLightUV2')
                box.prop(bpy.context.object,'FakeLightShift')
            if bpy.context.object.EDMEmptyType=='Light':
                box.prop(bpy.context.object,'EDMLightColor')
                box.prop(bpy.context.object,'EDMLightBrightness')
                box.prop(bpy.context.object,'EDMLightDistance')
                box.prop(bpy.context.object,'EDMisSpot')
                if bpy.context.object.EDMisSpot:
                    box.prop(bpy.context.object,'EDMLightPhi')
                    box.prop(bpy.context.object,'EDMLightTheta')    
                
                
            
class ActionOptionPanel(bpy.types.Panel):
    bl_idname = "ACTION_PT_Option"
    bl_label = "EDM"
    bl_space_type = 'DOPESHEET_EDITOR'
    bl_region_type = 'UI'
    bl_context = "action"
    bl_options = {'DEFAULT_CLOSED'}
    
    @classmethod
    def poll(cls, context):
        if context.object is None:
            return False
        if context.object.animation_data is None:
            return False			
        if context.object.animation_data.action is None:
            return False		
        return True
        
    def draw_header(self, context):
        layout = self.layout
        #layout.label(text="My Select")
    
    def draw(self, context):
        layout = self.layout
        box = layout.box()
        if context.object.animation_data.action is not None:
            box.label(text=context.object.animation_data.action.name)
            box.prop(context.object.animation_data.action, 'exportToEDM')
            box.prop(context.object.animation_data.action, 'animationArgument')


