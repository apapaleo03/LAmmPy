from ovito.io import import_file, export_file
from ovito.modifiers import ExpressionSelectionModifier, DeleteSelectedModifier

class Sphere:

  def __init__(self,file, identifier, cutoff):
    self.filename = file
    self.identifier = identifier
    self.cutoff = cutoff
    self.outfile = self.filename.split('.')[0]+'-'+self.identifier+".sphere"
    self.sphere_pipeline = self.getSpherePipeline()




  def getSpherePipeline(self):
      print("Obtaining sphere...")
      pipeline = import_file(self.filename)
      expr = "c_20 < "+str(self.cutoff)
      pipeline.modifiers.append(ExpressionSelectionModifier(expression=expr))
      pipeline.modifiers.append(DeleteSelectedModifier())

      data = pipeline.compute()
      print("Complete.")
      return pipeline

  def export_file_as(self,file_type = 'xyz'):
      export_file(self.sphere_pipeline, self.outfile, file_type, columns =
    ["Particle Identifier", "Particle Type", "Position.X", "Position.Y", "Position.Z"]
  )


