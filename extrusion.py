from madcad import text, extrusion, scale, vec3, icosphere, intersection, inflate, union
from arrex import typedlist
import trimesh
import numpy as np
import os

def map_to_sphere_surface(points, radius):
    """Maps the 2D points on the tangent plane to 3D sphere surface."""
    # Normalize the points to be on the surface of the sphere
    norm = np.linalg.norm(points, axis=1)  # Find the magnitude of each point
    scaled_points = points * (radius / norm[:, np.newaxis])  # Scale each point to the sphere's radius
    return scaled_points

def find_font_file(fontname):
    import pygame.freetype
    pygame.init()
    try:
        font = pygame.freetype.SysFont(fontname, 1)
        return font.path
    except:
        return None

def get_carved_sphere(letter, font, size, sphere_radius, sphere_center, resolution, extrusion_depth):
    from madcad import text, difference
    print (f'{font=}')
    shape1 = icosphere( vec3(0,0,0), sphere_radius, resolution=['div',resolution])
    #shape2 = icosphere( vec3(0,0,0), sphere_radius*(1-extrusion_depth), resolution=['div',resolution])
    label = text.text(letter,
                      font=font, 
                      size=size*sphere_radius, #scale according to sphere radius
                      fill=True,
                      align=('center', 'center') ,
                      resolution=['div', resolution*10]) 
    points = np.array([p.to_list() for p in label.points])
    points[:,-1] = 0
    #print (points.shape)
    letter_center = np.average(points, axis=0)
    label = label.transform(vec3(-letter_center + [0, 0, sphere_radius])) #north pole of the r-sphere
    points = map_to_sphere_surface(np.array([p.to_list() for p in label.points]), radius=sphere_radius)
    #points = np.array([p.to_list() for p in label.points])
    label.points = typedlist(vec3(p) for p in points)
    label = extrusion(label, vec3(0., 0., extrusion_depth), 0.5)
    #label = intersection(
	#	    label,
    #        inflate(shape1, extrusion_depth*0.5),
	#	)
    carved_shape = difference(shape1, label).finish()
    #carved_shape = union(union(shape1, label), inflate(shape2, extrusion_depth)).finish()
    #carved_shape = label
    carved_shape = carved_shape.transform(vec3(sphere_center))
    #show([carved_shape])
    #carved_shape.show()   
    vertices, faces = carved_shape.points, carved_shape.faces
    vertices = [p.to_list() for p in vertices]
    faces = [f.to_list() for f in faces]
    carved_shape = trimesh.Trimesh(vertices=vertices, faces=faces)

    #carved_shape.show()
    return carved_shape


if __name__ == '__main__' :
    import sys
    sphere_center = np.array([1.0, 1.0, 1.0])  # Center of the sphere
    sphere_radius = 2.0  # Radius of the sphere
    extrusion_depth = 0.5  # Depth of extrusion
    letter = sys.argv[1]
    scale = 1
    resolution = 10
    fontname = sys.argv[2] #'Arial'
    font = find_font_file(fontname)
    if not font.endswith('.ttf'):
        print (f'Error: font={fontname} file={font} extension is not ttf!\nNot compatible with madcad\nUsing default font instead!')
        font = None
    carved_sphere = get_carved_sphere(letter, font, scale, sphere_radius, sphere_center, resolution, extrusion_depth)
    carved_sphere.show()



