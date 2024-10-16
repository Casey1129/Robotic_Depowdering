from functools import reduce
from xml.etree import ElementTree as et
from xml.dom import minidom
import numpy as np
import pymeshlab as ml
import trimesh
import json
import os
import shutil
import rclpy
import rclpy.node
from .constants import ROBOTIC_DEPOWDERING_TMP_DIR

def get_obj_urdf(name, m=1.0, s=1.0):
    robot = et.Element('robot')
    robot.set('name', name)
    link = et.SubElement(robot, 'link')
    link.set('name', name)
    contact = et.SubElement(link, 'contact')
    lateral_friction = et.SubElement(contact, 'lateral_friction')
    lateral_friction.set('value', '1.0')
    rolling_friction = et.SubElement(contact, 'rolling_friction')
    rolling_friction.set('value', '1.0')
    inertia_scaling = et.SubElement(contact, 'inertia_scaling')
    inertia_scaling.set('value', '3.0')
    contact_cdm = et.SubElement(contact, 'contact_cdm')
    contact_cdm.set('value', '0.0')
    contact_erp = et.SubElement(contact, 'contact_erp')
    contact_erp.set('value', '1.0')
    inertial = et.SubElement(link, 'inertial')
    origin = et.SubElement(inertial, 'origin')
    origin.set('rpy', '0 0 0')
    origin.set('xyz', '0 0 0')
    mass = et.SubElement(inertial, 'mass')
    mass.set('value', '{}'.format(m))
    inertia = et.SubElement(inertial, 'inertia')
    inertia.set('ixx', '0')
    inertia.set('ixy', '0')
    inertia.set('ixz', '0')
    inertia.set('iyy', '0')
    inertia.set('iyz', '0')
    inertia.set('izz', '0')
    visual = et.SubElement(link, 'visual')
    origin = et.SubElement(visual, 'origin')
    origin.set('rpy', '0 0 0')
    origin.set('xyz', '0 0 0')
    geometry = et.SubElement(visual, 'geometry')
    mesh = et.SubElement(geometry, 'mesh')
    mesh.set('filename', name + '_vis.obj')
    mesh.set('scale', '{} {} {}'.format(s, s, s))
    material = et.SubElement(visual, 'material')
    material.set('name', 'blockmat')
    color = et.SubElement(material, 'color')
    color.set('rgba', '1.0 1.0 1.0 1.0')
    collision = et.SubElement(link, 'collision')
    origin = et.SubElement(collision, 'origin')
    origin.set('rpy', '0 0 0')
    origin.set('xyz', '0 0 0')
    geometry = et.SubElement(collision, 'geometry')
    mesh = et.SubElement(geometry, 'mesh')
    mesh.set('filename', name + '_col.obj')
    mesh.set('scale', '{} {} {}'.format(s, s, s))
    xml_str = minidom.parseString(et.tostring(robot)).toprettyxml(indent='  ')
    return xml_str


def dexnet(mesh_path, output):
    ms = ml.MeshSet()
    print(os.path.join(mesh_path))
    for obj_name in os.listdir(os.path.join(mesh_path)):
        print("Object:", obj_name)
        obj_name = obj_name[:-4]
        obj_path = os.path.join(output, obj_name)
        if not os.path.exists(obj_path):
            os.makedirs(obj_path)
        ms.load_new_mesh(os.path.join(mesh_path, obj_name + '.obj'))
        ms.apply_filter('meshing_invert_face_orientation', forceflip=False)
        ms.save_current_mesh(os.path.join(obj_path, obj_name + '.obj'))
        ms.save_current_mesh(os.path.join(obj_path, obj_name + '_vis.obj'))
        # ms.apply_filter('generate_convex_hull')
        ms.save_current_mesh(os.path.join(obj_path, obj_name + '_col.obj'))
        xml_str = get_obj_urdf(obj_name, m=1.0, s=1.0)
        with open(os.path.join(obj_path, obj_name + '.urdf'), 'w') as f:
            f.write(xml_str)


def kit(mesh_path, output):
    ms = ml.MeshSet()
    for obj_name in os.listdir(os.path.join(mesh_path)):
        print(obj_name)
        obj_name = obj_name[:-4]
        obj_path = os.path.join(output, obj_name)
        if not os.path.exists(obj_path):
            os.makedirs(obj_path)
        ms.load_new_mesh(os.path.join(mesh_path, obj_name + '.obj'))
        ms.apply_filter('meshing_invert_face_orientation', forceflip=False)
        # ms.apply_filter('transform_align_to_principal_axis')
        ms.save_current_mesh(os.path.join(obj_path, obj_name + '.obj'))
        ms.save_current_mesh(os.path.join(obj_path, obj_name + '_col.obj'))
        ms.save_current_mesh(os.path.join(obj_path, obj_name + '_vis.obj'))
        xml_str = get_obj_urdf(obj_name, m=1.0, s=1.0)
        with open(os.path.join(obj_path, obj_name + '.urdf'), 'w') as f:
            f.write(xml_str)


def block(mesh_path, output):
    ms = ml.MeshSet()
    print(os.path.join(mesh_path))
    for obj_name in os.listdir(mesh_path):
        if obj_name[-4:] != ".obj":
            continue
        print("Object", obj_name)
        obj_name = obj_name[:-4]
        obj_path = os.path.join(output, obj_name)
        if not os.path.exists(obj_path):
            os.makedirs(obj_path)
        ms.load_new_mesh(os.path.join(mesh_path, obj_name + '.obj'))
        # ms.apply_filter('meshing_invert_face_orientation', forceflip=False)
        # ms.apply_filter('transform_align_to_principal_axis')
        ms.save_current_mesh(os.path.join(obj_path, obj_name + '_col.obj'))
        ms.save_current_mesh(os.path.join(obj_path, obj_name + '_vis.obj'))
        ms.apply_filter('generate_resampled_uniform_mesh', cellsize=ml.Percentage(3))
        ms.apply_filter('meshing_remove_connected_component_by_diameter')
        ms.apply_filter('apply_coord_laplacian_smoothing_surface_preserving', angledeg=10, iterations=10)
        ms.save_current_mesh(os.path.join(obj_path, obj_name + '.obj'))
        xml_str = get_obj_urdf(obj_name, m=1.0, s=1.0)
        with open(os.path.join(obj_path, obj_name + '.urdf'), 'w') as f:
            f.write(xml_str)


