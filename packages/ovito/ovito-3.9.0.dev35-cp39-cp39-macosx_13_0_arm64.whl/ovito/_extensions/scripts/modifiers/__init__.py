import importlib
import ovito.modifiers

# Inject Python script extensions into the ovito.modifiers package.
# Note: Using importlib.import_module() here to load them, because human-readable Python filenames contain whitespace.

ovito.modifiers.IdentifyFCCPlanarFaultsModifier = importlib.import_module(".Identify fcc planar faults", __name__).IdentifyFCCPlanarFaultsModifier
ovito.modifiers.__all__ += ['IdentifyFCCPlanarFaultsModifier']

ovito.modifiers.RenderLAMMPSRegionsModifier = importlib.import_module(".Render LAMMPS regions", __name__).RenderLAMMPSRegionsModifier
ovito.modifiers.__all__ += ['RenderLAMMPSRegionsModifier']