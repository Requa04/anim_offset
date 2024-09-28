import bpy
import random
import numpy as np
import mathutils

def anim_offset(data_to_offset, offset_mode, seed, 
               offset_amount, reset_strip, only_pos_offset, 
               context, dist_origin, reset_cache_offset, 
               curve_path, x_dist_only, y_dist_only, z_dist_only):
     
    active_collection = context.view_layer.active_layer_collection.collection

    def remove_empty_nla_track_if_found(active_collection):
        collection = active_collection
        for obj in collection.objects:
                animation_data = obj.animation_data
                if animation_data is not None:
                    nla_tracks = animation_data.nla_tracks
                    if animation_data and nla_tracks:
                        for track in nla_tracks:
                            if not track.strips:
                                animation_data.nla_tracks.remove(track)
    
    remove_empty_nla_track_if_found(active_collection) 
    
    def check_anim_data(active_collection):
        for obj in active_collection.objects:
            if obj.modifiers is not None or obj.animation_data is not None:
                return True
    
    has_animation_data = check_anim_data(active_collection)
    
    if has_animation_data != False:
    
        def has_nla_strips_in_collection(active_collection):
            collection = active_collection 
            for obj in collection.objects:
                if obj.animation_data and obj.animation_data.nla_tracks:
                    for track in obj.animation_data.nla_tracks:
                        if track.strips:
                            return True  
            return False
        
        if dist_origin is not None:
            dist_origin = dist_origin.location * mathutils.Vector((x_dist_only, y_dist_only, z_dist_only))
            print(dist_origin)
        
        match (data_to_offset, offset_mode, has_nla_strips_in_collection(active_collection), reset_strip, reset_cache_offset):
            case ("KEY0", "KEY0", _, _, _):
                for i, obj in enumerate(active_collection.objects, start=0):
                    action = obj.animation_data.action
                    random.seed(a=i+seed, version=2)
                    frame_offset = random.random()
                    frame_offset = np.interp(frame_offset, [0, 1], [-offset_amount, offset_amount])
                    frame_offset = frame_offset if not only_pos_offset else abs(frame_offset)

                    if action:  
                        for fcurve in action.fcurves:    
                            for keyframe in fcurve.keyframe_points:
                                keyframe.co.x += frame_offset
                                left_handle = keyframe.handle_left
                                right_handle = keyframe.handle_right
                                keyframe.handle_left = (left_handle[0] + frame_offset, left_handle[1])
                                keyframe.handle_right = (right_handle[0] + frame_offset, right_handle[1])

            case ("KEY1", "KEY0", False, _, _):
                for i, obj in enumerate(active_collection.objects, start=0):
                    action = obj.animation_data.action
                    random.seed(a=i+seed, version=2)
                    frame_offset = random.random()
                    frame_offset = np.interp(frame_offset, [0, 1], [-offset_amount, offset_amount])
                    frame_offset = frame_offset if not only_pos_offset else abs(frame_offset)

                    if action:
                        track = obj.animation_data.nla_tracks.new()
                        track.strips.new(action.name, int(action.frame_range[0]), action)
                        obj.animation_data.action = None
                        nla_track = obj.animation_data.nla_tracks[-1]
                        nla_strip = nla_track.strips[-1]
                        nla_strip.frame_start += frame_offset
                        nla_strip.frame_end += frame_offset
            
            case ("KEY1", "KEY1", False, _, _):
                objects_pos = []
                origin = []
                for obj in active_collection.objects: 
                    objects_pos.append(obj.location)
                    origin.append(dist_origin)

                vector_lengths = np.linalg.norm(np.array(objects_pos)-np.array(origin), axis=1)
                frame_offset = np.interp(vector_lengths, [np.min(vector_lengths), np.max(vector_lengths)], [0, offset_amount])

                for i, obj in enumerate(active_collection.objects, start=0): 
                    action = obj.animation_data.action
                    if action:  
                        track = obj.animation_data.nla_tracks.new()
                        track.strips.new(action.name, int(action.frame_range[0]), action)
                        obj.animation_data.action = None
                        nla_track = obj.animation_data.nla_tracks[-1]
                        nla_strip = nla_track.strips[-1] 
                        nla_strip.frame_start += frame_offset[i]
                        nla_strip.frame_end += frame_offset[i]

            case ("KEY1", _, True, True, _):
                for obj in active_collection.objects:
                    if obj.animation_data and obj.animation_data.nla_tracks:
                        for track in obj.animation_data.nla_tracks:
                            if track.strips:
                                min_start_frame = min(strip.frame_start for strip in track.strips)
                                offset = -min_start_frame
                                for strip in track.strips:
                                    strip.frame_start += offset
                                    strip.frame_end += offset

            case ("KEY1", "KEY0", True, False, _):
                for i, obj in enumerate(active_collection.objects, start=0):
                    random.seed(i+seed)
                    offset = random.random()
                    if obj.animation_data and obj.animation_data.nla_tracks:
                        for track in obj.animation_data.nla_tracks:
                            if track.strips:
                                for strip in track.strips:
                                    offset = np.interp(offset, [0, 1], [-offset_amount, offset_amount])
                                    offset = offset if not only_pos_offset else abs(offset)
                                    strip.frame_start += offset
                                    strip.frame_end += offset

            case ("KEY1", "KEY1", True, False, _):
                objects_pos = []
                origin = []
                for obj in active_collection.objects: 
                    objects_pos.append(obj.location)
                    origin.append(dist_origin)

                if origin is not None:
                    
                    vector_lengths = np.linalg.norm(np.array(objects_pos)-np.array(origin), axis=1)
                    frame_offset = np.interp(vector_lengths, [np.min(vector_lengths), np.max(vector_lengths)], [0, offset_amount])
                    
                else:
                    raise Exception("This is a custom exception message!")
                    
                for i, obj in enumerate(active_collection.objects, start=0):    
                    if obj.animation_data and obj.animation_data.nla_tracks:
                        for track in obj.animation_data.nla_tracks:
                            if track.strips:
                                for strip in track.strips:
                                    strip.frame_start += frame_offset[i]
                                    strip.frame_end += frame_offset[i]

            case ("KEY2", "KEY0", _, _, False):
                for i, obj in enumerate(active_collection.objects, start=0):
                    random.seed(a=i+seed, version=2)
                    offset = random.random()
                    offset = round(np.interp(offset, [0, 1], [-offset_amount, offset_amount]))

                    for mod in obj.modifiers:
                        if mod.type == "MESH_SEQUENCE_CACHE" and mod.cache_file:
                            mod.cache_file.frame_offset = offset

            case ("KEY2", "KEY1", _, _, False):
                objects_pos = []
                origin = []
                for obj in active_collection.objects: 
                    objects_pos.append(obj.location)
                    origin.append(dist_origin)

                vector_lengths = np.linalg.norm(np.array(objects_pos)-np.array(origin), axis=1)
                frame_offset = np.interp(vector_lengths, [np.min(vector_lengths), np.max(vector_lengths)], [0, offset_amount])

                for i, obj in enumerate(active_collection.objects, start=0):
                    for mod in obj.modifiers:
                        if mod.type == "MESH_SEQUENCE_CACHE" and mod.cache_file:
                            mod.cache_file.frame_offset = frame_offset[i]

            case ("KEY2", _, _, _, True):
                for obj in active_collection.objects:
                    for mod in obj.modifiers:
                        if mod.type == "MESH_SEQUENCE_CACHE" and mod.cache_file:
                            mod.cache_file.frame_offset = 0

            case("KEY0", "KEY2", _, _, _):           
                
                def sample_nearest_curve_point(curve_object, sample_object):
        
                    if curve_object.type != "CURVE":
                        print("Selected object is not a curve.")
                        return None
                        
                    curve_data = curve_object.data
                    target_location = sample_object.location
                    
                    spline = curve_data.splines[0]
                    spline_type = spline.type
                    
                    point_factor = None
                    min_distance = float("inf")
                        
                    match spline_type:
                        case "BEZIER":  
                             spline_points = spline.bezier_points
                             spline_iterable = enumerate(spline_points, start=0)
                             for i, point in spline_iterable:
                                distance = (target_location - point.co).length
                                if distance < min_distance:
                                    min_distance = distance
                                    point_factor = float(i)/len(spline_points)
                        case "POLY":  
                            spline_points = spline.points
                            spline_iterable = enumerate(spline_points, start=0)
                            for i, point in spline_iterable:
                                distance = (target_location - point.co.xyz).length
                                if distance < min_distance:
                                    min_distance = distance
                                    point_factor = float(i)/len(spline_points)
                        case "NURBS":  
                            spline_points = spline.points
                            spline_iterable = enumerate(spline_points, start=0)
                            for i, point in spline_iterable:
                                distance = (target_location - point.co.xyz).length
                                if distance < min_distance:
                                    min_distance = distance
                                    point_factor = float(i)/len(spline_points)
                        case _:
                            print("Select Spline type object")
                        
                    return point_factor, min_distance    

                offset_value = []
                objects = active_collection.objects
                
                for obj in objects:
                    if curve_path is not None:
                        point_factor = sample_nearest_curve_point(curve_path, obj)[0]
                        offset_value.append(point_factor)
                    else:
                        raise Exception("No curve object selected")
                
                np_offset_value = np.array(offset_value)
                np_offset_value = np.interp(np_offset_value, [np.min(np_offset_value), np.max(np_offset_value)], [0, offset_amount])

                for i, obj in enumerate(objects, start=0):
                    action = obj.animation_data.action

                    if action:  
                        for fcurve in action.fcurves:    
                            for keyframe in fcurve.keyframe_points:
                                
                                keyframe.co.x += np_offset_value[i]
                                
                                left_handle = keyframe.handle_left
                                right_handle = keyframe.handle_right
                                
                                keyframe.handle_left = (left_handle[0] + np_offset_value[i], left_handle[1])
                                keyframe.handle_right = (right_handle[0] + np_offset_value[i], right_handle[1])
                                                 
            case("KEY1", "KEY2", False, False, _):           
                def sample_nearest_curve_point(curve_object, sample_object):

                    if curve_object.type != "CURVE":
                        print("Selected object is not a curve.")
                        return None
                        
                    curve_data = curve_object.data
                    target_location = sample_object.location
                    
                    spline = curve_data.splines[0]
                    spline_type = spline.type
                    
                    point_factor = None
                    min_distance = float("inf")
                        
                    match spline_type:
                        case "BEZIER":  
                             spline_points = spline.bezier_points
                             spline_iterable = enumerate(spline_points, start=0)
                             for i, point in spline_iterable:
                                distance = (target_location - point.co).length
                                if distance < min_distance:
                                    min_distance = distance
                                    point_factor = float(i)/len(spline_points)
                        case "POLY":  
                            spline_points = spline.points
                            spline_iterable = enumerate(spline_points, start=0)
                            for i, point in spline_iterable:
                                distance = (target_location - point.co.xyz).length
                                if distance < min_distance:
                                    min_distance = distance
                                    point_factor = float(i)/len(spline_points)
                        case "NURBS":  
                            spline_points = spline.points
                            spline_iterable = enumerate(spline_points, start=0)
                            for i, point in spline_iterable:
                                distance = (target_location - point.co.xyz).length
                                if distance < min_distance:
                                    min_distance = distance
                                    point_factor = float(i)/len(spline_points)
                        case _:
                            print("Select Spline type object")
                        
                    return point_factor, min_distance    

                offset_value = []
                objects = active_collection.objects
                
                for obj in objects:
                    if curve_path is not None:
                        point_factor = sample_nearest_curve_point(curve_path, obj)[0]
                        offset_value.append(point_factor)
                    else:
                        raise Exception("No curve object selected")
                
                np_offset_value = np.array(offset_value)
                np_offset_value = np.interp(np_offset_value, [np.min(np_offset_value), np.max(np_offset_value)], [0, offset_amount])

                for i, obj in enumerate(objects, start=0):
                    action = obj.animation_data.action
                    random.seed(a=i+seed, version=2)
                    frame_offset = random.random()
                    frame_offset = np.interp(frame_offset, [0, 1], [-offset_amount, offset_amount])
                    frame_offset = frame_offset if not only_pos_offset else abs(frame_offset)

                    if action:
                        track = obj.animation_data.nla_tracks.new()
                        track.strips.new(action.name, int(action.frame_range[0]), action)
                        obj.animation_data.action = None
                        nla_track = obj.animation_data.nla_tracks[-1]
                        nla_strip = nla_track.strips[-1]
                        nla_strip.frame_start += np_offset_value[i]
                        nla_strip.frame_end += np_offset_value[i]
                                   
            case("KEY1", "KEY2", True, False, _):           
                
                def sample_nearest_curve_point(curve_object, sample_object):
                    if curve_object.type != "CURVE":
                        print("Selected object is not a curve.")
                        return None
                        
                    curve_data = curve_object.data
                    target_location = sample_object.location
                    
                    spline = curve_data.splines[0]
                    spline_type = spline.type
                    
                    point_factor = None
                    min_distance = float("inf")
                        
                    match spline_type:
                        case "BEZIER":  
                             spline_points = spline.bezier_points
                             spline_iterable = enumerate(spline_points, start=0)
                             for i, point in spline_iterable:
                                distance = (target_location - point.co).length
                                if distance < min_distance:
                                    min_distance = distance
                                    point_factor = float(i)/len(spline_points)
                        case "POLY":  
                            spline_points = spline.points
                            spline_iterable = enumerate(spline_points, start=0)
                            for i, point in spline_iterable:
                                distance = (target_location - point.co.xyz).length
                                if distance < min_distance:
                                    min_distance = distance
                                    point_factor = float(i)/len(spline_points)
                        case "NURBS":  
                            spline_points = spline.points
                            spline_iterable = enumerate(spline_points, start=0)
                            for i, point in spline_iterable:
                                distance = (target_location - point.co.xyz).length
                                if distance < min_distance:
                                    min_distance = distance
                                    point_factor = float(i)/len(spline_points)
                        case _:
                            print("Select Spline type object")
                        
                    return point_factor, min_distance    

                offset_value = []
                objects = active_collection.objects
                
                for obj in objects:
                    if curve_path is not None:
                        point_factor = sample_nearest_curve_point(curve_path, obj)[0]
                        offset_value.append(point_factor)
                    else:
                        raise Exception("No curve object selected")
                
                np_offset_value = np.array(offset_value)
                np_offset_value = np.interp(np_offset_value, [np.min(np_offset_value), np.max(np_offset_value)], [0, offset_amount])

                for i, obj in enumerate(active_collection.objects, start=0):    
                    if obj.animation_data and obj.animation_data.nla_tracks:
                        for track in obj.animation_data.nla_tracks:
                            if track.strips:
                                for strip in track.strips:
                                    strip.frame_start += np_offset_value[i]
                                    strip.frame_end += np_offset_value[i]
                                                                    
            case("KEY2", "KEY2", _, _, False):           
                
                def sample_nearest_curve_point(curve_object, sample_object):
                    if curve_object.type != "CURVE":
                        print("Selected object is not a curve.")
                        return None
                        
                    curve_data = curve_object.data
                    target_location = sample_object.location
                    
                    spline = curve_data.splines[0]
                    spline_type = spline.type
                    
                    point_factor = None
                    min_distance = float("inf")
                        
                    match spline_type:
                        case "BEZIER":  
                             spline_points = spline.bezier_points
                             spline_iterable = enumerate(spline_points, start=0)
                             for i, point in spline_iterable:
                                distance = (target_location - point.co).length
                                if distance < min_distance:
                                    min_distance = distance
                                    point_factor = float(i)/len(spline_points)
                        case "POLY":  
                            spline_points = spline.points
                            spline_iterable = enumerate(spline_points, start=0)
                            for i, point in spline_iterable:
                                distance = (target_location - point.co.xyz).length
                                if distance < min_distance:
                                    min_distance = distance
                                    point_factor = float(i)/len(spline_points)
                        case "NURBS":  
                            spline_points = spline.points
                            spline_iterable = enumerate(spline_points, start=0)
                            for i, point in spline_iterable:
                                distance = (target_location - point.co.xyz).length
                                if distance < min_distance:
                                    min_distance = distance
                                    point_factor = float(i)/len(spline_points)
                        case _:
                            print("Select Spline type object")
                        
                    return point_factor, min_distance    

                offset_value = []
                objects = active_collection.objects
                
                for obj in objects:
                    if curve_path is not None:
                        point_factor = sample_nearest_curve_point(curve_path, obj)[0]
                        offset_value.append(point_factor)
                    else:
                        raise Exception("No curve object selected")
                
                np_offset_value = np.array(offset_value)
                np_offset_value = np.interp(np_offset_value, [np.min(np_offset_value), np.max(np_offset_value)], [0, offset_amount])

                for i, obj in enumerate(active_collection.objects, start=0):
                    for mod in obj.modifiers:
                        if mod.type == "MESH_SEQUENCE_CACHE" and mod.cache_file:
                            mod.cache_file.frame_offset = np_offset_value[i]
                                  
    else:
        pass


