from ovito.io import import_file
from ovito.modifiers import ConstructSurfaceModifier, InvertSelectionModifier, DeleteSelectedModifier
import numpy as np
from lammpy.Sphere import Sphere


class Surface:

  def __init__(self, sphere):

    if isinstance(sphere, Sphere):
      self.inputFileType = ""
      self.sphere_input = sphere.sphere_pipeline
      self.filename = sphere.outfile.split('.')[0]+".surface"
    elif isinstance(sphere, str):
      self.inputFileType = sphere.split('.')[1]
      self.sphere_input = import_file(sphere)
      self.filename = sphere.split('.')[0]+".surface"
      
    else:
      raise ValueError('Surface must be initialized with either a Sphere object or a sphere file.')

    if self.inputFileType == "surface":
      self.particle_data, self.surface_volume = self.read_surface_file(sphere)
    else:
      self.particle_data, self.surface_volume = self.calc_surface_from_pipeline(self.sphere_input)


  def calc_surface_from_pipeline(self,pipeline):
      print("Obtaining Surface...")
      pipeline.modifiers.append(ConstructSurfaceModifier(
          select_surface_particles=True,
          identify_regions = True))
      pipeline.modifiers.append(InvertSelectionModifier())
      pipeline.modifiers.append(DeleteSelectedModifier())
      data_0 = pipeline.compute(0)
      volume = data_0.attributes['ConstructSurfaceMesh.filled_volume']

      

      xyz = list(data_0.particles['Position'])

      for i in range(len(xyz)):
          xyz[i] = list(xyz[i])

      ids = list(data_0.particles['Particle Identifier'])

      all_data = []

      for i in range(len(ids)):
          all_data.append([ids[i]]+xyz[i])

      all_data = np.array(all_data)
      print("Complete.")
      return all_data,volume


  def adjust_com(self):

      surface = self.particle_data.T
      x_ave = np.average(surface[1])
      y_ave = np.average(surface[2])
      z_ave = np.average(surface[3])
      surface[1] -= x_ave
      surface[2] -= y_ave
      surface[3] -= z_ave
      self.particle_data = surface.T


  def read_surface_file(self, file):
      print("Reading surface from file...")
      positions = []
      with open(file,"r") as f:  
           
          for line in f.readlines():
              line = line.split()
              if len(line) == 4:
                  positions.append(line)
              else:
                if "Volume" in line[-1]:
                  volume = float(line[-1].split(':')[-1])
      print("Completed surface.")
      return np.array(positions).astype(float), volume

  