# Load dependencies.
import ovito._extensions.pyscript
import ovito._extensions.particles

# Load the C extension module.
import ovito.plugins.oxDNAPython

# Register import formats.
ovito.io.import_file._formatTable["oxdna"] = ovito.nonpublic.OXDNAImporter