class my_props(bpy.types.PropertyGroup):
    
    props = bpy.props
    
    offset_mode: props.EnumProperty(name="Offset Mode", default="KEY0", 
                                    items=[("KEY0", "Random", ""),
                                    ("KEY1", "Empty Distance", ""),
                                    ("KEY2", "Curve Distance", "")])
   
    seed: props.IntProperty(name="Seed", default=0, min=0, max=1000)
    offset_amount: props.IntProperty(name="Offset Amount", default=200, min=0, max=10_000)
    reset_strip: props.BoolProperty(name="Reset Strip", default=False, description="")  
    reset_cache_offset: props.BoolProperty(name="Reset Cache Offset", default=False, description="")
    only_pos_offset: props.BoolProperty(name="Only Positive Offset ", default=False)  
    
    data_to_offset: props.EnumProperty(items = [("KEY0", 'Keyframes', ""), 
                                                ("KEY1", "NLA Strips", ""), 
                                                ("KEY2", "Mesh Sequence Cache", "")],
                                                name = "Data To Offset", default="KEY0")                
    
    dist_origin: props.PointerProperty(type=bpy.types.Object, name="Empty", description="")
    curve_path: props.PointerProperty(type=bpy.types.Object, name="Curve", description="")
    x_dist_only: props.BoolProperty(name="X", default=True, description="")
    y_dist_only: props.BoolProperty(name="Y", default=True, description="")
    z_dist_only: props.BoolProperty(name="Z", default=True, description="")  