def egad(mesh_path, output):
    ms = ml.MeshSet()
    for obj_name in os.listdir(os.path.join(mesh_path)):
        print(obj_name)
        obj_name = obj_name[:-4]
        obj_path = os.path.join(output, obj_name)
        if not os.path.exists(obj_path):
            os.makedirs(obj_path)
        ms.load_new_mesh(os.path.join(mesh_path, obj_name + '.obj'))
        ms.apply_filter('meshing_invert_face_orientation', forceflip=False)
        # ms.apply_filter('transform_align_to_principal_axis')
        ms.apply_filter('transform_translate_center_set_origin', traslmethod=2)
        ms.save_current_mesh(os.path.join(obj_path, obj_name + '.obj'))
        ms.apply_filter('simplification_quadric_edge_collapse_decimation')
        ms.apply_filter('simplification_quadric_edge_collapse_decimation')
        ms.save_current_mesh(os.path.join(obj_path, obj_name + '_col.obj'))
        ms.save_current_mesh(os.path.join(obj_path, obj_name + '_vis.obj'))
        gm = ms.apply_filter('compute_geometric_measures')
        bbox_volume = ms.current_mesh().bounding_box().dim_x() * ms.current_mesh().bounding_box().dim_y() * ms.current_mesh().bounding_box().dim_z()
        m = bbox_volume * 137
        xml_str = get_obj_urdf(obj_name, m)
        with open(os.path.join(obj_path, obj_name+'.urdf'), 'w') as f:
            f.write(xml_str)


def primitive(mesh_path, output):
    with open('config/primitives.json', 'r') as f:
        shape_cfg = json.load(f)
    for shape_type in shape_cfg.keys():
        curr_shape = shape_cfg[shape_type]
        shape_type = shape_type.split('#')[0]
        for stride in range(curr_shape['num_stride']):
            scale_x = curr_shape['x'] + curr_shape['stride_x'] * stride
            scale_y = curr_shape['y'] + curr_shape['stride_y'] * stride
            scale_z = curr_shape['z'] + curr_shape['stride_z'] * stride
            folder = shape_type + '#{:.3f}#{:.3f}#{:.3f}'.format(scale_x, scale_y, scale_z)
            output_path = os.path.join(output, folder)
            if os.path.exists(output_path) and len(os.listdir(output_path)) != 0:
                print(folder + ' exists.')
                continue
            else:
                os.makedirs(output_path)
            mesh_path = os.path.join(mesh_path, shape_type)
            for mesh_name in os.listdir(mesh_path):
                mesh = trimesh.load_mesh(os.path.join(mesh_path, mesh_name))
                mesh.apply_scale((scale_x, scale_y, scale_z))
                mesh.visual = trimesh.visual.ColorVisuals()
                strings = mesh_name.split('_')
                mesh_name = '_'.join([folder, strings[-1]]) if len(strings) == 2 else folder + '.obj'
                mesh.export(os.path.join(output_path, mesh_name))
            xml_str = get_obj_urdf(mesh_name)
            with open(os.path.join(output_path, folder + '.urdf'), 'w') as f:
                f.write(xml_str)


def google_16k(folder_path, output):
    ms = ml.MeshSet()
    for obj_name in os.listdir(os.path.join(folder_path)):
        print(obj_name)
        mesh_path = os.path.join(folder_path, obj_name, 'google_16k', 'textured.obj')
        obj_path = os.path.join(output, obj_name)
        if not os.path.exists(obj_path):
            os.makedirs(obj_path)
        ms.load_new_mesh(mesh_path)
        ms.save_current_mesh(os.path.join(obj_path, obj_name + '_vis.obj'))
        ms.meshing_decimation_quadric_edge_collapse_with_texture()
        ms.meshing_decimation_quadric_edge_collapse_with_texture()
        ms.meshing_decimation_quadric_edge_collapse_with_texture()
        ms.save_current_mesh(os.path.join(obj_path, obj_name + '_col.obj'))
        ms.save_current_mesh(os.path.join(obj_path, obj_name + '.obj'))
        xml_str = get_obj_urdf(obj_name, m=1.0, s=1.0)
        with open(os.path.join(obj_path, obj_name + '.urdf'), 'w') as f:
            f.write(xml_str)


def main():
    rclpy.init()
    this_node = rclpy.node.Node('mesh_processing')

    mesh_path_param_name = 'mesh_path'
    output_path_param_name = 'output_path'


    this_node.declare_parameter(mesh_path_param_name, ROBOTIC_DEPOWDERING_TMP_DIR + 'meshes')
    this_node.declare_parameter(output_path_param_name, ROBOTIC_DEPOWDERING_TMP_DIR + 'meshes_output')

    mesh_path = this_node.get_parameter(mesh_path_param_name).get_parameter_value().string_value
    output_path = this_node.get_parameter(output_path_param_name).get_parameter_value().string_value
    print(output_path)
    
    if os.path.exists(output_path):
        shutil.rmtree(output_path)
    os.makedirs(output_path)
    
    block(mesh_path, output_path)

if __name__ == '__main__':
    main()