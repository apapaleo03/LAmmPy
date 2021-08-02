from itertools import permutations
from Surface import Surface
import numpy as np
from astropy.coordinates import cartesian_to_spherical, spherical_to_cartesian

def write_xyz(input, filename,lattice:tuple, origin:str, columns:list):
    if isinstance(input, Surface):
        data = input.particle_data.astype(str)
        filename = input.filename
        volume = str(input.surface_volume)
    else:
      data = input.astype(str) 
      volume = ""
    header = generate_header(lattice, origin, columns, volume)

    with open(filename,'w') as f:
        f.write(f"{len(data)}\n")
        f.write(header+"\n")
        for atom in data:
            f.write(' '.join(atom))
            f.write("\n")
    
def generate_header(lattice:tuple, origin:str, columns:list, volume = "") -> str:

    if not isinstance(lattice,tuple):
        raise TypeError('Parameter "Lattice" must be of type "tuple".')
    lattice_desc = f'"Lattice={lattice[0]} 0.0 0.0 0.0 {lattice[1]} 0.0 0.0 0.0 {lattice[2]} "'
    if origin == "center":
        origin_desc = f'Origin="-{lattice[0]/2} -{lattice[1]/2} -{lattice[2]/2} "'
    elif origin == "corner":
        origin_desc = f'"Origin=0.0 0.0 0.0" '
    else:
        raise TypeError('Parameter "origin" must be either "center" or "corner".')


    labels = [label.split('.')[0] for label in columns]
    label_cat = {label : None for label in labels}.keys()
    properties = "Properties="
    for label in label_cat:
        properties += parse_column_name(label) + str(labels.count(label))+":"
    properties = properties[:-1]

    header = lattice_desc+origin_desc+properties + f" Volume:{volume}"

    

    return header

def parse_column_name(name: str) -> str :
    if name.lower() == "particle identifier":
        return "id:I:"
    elif name.lower() == "particle type":
        return "species:S:"
    elif name.lower() == "position":
        return "pos:R:"
    elif name.lower() == "color":
        return "color:R:"
    else:
        return f"{name}:R:"

def combine_surfaces(*args):
    surfaces = []
    for arg in args:
        if not isinstance(arg, Surface):
            raise TypeError('Input argunenbts must be of type "Surface"')
        surfaces.append(arg.particle_data)
    colors = [(0,0,0)] + list(set(permutations([0,0,1])))+list(set(permutations([0,1,1])))
    total = []
    i = 0
    for surface, color  in zip(surfaces, colors):
        for coords in surface:
            x,y,z = coords[1:4]
            total.append([i,x,y,z,color[0],color[1],color[2]])
            i+=1
    return np.asarray(total)

def find_surface_difference(positions_1, positions_2):
    difference = []
    diffs = []
    for dims in positions_1:

        d2 = positions_2[np.where(((positions_2[:,1] == dims[1])) & (positions_2[:,2] == dims[2]))]

        if len(d2) == 0:
            continue
        r2 = d2[0][0]

        diff = r2 - dims[0]
        diffs.append(diff)
        new_val = np.hstack(([100],dims[1:]))
        cart_val = np.hstack((spherical_to_cartesian_(new_val[0],new_val[1],new_val[2]),diff))
        difference.append(cart_val)
    return np.array(difference)    

def round_to(val, base):
    return base * np.around(val/base,0)

def hash_angles(arr):
    hashed = []
    for theta,phi in zip(arr[1],arr[2]):
        hashed.append(hash((theta,phi)))
    hashed = np.array(hashed)
    return np.vstack((arr,np.array(hashed)))

def cartesian_to_spherical_and_round(x,y,z, prec):

    vals = cartesian_to_spherical(x,y,z)
    r = vals[0].value
    lat = round_to(vals[1].value * 180/np.pi,prec)
    long = round_to(vals[2].value * 180/np.pi,prec)

    return np.array([r,lat,long])

def spherical_to_cartesian_(r,lat,long):


    cart = spherical_to_cartesian(r,lat*np.pi/180,long*np.pi/180)
    return np.array([cart[0].value,cart[1].value,cart[2].value]).T

def find_change(surface_1, surface_2):
    print("Calculating difference between surfaces...")
    surface_1_cart = cartesian_to_spherical_and_round(surface_1.particle_data[:,1],surface_1.particle_data[:,2], surface_1.particle_data[:,3],3)
    surface_1_hash = hash_angles(surface_1_cart)


    surface_2_cart = cartesian_to_spherical_and_round(surface_2.particle_data[:,1],surface_2.particle_data[:,2], surface_2.particle_data[:,3],3)
    surface_2_hash = hash_angles(surface_2_cart)

    print("Completed.")
    return find_surface_difference(surface_1_hash.T, surface_2_hash.T)