class anim_offset_op(bpy.types.Operator):
    """Run the operator with current parameters"""
    
    bl_idname = "anim.anim_offset"
    bl_label = "Anim Offset"
    bl_options = {"REGISTER", "UNDO"}   
    
    def execute(self, context):
        
        op_context = context
        props = op_context.scene.my_props
        
        anim_offset(props.data_to_offset, 
        props.offset_mode, 
        props.seed, 
        props.offset_amount, 
        props.reset_strip, 
        props.only_pos_offset, 
        op_context, 
        props.dist_origin, 
        props.reset_cache_offset,
        props.curve_path,
        props.x_dist_only,
        props.y_dist_only,
        props.z_dist_only)
        
        return {"FINISHED"}
    
class Anim_Offset_Panel(bpy.types.Panel):
    
    bl_label = "Anim Offset"
    blidname = "Anim_Offset_Panel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Anim Offset"

    def draw(self, context):
        
        layout = self.layout
        props = context.scene.my_props
        layout.prop(props, "offset_mode")
        row = layout.row()
        
        if props.offset_mode != "KEY0":
            row.prop(props, "x_dist_only")
            row.prop(props, "y_dist_only")
            row.prop(props, "z_dist_only")
        
        if props.offset_mode == "KEY1":
            layout.prop(props, "dist_origin")
    
        if props.offset_mode == "KEY2":    
            layout.prop(props, "curve_path")

        layout.prop(props, "seed")
        layout.prop(props, "offset_amount")
        layout.prop(props, "only_pos_offset")
        layout.prop(props, "data_to_offset")
        
        if props.data_to_offset == "KEY1":
            layout.prop(props, "reset_strip")
        
        if props.data_to_offset == "KEY2":
            layout.prop(props, "reset_cache_offset")
        
        operator = layout.operator("anim.anim_offset", text="Run")
        
classes = [my_props, anim_offset_op, Anim_Offset_Panel] 

def register():
    for i in classes:
        bpy.utils.register_class(i)
        bpy.types.Scene.my_props = bpy.props.PointerProperty(type = my_props)

def unregister():
    for i in classes:
        bpy.utils.unregister_class(i)
        del bpy.types.Scene.my_props
        
if __name__ == "__main__":
    register()
