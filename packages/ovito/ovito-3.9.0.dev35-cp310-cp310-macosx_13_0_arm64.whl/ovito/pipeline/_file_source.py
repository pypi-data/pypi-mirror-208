import ovito
from . import FileSource
from ..data import DataCollection
from ..nonpublic import FileImporter, PipelineStatus, PythonScriptFileImporter
import collections.abc as collections

# Implementation of FileSource.load() method:
def _FileSource_load(self, location, **params):
    """ Sets a new input file, from which this data source will retrieve its data from.

        The function accepts additional keyword arguments, which are forwarded to the format-specific file reader.
        For further information, please see the documentation of the :py:func:`~ovito.io.import_file` function,
        which has the same function interface as this method.

        :param str location: The local file(s) or remote URL to load.
    """

    # Process input parameter
    if isinstance(location, str):
        location_list = [location]
    elif isinstance(location, collections.Sequence):
        location_list = list(location)
    else:
        raise TypeError("Invalid input file location. Expected string or sequence of strings.")
    first_location = location_list[0]

    # Did the caller specify the format of the input file explicitly?
    if 'input_format' in params:
        # Look up the importer class for the registered format name.
        format = params.pop('input_format')
        if not format in ovito.io.import_file._formatTable:
            raise ValueError(f"Unknown input format: '{format}'. The supported formats are: {sorted(list(ovito.io.import_file._formatTable.keys()))}")

        # Create an instance of the importer class. It will be configured below.
        importer = ovito.io.import_file._formatTable[format]()
    else:
        # Auto-detect the file's format if caller did not specify the format explicitly.
        importer = FileImporter.autodetect_format(first_location)
        if not importer:
            raise RuntimeError("Could not detect the file format. The format might not be supported.")

    # Re-use existing importer if compatible.
    if self.importer and type(self.importer) is type(importer):
        importer = self.importer

    # Forward user parameters to the file importer object.
    importer_object = importer.delegate if isinstance(importer, PythonScriptFileImporter) else importer
    for key, value in params.items():
        if not hasattr(importer_object, key):
            raise KeyError(f"Invalid keyword parameter. File reader {importer_object!r} doesn't support parameter '{key}'.")
        importer_object.__setattr__(key, value)

    # Load new data file.
    self.set_source(location_list, importer, False, False)

    # Block execution until data file has been loaded.
    self.wait_until_ready(0) # Requesting frame 0 here, because full list of frames is not loaded yet at this point.

    # Raise Python error if loading failed.
    if self.status.type == PipelineStatus.Type.Error:
        raise RuntimeError(self.status.text)

    # Block until list of animation frames has been loaded
    self.wait_for_frames_list()

FileSource.load = _FileSource_load

# Implementation of FileSource.source_path property.
def _get_FileSource_source_path(self):
    """ This read-only attribute returns the path(s) or URL(s) of the file(s) where this :py:class:`!FileSource` retrieves its input data from.
        You can change the source path by calling :py:meth:`.load`. """
    path_list = self.get_source_paths()
    if len(path_list) == 1:
        return path_list[0]
    elif len(path_list) == 0:
        return ""
    else:
        return path_list
FileSource.source_path = property(_get_FileSource_source_path)

def _FileSource_compute(self, frame = None):
    """ Requests data from this data source. The :py:class:`!FileSource` will load it from the external file if needed.

        The optional *frame* parameter determines the frame to retrieve, which must be in the range 0 through (:py:attr:`num_frames`-1).
        If no frame number is specified, the current time slider position is used (will always be frame 0 for scripts not running in the context of an interactive OVITO session).

        The :py:class:`!FileSource` uses a caching mechanism to keep the data for one or more frames in memory. Thus, invoking :py:meth:`!compute`
        repeatedly to retrieve the same frame will typically be very fast.

        :param int frame: The source frame to retrieve.
        :return: A new :py:class:`~ovito.data.DataCollection` containing the loaded data.
    """
    state = self._evaluate(frame)
    if state.status.type == PipelineStatus.Type.Error:
        raise RuntimeError(f"Data source evaluation failed: {state.status.text}")
    if state.data is None:
        raise RuntimeError("Data pipeline did not yield any output DataCollection.")

    return state.mutable_data

FileSource.compute = _FileSource_compute