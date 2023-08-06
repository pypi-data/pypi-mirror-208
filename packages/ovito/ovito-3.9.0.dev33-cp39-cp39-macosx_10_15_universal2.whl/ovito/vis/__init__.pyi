"""This module contains classes related to data visualization and rendering.

Rendering:

  * :py:class:`Viewport`

Rendering engines:

  * :py:class:`OpenGLRenderer`
  * :py:class:`TachyonRenderer`
  * :py:class:`OSPRayRenderer`

Data visualization elements:

  * :py:class:`DataVis` (base class for all visual elements)
  * :py:class:`BondsVis`
  * :py:class:`DislocationVis`
  * :py:class:`ParticlesVis`
  * :py:class:`SimulationCellVis`
  * :py:class:`SurfaceMeshVis`
  * :py:class:`TrajectoryVis`
  * :py:class:`TriangleMeshVis`
  * :py:class:`VectorVis`
  * :py:class:`VoxelGridVis`

Viewport overlays:

  * :py:class:`ViewportOverlay` (base class for all overlay types)
  * :py:class:`ColorLegendOverlay`
  * :py:class:`CoordinateTripodOverlay`
  * :py:class:`PythonViewportOverlay`
  * :py:class:`TextLabelOverlay`"""
__all__ = ['Viewport', 'OpenGLRenderer', 'DataVis', 'CoordinateTripodOverlay', 'PythonViewportOverlay', 'TextLabelOverlay', 'ViewportOverlay', 'TriangleMeshVis', 'SimulationCellVis', 'ColorLegendOverlay', 'SurfaceMeshVis', 'VoxelGridVis', 'ParticlesVis', 'VectorVis', 'BondsVis', 'TrajectoryVis', 'DislocationVis', 'OSPRayRenderer', 'TachyonRenderer']
from __future__ import annotations
from typing import Tuple, Optional, Any, Union, Sequence, MutableSequence, Callable, Generator
import enum
from numpy.typing import NDArray
import numpy
from dataclasses import dataclass
import ovito
import ovito.modifiers
import ovito.pipeline
import PySide6.QtCore
import PySide6.QtGui
import PySide6.QtWidgets
import ipywidgets
Color = Tuple[float, float, float]
Vector3 = Tuple[float, float, float]

@dataclass(kw_only=True)
class OpenGLRenderer:
    """This is the default rendering backend used by the :py:meth:`Viewport.render_image` and :py:meth:`Viewport.render_anim` functions. 
It also serves in the OVITO desktop application for the real-time display of the 3d scene in the interactive viewport windows. 
The OpenGL renderer uses your computer's GPU graphics hardware to accelerate the generation of images.
See the corresponding user manual page for more information. 

Enabling OpenGL support

This rendering backend requires an environment where OpenGL graphics support is available. Standalone Python scripts typically 
run in a headless environment, e.g. a text-based terminal without graphics support. This prevents the :py:class:`OpenGLRenderer` from
initializing an OpenGL context and an offscreen framebuffer to render into. A call to :py:meth:`Viewport.render_image` will raise an error in this case, and
you have to take one of the following steps to enable OpenGL graphics support -- or altogether avoid the problem by 
using one of the software-based rendering backends instead.

The ``ovito`` Python module, if imported by a Python script running in an external Python interpreter, sets up a headless environment by default, in which OpenGL rendering
is *not* available. A proper graphics environment can be explicitly requested in two ways (starting with OVITO 3.7.10):

#. Setting the environment variable ``OVITO_GUI_MODE=1`` prior to importing the ``ovito`` package or any of its sub-packages:
   
   You can set the variable either externally, before or while launching your Python script program:
  
   .. code-block:: shell-session

     OVITO_GUI_MODE=1 python3 <your_script.py>
  
   or within the Python program itself by including the following lines *before* the first ``import ovito`` statement at the top of your .py file::

      import os
      os.environ['OVITO_GUI_MODE'] = '1' # Request a session with OpenGL support

#. Create a Qt application object with GUI support before importing the ``ovito`` module:
  
   The standard behavior of the ``ovito`` module is to create a global `QCoreApplication <https://doc.qt.io/qtforpython/PySide6/QtCore/QCoreApplication.html>`__ object 
   during module import, which is only suitable for headless operation, e.g., file I/O and pipeline computations, but not sufficient for OpenGL-based rendering. 
   If, however, a global Qt application object already exists at the time the ``ovito`` module is loaded, then OVITO will use that pre-existing
   application object. For example::

      # Make the program run in the context of the graphical desktop environment.
      import PySide6.QtWidgets
      app = PySide6.QtWidgets.QApplication() 

      from ovito.vis import *
      vp = Viewport()
      vp.render_image(renderer=OpenGLRenderer())

        Other Python packages imported by your Python script may also be using the Qt cross-platform toolkit 
     (e.g. `Matplotlib's Qt backend <https://matplotlib.org/stable/users/explain/backends.html>`__). That means such a third-party package may 
     also set up a global Qt application object, which will subsequently be shared with the ovito module. Furthermore, if you are executing 
     your Python script in a graphical IDE such as *Spyder*, which `itself is based on the Qt framework <https://docs.spyder-ide.org/current/workshops/qt_fundamentals.html>`__, then 
     a global application instance may already be present at the time the Python script is launched.

**Linux/Unix systems (including WSL2)**

On Linux/Unix systems, an X11 or Wayland display server is required for OpenGL graphics. When you request a graphics session 
with one of the methods described above, the Qt framework will attempt to establish a connection to the X11/Wayland server.
If this fails, e.g., because the `DISPLAY environment variable <https://stackoverflow.com/questions/20947681/understanding-linux-display-variable>`__ 
is not set correctly, Qt reports an error and the program will quit with the following message:

.. code-block:: shell-session

  qt.qpa.xcb: could not connect to display 
  qt.qpa.plugin: Could not load the Qt platform plugin "xcb" in "" even though it was found.
  This application failed to start because no Qt platform plugin could be initialized. Reinstalling the application may fix this problem.

Remote servers and HPC clusters, which are typically accessed via SSH terminals, often do not provide a running graphical desktop environment
that would allow the use of OpenGL functions by OVITO. In such a headless environment it may still be possible to
provide a `virtual X server <https://en.wikipedia.org/wiki/Xvfb>`__ to the Python application, 
e.g., using the `xvfb-run <https://manpages.ubuntu.com/manpages/xenial/man1/xvfb-run.1.html>`__ wrapper command:

.. code-block:: shell-session

  OVITO_GUI_MODE=1 xvfb-run python3 <your_script.py>"""
    antialiasing_level: int = 3
    'A positive integer controlling the level of supersampling. If 1, no supersampling is performed. For larger values, the image in rendered at a higher resolution and then scaled back to the output size to reduce aliasing artifacts.\n\nDefault: ``3``'

@dataclass(kw_only=True)
class TachyonRenderer:
    """This is one of the software-based rendering backends of OVITO. Tachyon is an open-source raytracing engine integrated into OVITO.

An instance of this class can be passed to the :py:meth:`Viewport.render_image` or :py:meth:`Viewport.render_anim` methods. 

Tachyon can render scenes with ambient occlusion lighting, semi-transparent objects, and depth-of-field focal blur. See the corresponding user manual page for more information on this rendering backend."""
    ambient_occlusion: bool = True
    'Enables ambient occlusion shading. Enabling this lighting technique mimics some of the effects that occur under conditions of omnidirectional diffuse illumination, e.g. outdoors on an overcast day.\n\nDefault: ``True``'
    ambient_occlusion_brightness: float = 0.8
    'Controls the brightness of the sky light source used for ambient occlusion.\n\nDefault: ``0.8``'
    ambient_occlusion_samples: int = 12
    'Ambient occlusion is implemented using a Monte Carlo technique. This parameters controls the number of samples to compute. A higher sample count leads to a more even shading, but requires more computation time.\n\nDefault: ``12``'
    antialiasing: bool = True
    'Enables supersampling to reduce aliasing effects.\n\nDefault: ``True``'
    antialiasing_samples: int = 12
    'The number of supersampling rays to generate per pixel to reduce aliasing effects.\n\nDefault: ``12``'
    aperture: float = 0.01
    'Controls the aperture of the camera, which is used for depth-of-field rendering.\n\nDefault: ``0.01``'
    depth_of_field: bool = False
    'This flag enables depth-of-field rendering.\n\nDefault: ``False``'
    direct_light: bool = True
    'Enables the parallel light source, which is positioned at an angle behind the camera.\n\nDefault: ``True``'
    direct_light_intensity: float = 0.9
    'Controls the brightness of the directional light source.\n\nDefault: ``0.9``'
    focal_length: float = 40.0
    'Controls the focal length of the camera, which is used for depth-of-field rendering.\n\nDefault: ``40.0``'
    shadows: bool = True
    'Enables cast shadows for the directional light source.\n\nDefault: ``True``'

@dataclass(kw_only=True)
class OSPRayRenderer:
    """This is one of the software-based rendering backends of OVITO, which can generate images with higher fidelity than the standard :py:class:`OpenGLRenderer`. Typically, you create an instance of this class and pass it to the :py:meth:`Viewport.render_image` or :py:meth:`Viewport.render_anim` methods. 

OSPRay can render scenes with ambient occlusion lighting, semi-transparent objects, and depth-of-field focal blur. For technical details of the supported rendering algorithms and parameters, see the `www.ospray.org <https://www.ospray.org>`__ website. See also the corresponding user manual page for more information on this rendering engine."""
    ambient_brightness: float = 0.8
    'Controls the radiance of the ambient light. \n\nDefault: ``0.8``'
    ambient_light_enabled: bool = True
    'Enables the ambient light, which surrounds the scene and illuminates it from infinity with constant radiance. \n\nDefault: ``True``'
    aperture: float = 0.5
    'The aperture radius controls how blurred objects will appear that are out of focus if :py:attr:`dof_enabled` is set. \n\nDefault: ``0.5``'
    denoising_enabled: bool = True
    'Enables the application of a denoising filter to the rendered image to reduce Monte Carlo noise inherent to stochastic ray tracing methods like path tracing. \n\nDefault: ``True``'
    direct_light_angular_diameter: float = numpy.radians(10.0)
    'Specifies the apparent size (angle in radians) of the default directional light source. Setting the angular diameter to a value greater than zero yields soft shadow. \n\nDefault: ``numpy.radians(10.0)``'
    direct_light_enabled: bool = True
    'Enables the default directional light source that is positioned behind the camera and is pointing roughly along the viewing direction. The brightness of the light source is controlled by the :py:attr:`direct_light_intensity` parameter. \n\nDefault: ``True``'
    direct_light_intensity: float = 1.0
    'The intensity of the default directional light source. The light source must be enabled by setting :py:attr:`direct_light_enabled`. \n\nDefault: ``1.0``'
    dof_enabled: bool = False
    'Enables the depth-of-field effect (focal blur). Only objects exactly at the distance from the camera specified by the :py:attr:`focal_length` will appear sharp when depth-of-field rendering is enabled. Objects closer to or further from the camera will appear blurred. The strength of the effect is controlled by the :py:attr:`aperture` parameter. \n\nDefault: ``False``'
    focal_length: float = 40.0
    'Only objects exactly at this distance from the camera will appear sharp when :py:attr:`dof_enabled` is set. Objects closer to or further from the camera will appear blurred. \n\nDefault: ``40.0``'
    material_shininess: float = 10.0
    'Specular Phong exponent value for the default material. Usually in the range between 2.0 and 10,000. \n\nDefault: ``10.0``'
    material_specular_brightness: float = 0.02
    'Controls the specular reflectivity of the default material. \n\nDefault: ``0.02``'
    max_ray_recursion: int = 10
    'The maximum number of recursion steps during raytracing. Normally, 1 or 2 is enough, but when rendering semi-transparent objects, a larger recursion depth is needed. \n\nDefault: ``10``'
    refinement_iterations: int = 4
    'The OSPRay renderer supports a feature called adaptive accumulation, which is a progressive rendering method. During each rendering pass, the rendered image is progressively refined. This parameter controls the number of iterations until the refinement stops. \n\nDefault: ``4``'
    samples_per_pixel: int = 2
    'The number of raytracing samples computed per pixel. Larger values can help to reduce aliasing artifacts. \n\nDefault: ``2``'
    sky_albedo: float = 0.3
    'Controls the ground reflectance affecting the sky-sun light source. The light source must be enabled first by setting :py:attr:`sky_light_enabled`. Valid parameter range is [0.0 - 1.0].\n\nDefault: ``0.3``'
    sky_brightness: float = 2.0
    'The intensity of the sky-sun light source. The light source must be enabled first by setting :py:attr:`sky_light_enabled`. \n\nDefault: ``2.0``'
    sky_light_enabled: bool = False
    'Enables the sky/sun light source that mimics the light coming from the sky and the sun in an outdoor scene. The brightness of the sky is controlled by the :py:attr:`sky_brightness` parameter. \n\nDefault: ``False``'
    sky_turbidity: float = 3.0
    'Controls atmospheric turbidity due to particles affecting the sky-sun light source. The light source must be enabled first by setting :py:attr:`sky_light_enabled`. Valid parameter range is [1.0 - 10.0].\n\nDefault: ``3.0``'
Renderer = Union[OpenGLRenderer, TachyonRenderer, OSPRayRenderer]

@dataclass(kw_only=True)
class ViewportOverlay:
    """Abstract base class for viewport :py:attr:`overlays` and :py:attr:`underlays`, which render two-dimensional graphics on top of (or behind) the three-dimensional scene. Examples are :py:class:`CoordinateTripodOverlay`, :py:class:`TextLabelOverlay` and :py:class:`ColorLegendOverlay`. You can also implement your own viewport overlay in Python by using the :py:class:`PythonViewportOverlay` class."""
    enabled: bool = True
    'Controls whether the overlay gets rendered. An overlay can be hidden by setting its :py:attr:`enabled` property to ``False``. \n\nDefault: ``True``'

@dataclass(kw_only=True)
class ColorLegendOverlay(ViewportOverlay):
    """Base: :py:class:`ovito.vis.ViewportOverlay`

This layer renders a color legend over the viewport image, which helps the audience recognize the meaning of depicted object colors.
You should add this :py:class:`ViewportOverlay` to the :py:attr:`Viewport.overlays` or :py:attr:`Viewport.underlays` list of the viewport
you use for rendering:

```python
  from ovito.vis import ColorLegendOverlay, Viewport
  from ovito.qt_compat import QtCore
  
  vp = Viewport(type=Viewport.Type.Top)
  
  legend = ColorLegendOverlay(
      title = 'Potential energy per atom',
      alignment = QtCore.Qt.AlignmentFlag.AlignLeft | QtCore.Qt.AlignmentFlag.AlignTop,
      orientation = QtCore.Qt.Orientation.Vertical,
      offset_y = -0.04,
      font_size = 0.12,
      format_string = '%.2f eV')
  vp.overlays.append(legend)
```

Specifying the color map source

Most importantly, you need to specify which color scheme the legend is supposed to display. There currently are three kinds of color map sources one can use
for a legend:

  * The color map of a :py:class:`ColorCodingModifier` used in the current scene.
  * The color map of a visual element that supports pseudo-color mapping, e.g. :py:class:`SurfaceMeshVis`, :py:class:`VoxelGridVis`, :py:class:`TrajectoryVis`, or :py:class:`VectorVis`.
  * The discrete colors of a typed property representing different particle types, bond types, etc.

To display the color spectrum of a color coding modifier, including text labels indicating the corresponding numeric value range,
set the legend's :py:attr:`.modifier` field to point to the :py:class:`ColorCodingModifier`:

```python
  modifier = ColorCodingModifier(property='peatom')
  pipeline.modifiers.append(modifier)
  
  legend.modifier = modifier
```

If you have set up a visual element in your scene that supports pseudo-color mapping, e.g. a :py:class:`VoxelGridVis`
visualizing some grid property using pseudo-colors, then you can associate it with the color legend by
assigning it to the :py:attr:`color_mapping_source` field:

```python
  # Load a VASP volumetric charge density file:
  pipeline = import_file('input/CHGCAR.nospin.gz')
  pipeline.add_to_scene()
  
  # Configure the VoxelGridVis element responsible for displaying the charge density grid:
  grid_vis = pipeline.compute().grids['charge-density'].vis
  grid_vis.enabled = True
  grid_vis.color_mapping_property = 'Charge density' # Grid property to visualize using pseudo-colors
  grid_vis.color_mapping_interval = (0.02186, 0.05465)
  
  # Use the VoxelGridVis as color map source for the legend:
  legend.color_mapping_source = grid_vis
```

To display the discrete colors of a typed :py:class:`Property`, specify the source particle or bond property as follows:

```python
  legend.property = 'particles/Particle Type'
```

See the documentation of the :py:attr:`property` parameter for more information."""
    alignment: PySide6.QtCore.Qt.Alignment = PySide6.QtCore.Qt.AlignHCenter ^ PySide6.QtCore.Qt.AlignBottom
    'Selects the corner of the viewport where the color bar is displayed (anchor position). This must be a valid `Qt.AlignmentFlag value <https://doc.qt.io/qtforpython/PySide6/QtCore/Qt.html#PySide6.QtCore.PySide6.QtCore.Qt.AlignmentFlag>`__ as shown in the code example above. \n\nDefault: ``QtCore.Qt.AlignmentFlag.AlignHCenter | QtCore.Qt.AlignmentFlag.AlignBottom``'
    aspect_ratio: float = 8.0
    'The aspect ratio of the color bar. Larger values make it more narrow. \n\nDefault: ``8.0``'
    border_color: Color = (0.0, 0.0, 0.0)
    'The line color of the border painted around the color map. This is used only if :py:attr:`border_enabled` is set.\n\nDefault: ``(0.0, 0.0, 0.0)``'
    border_enabled: bool = False
    'Enables the painting of a border line around color map. \n\nDefault: ``False``'
    font: str = ''
    "A string with comma-separated parameter values describing the font to be used for rendering the text labels of the viewport layer. The string must follow the specific form understood by the `QFont.fromString() <https://doc.qt.io/qtforpython/PySide6/QtGui/QFont.html#PySide6.QtGui.PySide6.QtGui.QFont.fromString>`__ method, for example ``'Arial,10,-1,5,75,0,0,0,0,0,Bold'``. \n\nNote that the font size parameter (10 in the example specification above) will be ignored by the viewport layer, because the size of text labels is already controlled by the :py:attr:`font_size` parameter."
    font_size: float = 0.1
    'The relative size of the font used for text labels.\n\nDefault: ``0.1``'
    label_size: float = 0.6
    'The relative size of the font used for the tick labels. Size given relative to :py:attr:`font_size`.\n\nDefault: ``0.6``'
    format_string: str = '%g'
    "The format string used with the `sprintf() <https://en.cppreference.com/w/cpp/io/c/fprintf>`__ function to generate the text representation of floating-point values. You can change this format string to control the number of displayed decimal places. \n\nLiteral text may be incorporated into the format string to include physical units, for example, and :ref:`manual:viewport_layers.text_label.text_formatting` is supported.\n\nDefault: ``'%g'``"
    label1: str = ''
    "Sets the text string displayed at the upper end of the bar. If empty, the :py:attr:`end_value` of the :py:class:`ColorCodingModifier` is used. \n\nThe label supports :ref:`manual:viewport_layers.text_label.text_formatting`.\n\nDefault: ``''``"
    label2: str = ''
    "Sets the text string displayed at the lower end of the bar. If empty, the :py:attr:`start_value` of the :py:class:`ColorCodingModifier` is used. \n\nThe label supports :ref:`manual:viewport_layers.text_label.text_formatting`.\n\nDefault: ``''``"
    legend_size: float = 0.3
    'Controls the overall size of the color bar relative to the output image size. \n\nDefault: ``0.3``'
    modifier: Optional[ovito.modifiers.ColorCodingModifier] = None
    'The :py:class:`ColorCodingModifier` for which the color legend should be rendered.'
    offset_x: float = 0.0
    'This parameter allows to displace the color bar horizontally from its anchor position. The offset is specified as a fraction of the output image width.\n\nDefault: ``0.0``'
    offset_y: float = 0.0
    'This parameter allows to displace the color bar vertically from its anchor position. The offset is specified as a fraction of the output image height.\n\nDefault: ``0.0``'
    orientation: PySide6.QtCore.Orientation = PySide6.QtCore.Qt.Horizontal
    'Selects the orientation of the color bar. This must be a valid `Qt.Orientation value <https://doc.qt.io/qtforpython/PySide6/QtCore/Qt.html#PySide6.QtCore.PySide6.QtCore.Qt.Orientation>`__ as shown in the code example above. \n\nDefault: ``QtCore.Qt.Orientation.Horizontal``'
    outline_color: Color = (1.0, 1.0, 1.0)
    'The text outline color. This is used only if :py:attr:`outline_enabled` is set.\n\nDefault: ``(1.0, 1.0, 1.0)``'
    outline_enabled: bool = False
    'Enables the painting of a font outline to make the text easier to read.\n\nDefault: ``False``'
    text_color: Color = (0.0, 0.0, 0.0)
    'The RGB color used for text labels.\n\nDefault: ``(0.0, 0.0, 0.0)``'
    title: str = ''
    "The text displayed next to the color bar. If this string is empty, the title of the source :py:class:`Property` object is used. \n\nThe title label supports :ref:`manual:viewport_layers.text_label.text_formatting`.\n\nDefault: ``''``"
    property: str = ''
    "Specifies the path to the typed :py:class:`Property` for which a discrete color legend should be rendered. \n\nThe specified path tells the legend where to find the particle or bond property whose discrete :py:attr:`types` it should display. Generally, the selected property may be dynamically produced by the current data :py:class:`Pipeline` and may not exist yet at the point when you set up the :py:class:`ColorLegendOverlay`. That's why you have to reference it by name instead of specifying the :py:class:`Property` object directly. \n\nThe path specifies where to find the selected property within the nested containers that make up the :py:class:`DataCollection` produced by the current pipeline. It consists of a sequence of `DataObject.identifier` strings separated by slashes. The last entry in the path is simply the name of the :py:class:`Property` to be displayed by the legend. \n\nExamples:\n\n```python\n  # Display the different structural types identified by PolyhedralTemplateMatchingModifier:\n  legend.property = 'particles/Structure Type'\n  \n  # Display the list of bond types in the system:\n  legend.property = 'particles/bonds/Bond Type'\n```\n\nIn case there are multiple data pipelines in the current scene, the legend will automatically pick the first pipeline that yields a :py:class:`DataCollection` containing the selected property. \n\nDefault: ``''``"
    color_mapping_source: Optional[DataVis] = None
    "The :py:class:`DataVis` element to be used as color map source by this viewport layer. Set this to the :py:class:`SurfaceMeshVis`, :py:class:`VoxelGridVis`, :py:class:`TrajectoryVis`, or :py:class:`VectorVis` element whose color map the legend should display. \n\nExample:\n\n```python\n  # Add modifier to the pipeline which generates particle trajectory lines:\n  modifier = GenerateTrajectoryLinesModifier(only_selected=False)\n  pipeline.modifiers.append(modifier)\n  modifier.generate()\n  \n  # Configure the modifier's TrajectoryVis element to apply a color mapping to the lines:\n  modifier.vis.color_mapping_property = 'Time'\n  modifier.vis.color_mapping_interval = (0, pipeline.source.num_frames-1)\n  \n  # Add a color legend and link it to the TrajectoryVis element to display its color map.\n  vp.overlays.append(ColorLegendOverlay(color_mapping_source=modifier.vis))\n```\n\nDefault: ``None``"
    ticks_enabled: bool = False
    'Enables the painting of tick marks and labels on the color map. \n\nDefault: ``False``'
    ticks_spacing: float = 0.0
    'Defines the tick spacing along the (continuous) color scale. Requires :py:attr:`ticks_enabled` to be set. The standard value of ``0`` activates automatic tick placement based on the input value range.\n\nDefault: ``0``'
    rotate_title: bool = False
    "Enables the vertical orientation of the title, i.e. text orientation parallel to the color legend, if the legend's :py:attr:`orientation` is set to `QtCore.Qt.Vertical`. Otherwise this option is ignored and the title text will be rendered horizontally.\n\nDefault: ``False``"
    background_enabled: bool = False
    'Enables the painting of a color legend background. A filled panel will be drawn behind the legend to better distinguish the legend from the cluttered 3d scene in the background.\n\nDefault: ``False``'
    background_color: Color = (1.0, 1.0, 1.0)
    'The color of the background panel. Only used if :py:attr:`background_enabled` is set.\n\nDefault: ``(1.0, 1.0, 1.0)``'

@dataclass(kw_only=True)
class CoordinateTripodOverlay(ViewportOverlay):
    """Base: :py:class:`ovito.vis.ViewportOverlay`

Displays a coordinate tripod in rendered images. You can attach an instance of this class to a viewport by adding it to the viewport's :py:attr:`overlays` collection:

```python
  from ovito.vis import CoordinateTripodOverlay, Viewport
  from ovito.qt_compat import QtCore
  
  # Create the overlay.
  tripod = CoordinateTripodOverlay()
  tripod.size = 0.07
  tripod.alignment = QtCore.Qt.AlignmentFlag.AlignRight | QtCore.Qt.AlignmentFlag.AlignBottom
  tripod.style = CoordinateTripodOverlay.Style.Solid
  
  # Attach overlay to a newly created viewport.
  viewport = Viewport(type=Viewport.Type.Perspective, camera_dir=(1,2,-1))
  viewport.overlays.append(tripod)
```"""

    class Style(enum.Enum):
        """"""
        Flat = enum.auto()
        Solid = enum.auto()
    alignment: PySide6.QtCore.Qt.Alignment = PySide6.QtCore.Qt.AlignLeft ^ PySide6.QtCore.Qt.AlignBottom
    'Selects the corner of the viewport where the tripod is displayed (anchor position). This must be a valid `Qt.AlignmentFlag value <https://doc.qt.io/qtforpython/PySide6/QtCore/Qt.html#PySide6.QtCore.PySide6.QtCore.Qt.AlignmentFlag>`__ value as shown in the example above.\n\nDefault: ``QtCore.Qt.AlignmentFlag.AlignLeft | QtCore.Qt.AlignmentFlag.AlignBottom``'
    axis1_color: Color = (1.0, 0.0, 0.0)
    'RGB display color of the first axis.\n\nDefault: ``(1.0, 0.0, 0.0)``'
    axis1_dir: Vector3 = (1.0, 0.0, 0.0)
    'Vector specifying direction and length of first axis, expressed in the global Cartesian coordinate system.\n\nDefault: ``(1.0, 0.0, 0.0)``'
    axis1_enabled: bool = True
    'Enables the display of the first axis.\n\nDefault: ``True``'
    axis1_label: str = 'x'
    'Text label for the first axis. Supports formatted text.\n\nDefault: ``"x"``'
    axis2_color: Color = (0.0, 0.8, 0.0)
    'RGB display color of the second axis.\n\nDefault: ``(0.0, 0.8, 0.0)``'
    axis2_dir: Vector3 = (0.0, 1.0, 0.0)
    'Vector specifying direction and length of second axis, expressed in the global Cartesian coordinate system.\n\nDefault: ``(0.0, 1.0, 0.0)``'
    axis2_enabled: bool = True
    'Enables the display of the second axis.\n\nDefault: ``True``'
    axis2_label: str = 'y'
    'Text label for the second axis. Supports formatted text.\n\nDefault: ``"y"``'
    axis3_color: Color = (0.2, 0.2, 1.0)
    'RGB display color of the third axis.\n\nDefault: ``(0.2, 0.2, 1.0)``'
    axis3_dir: Vector3 = (0.0, 0.0, 1.0)
    'Vector specifying direction and length of third axis, expressed in the global Cartesian coordinate system.\n\nDefault: ``(0.0, 0.0, 1.0)``'
    axis3_enabled: bool = True
    'Enables the display of the third axis.\n\nDefault: ``True``'
    axis3_label: str = 'z'
    'Text label for the third axis. Supports formatted text.\n\nDefault: ``"z"``'
    axis4_color: Color = (1.0, 0.0, 1.0)
    'RGB display color of the fourth axis.\n\nDefault: ``(1.0, 0.0, 1.0)``'
    axis4_dir: Vector3 = (0.7071, 0.7071, 0.0)
    'Vector specifying direction and length of fourth axis, expressed in the global Cartesian coordinate system.\n\nDefault: ``(0.7071, 0.7071, 0.0)``'
    axis4_enabled: bool = False
    'Enables the display of the fourth axis.\n\nDefault: ``False``'
    axis4_label: str = 'w'
    'Label for the fourth axis. Supports formatted text.\n\nDefault: ``"w"``'
    font: str = ''
    "A string with comma-separated parameter values describing the font to be used for rendering the text labels of the viewport layer. The string must follow the specific form understood by the `QFont.fromString() <https://doc.qt.io/qtforpython/PySide6/QtGui/QFont.html#PySide6.QtGui.PySide6.QtGui.QFont.fromString>`__ method, for example ``'Arial,10,-1,5,75,0,0,0,0,0,Bold'``. \n\nNote that the font size parameter (10 in the example specification above) will be ignored by the viewport layer, because the size of text labels is already controlled by the :py:attr:`font_size` parameter."
    font_size: float = 0.4
    'The font size for rendering the text labels of the tripod. The font size is specified in terms of the tripod size.\n\nDefault: ``0.4``'
    line_width: float = 0.06
    'Controls the width of axis arrows. The line width is specified relative to the tripod size.\n\nDefault: ``0.06``'
    offset_x: float = 0.0
    'This parameter allows to displace the tripod horizontally. The offset is specified as a fraction of the output image width.\n\nDefault: ``0.0``'
    offset_y: float = 0.0
    'This parameter allows to displace the tripod vertically. The offset is specified as a fraction of the output image height.\n\nDefault: ``0.0``'
    outline_color: Color = (1.0, 1.0, 1.0)
    'The outline color for text labels. This is used only if :py:attr:`outline_enabled` is set.\n\nDefault: ``(1.0, 1.0, 1.0)``'
    outline_enabled: bool = False
    'Enables the painting of a font outline to make the axis labels easier to read.\n\nDefault: ``False``'
    size: float = 0.075
    'Scaling factor controlling the overall size of the tripod. The size is specified as a fraction of the output image height.\n\nDefault: ``0.075``'
    style: CoordinateTripodOverlay.Style = Style.Flat
    'Selects the visual style of the coordinate axis tripod.\nSupported values are:\n\n   * ``CoordinateTripodOverlay.Style.Flat`` (default) \n   * ``CoordinateTripodOverlay.Style.Solid``'

@dataclass(kw_only=True)
class PythonViewportOverlay(ViewportOverlay):
    """Base: :py:class:`ovito.vis.ViewportOverlay`

This type of viewport overlay runs a custom Python script function every time an image of the viewport is rendered. The user-defined script function can paint arbitrary graphics on top of the three-dimensional scene. 

Note that instead of using a :py:class:`PythonViewportOverlay` it is also possible to directly manipulate the image returned by the :py:meth:`Viewport.render_image` method before saving the image to disk. A :py:class:`PythonViewportOverlay` is only necessary when rendering animations or if you want the overlay to be usable from in the graphical program version. 

You can attach the Python overlay to a viewport by adding it to the viewport's :py:attr:`overlays` collection:

```python
  from ovito.vis import PythonViewportOverlay, Viewport
  
  # Create a viewport:
  viewport = Viewport(type = Viewport.Type.Top)
  
  # The user-defined function that will paint on top of rendered images:
  def render_some_text(args: PythonViewportOverlay.Arguments):
      args.painter.drawText(10, 10, "Hello world")
  
  # Attach overlay function to viewport:
  viewport.overlays.append(PythonViewportOverlay(function = render_some_text))
```

The user-defined Python function must accept a single argument (named ``args`` in the example above). The system will pass in an instance of the :py:class:`.Arguments` class to the function, which contains various state information, including the current animation frame number and the viewport being rendered as well as a `QPainter <https://doc.qt.io/qtforpython/PySide6/QtGui/QPainter.html>`__ object, which the function should use to issue drawing calls."""

    class Arguments:
        """This data structure is passed to the user-defined ``render()`` function of the viewport overlay by the system. It carries context information about the frame being rendered and provides utility methods for projecting points from 3d to 2d space. Most importantly, it gives access to the :py:attr:`painter` object, which should be used by the ``render()`` function to issue drawing commands."""

        @property
        def fov(self) -> float:
            """The field of view of the viewport’s camera. For perspective projections, this is the frustum angle in the vertical direction (in radians). For orthogonal projections this is the visible range in the vertical direction (in world units)."""
            ...

        @property
        def frame(self) -> int:
            """The animation frame number being rendered (0-based)."""
            ...

        @property
        def is_perspective(self) -> bool:
            """Flag indicating whether the viewport uses a perspective projection or parallel projection."""
            ...

        @property
        def painter(self) -> PySide6.QtGui.QPainter:
            """The `QPainter <https://doc.qt.io/qtforpython/PySide6/QtGui/QPainter.html>`__ object, which provides painting methods for drawing on top of the image canvas."""
            ...

        @property
        def proj_tm(self) -> NDArray[numpy.float64]:
            """The projection matrix. This 4x4 matrix transforms points from camera space to screen space."""
            ...

        @property
        def view_tm(self) -> NDArray[numpy.float64]:
            """The affine camera transformation matrix. This 3x4 matrix transforms points/vectors from world space to camera space."""
            ...

        @property
        def scene(self) -> ovito.Scene:
            """The current three-dimensional :py:class:`~ovito.Scene` being rendered. Provides access to all visible data pipelines."""
            ...

        @property
        def size(self) -> Tuple[int, int]:
            """A tuple containing the width and height of the viewport image being rendered (in pixels). This may be a sub-region of the output image when rendering a multi-viewport layout."""
            ...

        @property
        def viewport(self) -> Viewport:
            """The :py:class:`Viewport` being rendered."""
            ...

        def project_point(self, world_xyz: Vector3) -> Optional[Tuple[float, float]]:
            """Projects a point, given in world-space coordinates, to screen space. This method can be used to determine where a 3d point would appear in the rendered image.

Note that the projected point may lay outside of the visible viewport region. Furthermore, for viewports with a perspective projection, the input point may lie behind the virtual camera. In this case no corresponding projected point in 2d screen space exists and the method returns ``None``. 

:param world_xyz: The (x,y,z) coordinates of the input point
:return: A (x,y) pair of pixel coordinates; or ``None`` if *world_xyz* is behind the viewer."""
            ...

        def project_size(self, world_xyz: Vector3, r: float) -> float:
            """Projects a size from 3d world space to 2d screen space. This method can be used to determine how large a 3d object, for example a sphere with the given radius *r*, would appear in the rendered image. 

Additionally to the size *r* to be projected, the method takes a coordinate triplet (x,y,z) as input. It specifies the location of the base point from where the distance is measured. 

:param world_xyz: The (x,y,z) world-space coordinates of the base point
:param r: The world-space size or distance to be converted to screen space
:return: The computed screen-space size measured in pixels."""
            ...
    function: Callable[[PythonViewportOverlay.Arguments], Optional[Generator[str | float, None, None]]] | None = None
    'A reference to the Python function to be called every time the viewport is repainted or when an output image is rendered.\n\nThe user-defined function must accept exactly one argument as shown in the example above. The system will pass an :py:class:`.Arguments` object to the function, providing various contextual information on the current frame being rendered. \n\nImplementation note: Exceptions raised within the custom rendering function are *not* propagated to the calling context. \n\nDefault: ``None``'

@dataclass(kw_only=True)
class TextLabelOverlay(ViewportOverlay):
    """Base: :py:class:`ovito.vis.ViewportOverlay`

Displays a text label in a viewport and in rendered images. You can attach an instance of this class to a viewport by adding it to the viewport's :py:attr:`overlays` collection:

```python
  from ovito.vis import TextLabelOverlay, Viewport
  from ovito.qt_compat import QtCore
  
  # Create the overlay:
  overlay = TextLabelOverlay(
      text = 'Some text',
      alignment = QtCore.Qt.AlignmentFlag.AlignHCenter | QtCore.Qt.AlignmentFlag.AlignBottom,
      offset_y = 0.1,
      font_size = 0.03,
      text_color = (0,0,0))
  
  # Attach the overlay to a newly created viewport:
  viewport = Viewport(type = Viewport.Type.Top)
  viewport.overlays.append(overlay)
```

Text labels can display dynamically computed values. See the :py:attr:`text` property for an example."""
    alignment: PySide6.QtCore.Qt.Alignment = PySide6.QtCore.Qt.AlignLeft ^ PySide6.QtCore.Qt.AlignTop
    'Selects the corner of the viewport where the text is displayed (anchor position). This must be a valid `Qt.AlignmentFlag value <https://doc.qt.io/qtforpython/PySide6/QtCore/Qt.html#PySide6.QtCore.PySide6.QtCore.Qt.AlignmentFlag>`__ as shown in the example above. \n\nDefault: ``QtCore.Qt.AlignmentFlag.AlignLeft | QtCore.Qt.AlignmentFlag.AlignTop``'
    font: str = ''
    "A string with comma-separated parameter values describing the font to be used for rendering the text labels of the viewport layer. The string must follow the specific form understood by the `QFont.fromString() <https://doc.qt.io/qtforpython/PySide6/QtGui/QFont.html#PySide6.QtGui.PySide6.QtGui.QFont.fromString>`__ method, for example ``'Arial,10,-1,5,75,0,0,0,0,0,Bold'``. \n\nNote that the font size parameter (10 in the example specification above) will be ignored by the viewport layer, because the size of text labels is already controlled by the :py:attr:`font_size` parameter."
    font_size: float = 0.02
    'The font size, which is specified as a fraction of the output image height.\n\nDefault: ``0.02``'
    format_string: str = '%.6g'
    "The format string used with the `sprintf() <https://en.cppreference.com/w/cpp/io/c/fprintf>`__ function to generate the text representation of global attributes (only floating-point values). You can change this format string to control the number of decimal places shown and switch between exponential and regular notation, for example. \n\nDefault: ``'%.6g'``"
    offset_x: float = 0.0
    'This parameter allows to displace the label horizontally from its anchor position. The offset is specified as a fraction of the output image width.\n\nDefault: ``0.0``'
    offset_y: float = 0.0
    'This parameter allows to displace the label vertically from its anchor position. The offset is specified as a fraction of the output image height.\n\nDefault: ``0.0``'
    outline_color: Color = (1.0, 1.0, 1.0)
    'The text outline color. This is used only if :py:attr:`outline_enabled` is set.\n\nDefault: ``(1.0, 1.0, 1.0)``'
    outline_enabled: bool = False
    'Enables the painting of a font outline to make the text easier to read.\n\nDefault: ``False``'
    source_pipeline: Optional[ovito.pipeline.Pipeline] = None
    'The :py:class:`Pipeline` that is queried to obtain the attribute values referenced in the text string. See the :py:attr:`text` property for more information.'
    text: str = 'Text label'
    'The text string to be rendered.\n\nThe string can contain placeholder references to dynamically computed attributes of the form ``[attribute]``, which will be replaced by their actual value before rendering the text label. Attributes are taken from the pipeline output of the :py:class:`Pipeline` assigned to the overlay\'s :py:attr:`source_pipeline` property. \n\nThe following example demonstrates how to insert a text label that displays the number of currently selected particles: \n\n```python\n  from ovito.io import import_file\n  from ovito.vis import TextLabelOverlay, Viewport\n  from ovito.modifiers import ExpressionSelectionModifier\n  \n  # Import a simulation dataset and select some atoms based on their potential energy:\n  pipeline = import_file("input/simulation.dump")\n  pipeline.add_to_scene()\n  pipeline.modifiers.append(ExpressionSelectionModifier(expression="peatom > -4.2"))\n  \n  # Create the overlay. Note that the text string contains a reference\n  # to an output attribute of the ExpressionSelectionModifier.\n  overlay = TextLabelOverlay(text="Number of selected atoms: [ExpressionSelection.count]")\n  # Specify the source of dynamically computed attributes.\n  overlay.source_pipeline = pipeline\n  \n  # Attach overlay to a newly created viewport:\n  viewport = Viewport(type=Viewport.Type.Top)\n  viewport.overlays.append(overlay)\n```\n\n.. tip::\n\n  You can embed HTML and CSS markup elements in the string to further control the formatting and styling of the text.\n\nDefault: ``"Text label"``'
    text_color: Color = (0.0, 0.0, 0.5)
    'The text rendering color.\n\nDefault: ``(0.0, 0.0, 0.5)``'

@dataclass(kw_only=True)
class DataVis:
    """Abstract base class for visualization elements that are responsible for the visual appearance of data objects in the visualization. Some `DataObjects` are associated with a corresponding :py:class:`DataVis` element (see `DataObject.vis` property), making them *visual* data objects that appear in the viewports and in rendered images. 

See the :py:mod:`ovito.vis` module for the list of visual element types available in OVITO."""
    enabled: bool = True
    'Boolean flag controlling the visibility of the data. If set to ``False``, the data will not be visible in the viewports or in rendered images.\n\nDefault: ``True``'
    title: str = ''
    "A custom title string assigned to the visual element, which will show in the pipeline editor of OVITO. \n\nDefault: ``''``"

@dataclass(kw_only=True)
class SimulationCellVis(DataVis):
    """Base: :py:class:`ovito.vis.DataVis`

Controls the visual appearance of the simulation cell. 
An instance of this class is attached to the :py:class:`SimulationCell` object 
and can be accessed through its :py:attr:`vis` field. 
See also the corresponding user manual page for this visual element. 

The following example script demonstrates how to change the display line width and rendering color of the simulation cell 
loaded from an input simulation file:

```python
  from ovito.io import import_file
  
  pipeline = import_file("input/simulation.dump")
  pipeline.add_to_scene()
  
  cell_vis = pipeline.source.data.cell.vis
  cell_vis.line_width = 1.3
  cell_vis.rendering_color = (0.0, 0.0, 0.8)
```"""
    line_width: float = 0.0
    'The width of the simulation cell line (in simulation units of length).\n\nDefault: 0.14% of the simulation box diameter'
    render_cell: bool = True
    "Boolean flag controlling the cell's visibility in rendered images. If ``False``, the cell will only be visible in the interactive viewports. \n\nDefault: ``True``"
    rendering_color: Color = (0.0, 0.0, 0.0)
    'The line color used when rendering the cell.\n\nDefault: ``(0.0, 0.0, 0.0)``'

@dataclass(kw_only=True)
class ParticlesVis(DataVis):
    """Base: :py:class:`ovito.vis.DataVis`

This type of visual element is responsible for rendering particles and is attached to every :py:class:`Particles` data object. 
You can access the element through the :py:attr:`vis` field of the data object and adjust its parameters to control the visual
appearance of particles in rendered images:

```python
  from ovito.io import import_file
  from ovito.vis import ParticlesVis
  
  pipeline = import_file("input/simulation.dump")
  pipeline.add_to_scene()
  
  vis_element = pipeline.compute().particles.vis
  vis_element.shape = ParticlesVis.Shape.Square
```

See also the corresponding user manual page for more information on this visual element."""

    class Shape(enum.Enum):
        """"""
        Unspecified = enum.auto()
        Sphere = enum.auto()
        Box = enum.auto()
        Circle = enum.auto()
        Square = enum.auto()
        Cylinder = enum.auto()
        Spherocylinder = enum.auto()
        Mesh = enum.auto()
    radius: float = 1.2
    'The standard display radius of particles. This value is only used if no per-particle or per-type radii have been set. A per-type radius can be set via `ParticleType.radius`. An individual display radius can be assigned to each particle by setting the ``Radius`` particle property, e.g. using the :py:class:`ComputePropertyModifier`. \n\nDefault: ``1.2``'
    scaling: float = 1.0
    'Global scaling factor that is applied to every particle being rendered. \n\nDefault: ``1.0``'
    shape: ParticlesVis.Shape = Shape.Sphere
    'The kind of shape to use when rendering the particles. Supported modes are:\n\n   * ``ParticlesVis.Shape.Sphere`` (default) \n   * ``ParticlesVis.Shape.Box``\n   * ``ParticlesVis.Shape.Circle``\n   * ``ParticlesVis.Shape.Square``\n   * ``ParticlesVis.Shape.Cylinder``\n   * ``ParticlesVis.Shape.Spherocylinder``\n\n\nMode ``Sphere`` includes ellipsoid and superquadric particle geometries, which are activated by the presence of the ``Aspherical Shape`` and ``Superquadric Roundness`` particle properties. Mode ``Box`` renders cubic as well as non-cubic boxes depending on the presence of the ``Aspherical Shape`` particle property. \n\nNote that this parameter controls the standard shape to be used for all particles. You can override this default setting on a per-particle type basis by setting the `ParticleType.shape` property to a different value.'

@dataclass(kw_only=True)
class BondsVis(DataVis):
    """Base: :py:class:`ovito.vis.DataVis`

A visualization element that renders cylindrical bonds between particles. 
An instance of this class is attached to every :py:class:`Bonds` data object 
and controls the visual appearance of the bonds in rendered images. 

See also the corresponding user manual page for this visual element. 
If you import a simulation file containing bonds, you can subsequently access the :py:class:`BondsVis` element 
through the :py:attr:`vis` field of the bonds data object, which is part in the data collection managed 
by the pipeline's :py:attr:`source` object:

```python
  pipeline = import_file('input/bonds.data.gz', atom_style='bond')
  pipeline.add_to_scene()
  bonds_vis = pipeline.source.data.particles.bonds.vis
  bonds_vis.width = 0.4
```

In cases where the :py:class:`Bonds` data is dynamically generated by a modifier, e.g. the :py:class:`CreateBondsModifier`, 
the :py:class:`BondsVis` element is managed by the modifier:

```python
  modifier = CreateBondsModifier(cutoff = 2.8)
  modifier.vis.flat_shading = True
  pipeline.modifiers.append(modifier)
```"""

    class ColoringMode(enum.Enum):
        """"""
        Uniform = enum.auto()
        ByBondType = enum.auto()
        ByParticle = enum.auto()
    color: Color = (0.6, 0.6, 0.6)
    'The uniform color of bonds. This parameter is only used if :py:attr:`coloring_mode` is set to ``Uniform`` and if the bonds do not possess a bond property named ``Color``, i.e., explicit per-bond colors were not provided. \n\nDefault: ``(0.6, 0.6, 0.6)``'
    coloring_mode: BondsVis.ColoringMode = ColoringMode.ByParticle
    "Selects how the color of each bond is determined. Available modes:\n\n  * ``BondsVis.ColoringMode.Uniform``: Use the specified :py:attr:`color` value to render all bonds.\n  * ``BondsVis.ColoringMode.ByBondType``: Use each bond type's :py:attr:`color` to render the bonds.\n  * ``BondsVis.ColoringMode.ByParticle``: Adopt the colors of the particles connect by the bonds.\n\n\n  If the :py:class:`Bonds` object being rendered contains the ``Color`` property, then the visual element will directly use these explicit per-bond RGB values   for rendering the bonds. The :py:attr:`coloring_mode` parameter is ignored in this case. \n\nDefault: ``BondsVis.ColoringMode.ByParticle``"
    flat_shading: bool = False
    'Boolean flag that activates a flat-shaded representation of the bonds instead of the normal cylinder representation. \n\nDefault: ``False``'
    width: float = 0.4
    'The display width of bonds (in natural length units).\n\nDefault: ``0.4``'

@dataclass(kw_only=True)
class DislocationVis(DataVis):
    """Base: :py:class:`ovito.vis.DataVis`

Controls the visual appearance of dislocation lines extracted by a :py:class:`DislocationAnalysisModifier`. An instance of this class is attached to every :py:class:`DislocationNetwork` data object. 

See also the corresponding user manual page for more information on this visual element."""

    class ColoringMode(enum.Enum):
        """"""
        ByDislocationType = enum.auto()
        ByBurgersVector = enum.auto()
        ByCharacter = enum.auto()

    class Shading(enum.Enum):
        """A simple attribute-based namespace.

SimpleNamespace(**kwargs)"""
        Normal = enum.auto()
        Flat = enum.auto()
    burgers_vector_color: Color = (0.7, 0.7, 0.7)
    'The color of Burgers vector arrows.\n\nDefault: ``(0.7, 0.7, 0.7)``'
    burgers_vector_scaling: float = 1.0
    'The scaling factor applied to displayed Burgers vectors. This can be used to exaggerate the arrow size.\n\nDefault: ``1.0``'
    burgers_vector_width: float = 0.6
    'Specifies the width of Burgers vector arrows (in length units).\n\nDefault: ``0.6``'
    coloring_mode: DislocationVis.ColoringMode = ColoringMode.ByDislocationType
    'Selects the coloring mode for dislocation lines. \nSupported modes are:\n\n   * ``DislocationVis.ColoringMode.ByDislocationType`` (default) \n   * ``DislocationVis.ColoringMode.ByBurgersVector``\n   * ``DislocationVis.ColoringMode.ByCharacter``'
    line_width: float = 1.0
    'Controls the display width (in units of length of the simulation) of dislocation lines.\n\nDefault: ``1.0``'
    shading: DislocationVis.Shading = Shading.Normal
    'The shading style used for the lines.\nPossible values:\n\n   * ``DislocationVis.Shading.Normal`` (default) \n   * ``DislocationVis.Shading.Flat``'
    show_burgers_vectors: bool = False
    'Boolean flag that enables the display of Burgers vector arrows.\n\nDefault: ``False``'
    show_line_directions: bool = False
    'Boolean flag that enables the visualization of line directions.\n\nDefault: ``False``'

@dataclass(kw_only=True)
class SurfaceMeshVis(DataVis):
    """Base: :py:class:`ovito.vis.DataVis`

Controls the visual appearance of a :py:class:`SurfaceMesh` object, which is typically generated by modifiers such as 
:py:class:`ConstructSurfaceModifier` or :py:class:`CreateIsosurfaceModifier`. 
See also the corresponding user manual page for more information on this visual element."""

    class ColorMappingMode(enum.Enum):
        """"""
        Uniform = enum.auto()
        Vertex = enum.auto()
        Face = enum.auto()
        Region = enum.auto()
    cap_color: Color = (0.8, 0.8, 1.0)
    'The RGB display color of the cap polygons at periodic boundaries.\n\nDefault: ``(0.8, 0.8, 1.0)``'
    cap_transparency: float = 0.0
    'The level of transparency of the displayed cap polygons. The valid range is 0.0 -- 1.0  (fully opaque to fully transparent).\n\nDefault: ``0.0``'
    clip_at_domain_boundaries: bool = False
    'Controls whether the mesh gets clipped at *non-periodic* cell boundaries during visualization. This option plays a role only if the mesh extends beyond the boundaries of the finite :py:attr:`domain` of the :py:class:`SurfaceMesh`; it does *not* apply to intersections of the surface with *periodic* boundaries of the simulation domain (see :py:attr:`pbc`), at which the surface mesh always gets wrapped back into primary cell image for visualization. \n\nIf the mesh extends beyond the (non-periodic) domain boundaries, you can use this option to restrict the display of the mesh to those parts that are located inside the domain. \n\n.. figure:: ../introduction/graphics/surface_mesh_vis_clipping_off.png\n  :figwidth: 20%\n  :align: left\n\n  Clipping off\n\n.. figure:: ../introduction/graphics/surface_mesh_vis_clipping_on.png\n  :figwidth: 20%\n  :align: left\n\n  Clipping on\n\nDefault: ``False``'
    color_mapping_gradient: ovito.modifiers.ColorCodingModifier.Gradient = ovito.modifiers.ColorCodingModifier.Rainbow()
    'The color gradient for mapping scalar property values taken from the selected :py:attr:`color_mapping_property` to corresponding RGB color values (*color transfer function*). See the `ColorCodingModifier.gradient` parameter for a list of available color gradient types. \n\nDefault: ``ColorCodingModifier.Rainbow()``'
    color_mapping_interval: Tuple[float, float] = (0.0, 0.0)
    'Specifies the range of input values from the selected :py:attr:`color_mapping_property` getting mapped to corresponding RGB values by the selected :py:attr:`color_mapping_gradient`. The tuple defines the start and end of the linear interval that is translated to pseudo-colors by the color map. Input property values not within of the interval get mapped to the marginal colors of the selected color map. \n\nDefault: ``(0.0, 0.0)``'
    color_mapping_mode: SurfaceMeshVis.ColorMappingMode = ColorMappingMode.Uniform
    "Controls how the color of the surface is computed. Using pseudo-coloring you can visualize a local property of the surface. \n\nAvailable modes:\n\n  * ``SurfaceMeshVis.ColorMappingMode.Uniform``: Uses :py:attr:`surface_color` for rendering the entire surface with a constant color (disables local pseudo-coloring).\n  * ``SurfaceMeshVis.ColorMappingMode.Vertex``: Colors the surface based on a local property associated with the surface's :py:attr:`vertices`.\n  * ``SurfaceMeshVis.ColorMappingMode.Face``: Colors the surface based on a local property associated with the surface's :py:attr:`faces`.\n  * ``SurfaceMeshVis.ColorMappingMode.Region``: Colors the surface based on a local property associated with the surface's :py:attr:`regions`.\n\n\nDefault: ``SurfaceMeshVis.ColorMappingMode.Uniform``\n\n\n  This setting has no effect if the :py:attr:`vertices`, :py:attr:`faces` or :py:attr:`regions` of the :py:class:`SurfaceMesh` have   explicit colors associated with them, i.e., if the ``Color`` property exists in one of these property containers."
    color_mapping_property: str = ''
    "The name of the property to be used for coloring the mesh to visualize the local values of this property on the surface. If the :py:class:`Property` has several components, then the name must be followed by a component name, e.g. ``'Orientation.X'``. Whether the property is taken from the :py:attr:`vertices`, :py:attr:`faces`, or :py:attr:`regions` of the :py:class:`SurfaceMesh` being rendered is determined by the selected :py:attr:`color_mapping_mode`. \n\nNumeric values from the source property are mapped to corresponding RGB-based pseudo-colors by first normalizing them according to the specified :py:attr:`color_mapping_interval` and then applying the selected :py:attr:`color_mapping_gradient`. \n\nNote that, if the ``Color`` property is defined on the surface's :py:attr:`vertices`, :py:attr:`faces`, or :py:attr:`regions`, then the visual element directly uses these explicit RGB values to render the surface. No color mapping takes place in this case and the :py:attr:`color_mapping_property`, :py:attr:`color_mapping_mode` and :py:attr:`surface_color` parameters are all ignored. \n\nDefault: ``''``"
    highlight_edges: bool = False
    'Activates the highlighted rendering of the polygonal edges of the mesh.\n\nDefault: ``False``'
    reverse_orientation: bool = False
    'Flips the orientation of the surface. This affects the generation of cap polygons as well.\n\nDefault: ``False``'
    show_cap: bool = True
    'Controls the visibility of cap polygons, which are created at the intersection of the surface mesh with the `domain` boundaries. This option has an effect only if the surface mesh being rendered is *closed*, which means there are well-defined "interior" and "exterior" regions of space separated by the surface manifold. \n\nDefault: ``True``\n\n\n.. seealso:: `SurfaceMeshTopology.is_closed`'
    smooth_shading: bool = True
    'Enables smooth shading of the triangulated surface mesh.\n\nDefault: ``True``'
    surface_color: Color = (1.0, 1.0, 1.0)
    'The RGB display color of the surface mesh. Used only if :py:attr:`color_mapping_mode` is set to uniform coloring. \n\nDefault: ``(1.0, 1.0, 1.0)``'
    surface_transparency: float = 0.0
    'The level of transparency of the displayed surface. The valid range is 0.0 -- 1.0 (fully opaque to fully transparent).\n\nDefault: ``0.0``'

@dataclass(kw_only=True)
class TrajectoryVis(DataVis):
    """Base: :py:class:`ovito.vis.DataVis`

Controls the visual appearance of particle trajectory lines. An instance of this class is attached 
to every :py:class:`TrajectoryLines` data object. 

You typically create trajectory lines by inserting the :py:class:`GenerateTrajectoryLinesModifier`
into a data pipeline. The modifier owns a :py:class:`TrajectoryVis` element, which is used for 
visualizing the generated trajectory lines. You can access it through the modifier's :py:attr:`vis` field."""

    class Shading(enum.Enum):
        """"""
        Normal = enum.auto()
        Flat = enum.auto()
    color: Color = (0.6, 0.6, 0.6)
    'The uniform color to be used for rendering the trajectory lines. This parameter is ignored if pseudo-coloring of the lines has been activated by setting a :py:attr:`color_mapping_property`. \n\nDefault: ``(0.6, 0.6, 0.6)``'
    color_mapping_gradient: ovito.modifiers.ColorCodingModifier.Gradient = ovito.modifiers.ColorCodingModifier.Rainbow()
    'The color gradient used to map scalar property values from the selected :py:attr:`color_mapping_property` to corresponding RGB output values (also called *color transfer function*). See the `ColorCodingModifier.gradient` parameter for a list of available color gradient types. \n\nDefault: ``ColorCodingModifier.Rainbow()``'
    color_mapping_interval: Tuple[float, float] = (0.0, 0.0)
    'Specifies the range of input values from the selected :py:attr:`color_mapping_property` getting mapped to corresponding RGB values by the selected :py:attr:`color_mapping_gradient`. The tuple defines the start and end of the linear interval that is translated to pseudo-colors by the color map. Input property values not within of the interval get mapped to the marginal colors of the selected color map. \n\nDefault: ``(0.0, 0.0)``'
    color_mapping_property: str = ''
    "The name of the :py:class:`TrajectoryLines` property to be used for pseudo-coloring the lines according to the scalar values of this property. If the :py:class:`Property` consists of several vector components, then the name must be followed by a specific component name, e.g. ``'Velocity.Z'``. \n\nTypically, this parameter should be set to the name of the particle property which was sampled during line tracing by the :py:class:`GenerateTrajectoryLinesModifier`. See its :py:attr:`sample_particle_property` parameter for an example. \n\nNumeric values from the selected source property are mapped to corresponding RGB values by first normalizing them according to the specified :py:attr:`color_mapping_interval` and then applying the selected :py:attr:`color_mapping_gradient`. \n\n  If the :py:class:`TrajectoryLines` object being rendered has a property named ``Color``, then this explicit line coloring   is used. No color mapping takes place in this case, and the :py:attr:`color_mapping_property` and :py:attr:`color` parameters of the visual element are ignored. \n\nDefault: ``''``"
    shading: TrajectoryVis.Shading = Shading.Flat
    'The shading style used for trajectory lines.\nPossible values:\n\n   * ``TrajectoryVis.Shading.Normal`` \n   * ``TrajectoryVis.Shading.Flat`` (default)'
    upto_current_time: bool = False
    'If ``True``, trajectory lines are only rendered up to the particle positions at the current animation time. Otherwise, the complete trajectory lines are displayed.\n\nDefault: ``False``'
    width: float = 0.2
    'The display width of trajectory lines.\n\nDefault: ``0.2``'
    wrapped_lines: bool = False
    'If ``True``, the continuous trajectory lines will automatically be wrapped back into the simulation box during rendering. Thus, they will be shown as several discontinuous segments if they cross periodic boundaries of the simulation box. \n\nDefault: ``False``'

@dataclass(kw_only=True)
class TriangleMeshVis(DataVis):
    """Base: :py:class:`ovito.vis.DataVis`

Controls the visual appearance of a :py:class:`TriangleMesh`. 
See also the corresponding user manual page for more information on this visual element."""
    backface_culling: bool = False
    'Controls whether triangle faces facing away from the viewer are not rendered. \n\nDefault: ``False``'
    color: Color = (0.85, 0.85, 1.0)
    "The uniform RGB color of the triangle mesh, which is used for rendering if the mesh's faces or vertices have no local colors associated with them. RGB color components must be in the range 0--1.\n\nDefault: ``(0.85, 0.85, 1.0)``"
    highlight_edges: bool = False
    'Highlights the polygonal edges of the mesh by rendering a wireframe lines along those edges that have been marked as visible.\n\nDefault: ``False``'
    transparency: float = 0.0
    'The degree of semi-transparency of the rendered mesh. Valid parameter range is 0.0 -- 1.0.\n\nDefault: ``0.0``'

@dataclass(kw_only=True)
class VectorVis(DataVis):
    """Base: :py:class:`ovito.vis.DataVis`

This kind of visual element renders arrow glyphs for visualizing vectorial data stored in a :py:class:`Property` object. 
See also the corresponding user manual page for more information.

A vector property is any :py:class:`Property` array with data type ``float`` and three components per element. The :py:class:`VectorVis` element supports visualization of 
vector properties that are stored of the following :py:class:`PropertyContainer` types: :py:class:`Particles`, :py:class:`Bonds`,
`SurfaceMesh.vertices`, `SurfaceMesh.faces`, and :py:class:`VoxelGrid`.

The standard particle properties ``Force``, ``Displacement``, ``Dipole``, and ``Velocity`` already have an existing :py:class:`VectorVis` element
attached to them, which is disabled by default. You must `enable`  it for the arrow glyphs to be displayed, e.g.:

```python
  pipeline = import_file('input/simulation.dump')
  pipeline.add_to_scene()
  vector_vis = pipeline.compute().particles.forces.vis
  vector_vis.enabled = True  # This activates the display of arrow glyphs
  vector_vis.color = (1,0,0)
```

In this example, the atomistic :py:attr:`forces` were loaded as particle property named ``Force`` from the imported simulation file, 
Parameters such as :py:attr:`color`, :py:attr:`width`, and :py:attr:`flat_shading` of the :py:class:`VectorVis` element control the visual appearance of the arrow glyphs in rendered images. 

Some modifiers in OVITO dynamically add new vector properties to particles. For instance, the :py:class:`CalculateDisplacementsModifier` 
creates the ``Displacement`` property and automatically attaches a :py:class:`VectorVis` element to it in case you want to visualize the displacements. 
The visual element is part of the modifier in this case: 

```python
  modifier = CalculateDisplacementsModifier()
  pipeline.modifiers.append(modifier)
  modifier.vis.enabled = True  # This activates the display of displacement vectors
  modifier.vis.flat_shading = False
```

If you are writing your own modifier function to compute a vector property, and you want to visualize that property 
using arrow glyphs, you need to construct a :py:class:`VectorVis` element and attach it to the newly created :py:class:`Property` object. For example: 

```python
  def modify(frame, data, vector_vis=VectorVis(alignment=VectorVis.Alignment.Center, color=(1.0, 0.0, 0.4))):
  
      # Add a new vector property to the particles:
      vector_data = numpy.random.random_sample(size=(data.particles.count, 3))
      property = data.particles_.create_property('My Vector Property', data=vector_data)
  
      # Attach the visual element to the output property:
      property.vis = vector_vis  
```

Setting up the visual element as an additional parameter of the ``modify()`` function provides two advantages: 
Only a single instance is created, which survives multiple invocations of the modifier function, and OVITO Pro displays the element's 
parameter panel in the UI."""

    class Alignment(enum.Enum):
        """"""
        Base = enum.auto()
        Center = enum.auto()
        Head = enum.auto()
    alignment: VectorVis.Alignment = Alignment.Base
    'Controls the positioning of the arrows glyphs with respect to the base points, e.g., the particle positions.\nPossible values:\n\n   * ``VectorVis.Alignment.Base`` (default) \n   * ``VectorVis.Alignment.Center``\n   * ``VectorVis.Alignment.Head``'
    color: Color = (1.0, 1.0, 0.0)
    'The uniform display color of arrow glyphs. This parameter is *not* used if pseudo-color mapping is enabled through the :py:attr:`color_mapping_property` option or when the ``Vector Color`` property was set for the particles. \n\nDefault: ``(1.0, 1.0, 0.0)``'
    color_mapping_gradient: ovito.modifiers.ColorCodingModifier.Gradient = ovito.modifiers.ColorCodingModifier.Rainbow()
    'The color gradient used to map scalar property values from the selected :py:attr:`color_mapping_property` to corresponding RGB output values (*color transfer function*). See the `ColorCodingModifier.gradient` parameter for a list of available color gradient types. \n\nDefault: ``ColorCodingModifier.Rainbow()``'
    color_mapping_interval: Tuple[float, float] = (0.0, 0.0)
    'Specifies the range of input values from the selected :py:attr:`color_mapping_property` getting mapped to corresponding RGB values by the selected :py:attr:`color_mapping_gradient`. The tuple defines the start and end of the linear interval that is translated to pseudo-colors by the color map. Input property values not within of the interval get mapped to the marginal colors of the selected color map. \n\nDefault: ``(0.0, 0.0)``'
    color_mapping_property: str = ''
    "The name of a scalar property to be used for coloring the vector glyphs. If the :py:class:`Property` has several components, then the name must be followed by a component name, e.g. ``'Displacement.Z'``. \n\nNumeric values from the selected source property are mapped to corresponding RGB values by first normalizing them according to the specified :py:attr:`color_mapping_interval` and then applying the selected :py:attr:`color_mapping_gradient`. \n\nNote that, if a :py:class:`Particles` object is being rendered that has a property named ``Vector Color``, then these explicit per-particle colors will be used for rendering the vector glyphs. No color mapping takes place in this case and the :py:attr:`color_mapping_property` and :py:attr:`color` parameters of the visual element are ignored. \n\nDefault: ``''``"
    flat_shading: bool = True
    'Switches between a flat rendering style for the arrows and a three-dimensional representation. \n\nDefault: ``True``'
    offset: Vector3 = (0.0, 0.0, 0.0)
    'Additional offset by which all arrows are displaced. This can be used to move the arrows in front of or behind the particles and avoid occlusions. \n\nDefault: ``(0.0, 0.0, 0.0)``'
    reverse: bool = False
    'Boolean flag which reverves the direction the arrow glyphs.\n\nDefault: ``False``'
    scaling: float = 1.0
    'The uniform scaling factor applied to arrow glyphs. \n\nDefault: ``1.0``'
    transparency: float = 0.0
    'The level of semi-transparency for rendering the arrows. The valid parameter range is 0.0 -- 1.0 (fully opaque to fully transparent).\n\nDefault: ``0.0``'
    width: float = 0.5
    'Controls the width of arrows (in simulation units of length).\n\nDefault: ``0.5``'

@dataclass(kw_only=True)
class VoxelGridVis(DataVis):
    """Base: :py:class:`ovito.vis.DataVis`

This visual element controls the appearance of a :py:class:`VoxelGrid` data object, which is typically generated by the 
:py:class:`SpatialBinningModifier` or imported directly from files containing volumetric data. The visual element is responsible for rendering 
the outer boundaries of the grid, i.e., showing only the voxel cells at the surface but not in the interior of the grid volume.

See also the corresponding user manual page for further information on this visual element."""
    color_mapping_gradient: ovito.modifiers.ColorCodingModifier.Gradient = ovito.modifiers.ColorCodingModifier.Rainbow()
    'The color gradient used to map scalar property values from the selected :py:attr:`color_mapping_property` to corresponding RGB output values (also called *color transfer function*). See the `ColorCodingModifier.gradient` parameter for a list of available color gradient types. \n\nDefault: ``ColorCodingModifier.Rainbow()``'
    color_mapping_interval: Tuple[float, float] = (0.0, 0.0)
    'Specifies the range of input values from the selected :py:attr:`color_mapping_property` getting mapped to corresponding RGB values by the selected :py:attr:`color_mapping_gradient`. The tuple defines the start and end of the linear interval that is translated to pseudo-colors by the color map. Input property values not within of the interval get mapped to the marginal colors of the selected color map. \n\nDefault: ``(0.0, 0.0)``'
    color_mapping_property: str = ''
    "The name of the :py:class:`VoxelGrid` scalar property to be used for coloring the grid cells. If the :py:class:`Property` has several components, then the name must be followed by a component name, e.g. ``'Velocity.Z'``. \n\nNumeric values from the selected source property are mapped to corresponding RGB cell colors by first normalizing them according to the specified :py:attr:`color_mapping_interval` and then applying the selected :py:attr:`color_mapping_gradient`. \n\nNote that, if the :py:class:`VoxelGrid` being rendered contains the ``Color`` property, then the visual element directly uses these RGB values to render the grid cells. No color mapping takes place in this case and the :py:attr:`color_mapping_property` parameter is ignored. \n\nDefault: ``''``"
    highlight_grid_lines: bool = True
    'Controls the rendering of grid lines separating the voxel cells.\n\nDefault: ``True``'
    interpolate_colors: bool = False
    'Controls whether the (pseudo)colors of the voxel cells visible on the boundary of the grid are smoothly interpolated between neighboring cells. \n\nDefault: ``False``'
    transparency: float = 0.0
    'The level of transparency of the displayed grid surface. The valid parameter range is 0.0 -- 1.0 (fully opaque to fully transparent).\n\nDefault: ``0.0``'

@dataclass(kw_only=True)
class JupyterViewportWidget(ipywidgets.DOMWidget):
    antialiasing: bool = True
    picking: bool = False
    vr_scale: float = 0.0

    def refresh(self) -> None:
        ...

@dataclass(kw_only=True)
class Viewport:
    """A viewport is a "window" to the three-dimensional scene, showing the scene from the point of view of a virtual camera. 

The virtual camera's position and orientation are given by the :py:attr:`camera_pos` and :py:attr:`camera_dir` properties. Additionally, the :py:attr:`type` field allows you to switch between perspective and parallel projection modes or reset the camera to one of the standard axis-aligned orientations (top, left, front, etc.). The :py:meth:`.zoom_all` method repositions the camera automatically such that the entire scene becomes fully visible within the viewport. See also the documentation of the Adjust View dialog of OVITO to learn more about these camera-related settings. 

After the viewport's virtual camera has been set up, you can render an image or movie using the :py:meth:`.render_image` and :py:meth:`.render_anim` methods. For example: 

```python
  from ovito.io import import_file
  from ovito.vis import Viewport, TachyonRenderer
  
  pipeline = import_file('input/simulation.dump')
  pipeline.add_to_scene()
  
  vp = Viewport(type = Viewport.Type.Ortho, camera_dir = (2, 1, -1))
  vp.zoom_all()
  vp.render_image(filename='output/simulation.png', 
                  size=(320, 240), 
                  renderer=TachyonRenderer())
```

Furthermore, so-called *overlays* may be added to a viewport. Overlays are function objects that draw additional two-dimensional graphics or text on top of or behind the rendered scene, e.g. coordinate axes or a color legend. See the documentation of the :py:attr:`overlays` and :py:attr:`underlays` lists for more information."""

    class Type(enum.Enum):
        """"""
        NONE = enum.auto()
        Perspective = enum.auto()
        Ortho = enum.auto()
        Top = enum.auto()
        Bottom = enum.auto()
        Front = enum.auto()
        Back = enum.auto()
        Left = enum.auto()
        Right = enum.auto()
    camera_dir: Vector3 = (0.0, 0.0, 1.0)
    "The viewing direction vector of the viewport's camera."
    camera_pos: Vector3 = (0.0, 0.0, 0.0)
    "The position of the viewport's camera in the three-dimensional scene."
    camera_up: Vector3 = (0.0, 0.0, 0.0)
    "Direction vector specifying which coordinate axis will point upward in rendered images. Set this parameter to a non-zero vector in order to rotate the camera around the viewing direction and align the vertical direction in rendered images with a different simulation coordinate axis. If set to ``(0,0,0)``, then the upward axis is determined by the current user settings set in OVITO's application settings dialog (z-axis by default). \n\nDefault: ``(0.0, 0.0, 0.0)``"
    fov: float = 100.0
    "The field of view of the viewport's camera. For perspective projections this is the camera's angle in the vertical direction (in radians). For orthogonal projections this is the visible range in the vertical direction (in world units)."
    type: Viewport.Type = Type.NONE
    'Specifies the projection type of the viewport. The following standard projections are available:\n\n  * ``Viewport.Type.Perspective``\n  * ``Viewport.Type.Ortho``\n  * ``Viewport.Type.Top``\n  * ``Viewport.Type.Bottom``\n  * ``Viewport.Type.Front``\n  * ``Viewport.Type.Back``\n  * ``Viewport.Type.Left``\n  * ``Viewport.Type.Right``\n\nThe first two types (``Perspective`` and ``Ortho``) allow you to set up custom views with arbitrary camera orientations.'

    @property
    def overlays(self) -> MutableSequence[ViewportOverlay]:
        """The list of :py:class:`ViewportOverlay` objects currently attached to this viewport. Overlays render two-dimensional graphics on top of the three-dimensional scene. See the following overlay types for more information:

   * :py:class:`TextLabelOverlay`
   * :py:class:`ColorLegendOverlay`
   * :py:class:`CoordinateTripodOverlay`
   * :py:class:`PythonViewportOverlay`


To attach a new overlay to the viewport, use the list's ``append()`` method:

```python
  from ovito.vis import Viewport, CoordinateTripodOverlay
  
  vp = Viewport(type = Viewport.Type.Ortho)
  tripod = CoordinateTripodOverlay(size = 0.07)
  vp.overlays.append(tripod)
```

The viewport also has an :py:attr:`underlays` list. :py:class:`ViewportOverlay` objects inserted into that list will be rendered *behind* the 3d objects of the scene."""
        ...

    @property
    def underlays(self) -> MutableSequence[ViewportOverlay]:
        """The list of :py:class:`ViewportOverlay` objects currently attached to this viewport. They render two-dimensional graphics *behind* the three-dimensional scene. See the :py:attr:`overlays` list for further information."""
        ...

    def create_qt_widget(self, parent: Optional[PySide6.QtWidgets.QWidget]=None) -> PySide6.QtWidgets.QWidget:
        """Creates an interactive visual widget displaying the three-dimensional scene as seen through this virtual viewport.
The method creates an interactive window accepting mouse inputs from the user similar to the viewport windows
of the OVITO desktop application. You can use this method to develop custom user interfaces based on the Qt cross-platform framework
that integrate OVITO's functionality and display the output of a data pipeline.

:param parent: An optional Qt widget that should serve as parent of the newly created viewport widget.
:returns: A new `QWidget <https://doc.qt.io/qtforpython/PySide6/QtWidgets/QWidget.html>`__ displaying the three-dimensional scene as seen through the virtual viewport.

The Qt widget returned by this method is linked to this :py:class:`Viewport` instance.
Any changes your Python script subsequently makes to the non-visual :py:class:`Viewport` instance,
for example setting :py:attr:`camera_pos` or :py:attr:`camera_dir`, will automatically be reflected by the
visual viewport widget. Vice versa will interactions of the user with the viewport widget
automatically lead to changes of the corresponding fields of the :py:class:`Viewport` instance.

The following short example program demonstrates the use of the :py:meth:`create_qt_widget` method. Please see the
`Qt for Python <https://doc.qt.io/qtforpython/>`__ documentation for more information on how to create graphical
user interfaces using the Qt framework.

.. seealso:: :ref:`example_trajectory_viewer`

```python
  import sys, os
  from PySide6.QtCore import QEventLoop
  from PySide6.QtWidgets import QApplication
  
  # Create a global Qt application object - unless we are running inside the 'ovitos' interpreter,
  # which automatically initializes a Qt application object.
  if not QApplication.instance():
      app = QApplication(sys.argv)
  
  # Note: Import the ovito module AFTER the QApplication object has been created.
  # Otherwise, the ovito module automatically creates its own QCoreApplication object,
  # which wouldn't let us display a GUI.
  from ovito.io import import_file
  from ovito.vis import Viewport
  
  # Import model and add it to visualization scene.
  pipeline = import_file('input/simulation.dump')
  pipeline.add_to_scene()
  
  # Create a virtual Viewport.
  vp = Viewport(type=Viewport.Type.Perspective, camera_dir=(2, 1, -1))
  
  # Create a visible GUI widget associated with the viewport.
  widget = vp.create_qt_widget()
  widget.resize(500, 400)
  widget.setWindowTitle('OVITO Viewport Demo')
  widget.show()
  vp.zoom_all((widget.width(), widget.height()))
  
  # Shutdown application when the user closes the viewport widget.
  widget.destroyed.connect(QApplication.instance().quit)
  
  # Start the Qt event loop.
  if 'app' in locals():
      # When a standard Python interpreter is used to run this script, start the
      # application's main event loop to begin UI event processing.
      sys.exit(app.exec())
  else:
      # When running this script with the 'ovitos' interpreter, a Qt event loop is already active.
      # Start a nested event loop then, just for this little demo program.
      eventLoop = QEventLoop()
      widget.destroyed.connect(eventLoop.quit) # Stop event loop when user closes the viewport widget.
      eventLoop.exec()
```"""
        ...

    def create_jupyter_widget(self, antialiasing: bool=True, picking: bool=False, vr_scale: float=0.0, layout: ipywidgets.Layout=ipywidgets.Layout(width='400px', height='200px')) -> JupyterViewportWidget:
        """Creates an interactive widget for embedding in a Jupyter notebook, which displays the 3d scene as seen through this virtual viewport.
The method returns an interactive notebook element, which accepts mouse inputs similar to the viewport windows
of the OVITO desktop application. It may be necessary to call :func:`display <ipython:IPython.display.display>` in order to show the widget:

.. code-block::

    vp = Viewport(type=Viewport.Type.Perspective, camera_dir=(0.5, 1.0, -0.4))
    vp.zoom_all()
    widget = vp.create_jupyter_widget(picking=True)
    display(widget)

The `Jupyter widget <https://ipywidgets.readthedocs.io/en/stable/>`__ returned by this method is permanently linked to this :py:class:`Viewport` instance.
Any changes you subsequently make to the non-visual :py:class:`Viewport`, for example, setting its :py:attr:`camera_pos` or :py:attr:`camera_dir`, will be
reflected by the visual viewport widget. Vice versa do all user interactions with the viewport widget
update the corresponding fields of the :py:class:`Viewport` object.

.. important::

    This method requires the `ipywidgets <https://ipywidgets.readthedocs.io/en/stable/user_install.html>`__ Python package.
    Please install this package in the Python interpreter used by your Jupyter environment.

:param bool antialiasing: Enables multisample anti-aliasing to reduce jagged edges, which appear during WebGL rasterization.
:param bool picking: Enables object picking. When hovering the mouse cursor over an object, the widget will display the object's properties as text.
:param float vr_scale: Enables VR support (WebXR browser interface) if set to a positive value. The parameter value specifies the ratio of 1 length unit
                       of the simulation model and 1 meter in VR space. It thus controls the apparent size (scaling) of the model in virtual reality mode.
                       For example, if object dimensions are specified in terms of nanometers in the simulation model, then a *vr_scale* value of 0.2 would let
                       a 1 nanometer sphere appear 20 centimeters large in virtual reality space.
:param ipywidgets.Layout layout: The `layout attribute <https://ipywidgets.readthedocs.io/en/latest/examples/Widget%20Layout.html>`__ for the new Jupyter widget.
:return: `ipywidgets.DOMWidget <https://ipywidgets.readthedocs.io/en/stable/>`__

The ``layout`` attribute lets you control the `size of the widget <https://ipywidgets.readthedocs.io/en/stable/examples/Widget%20Layout.html>`__, e.g.:

.. code-block::

    from ipywidgets import Layout
    widget = vp.create_jupyter_widget(layout=Layout(width='100%', height='400px'))

.. caution::

    This method is still under active development and not fully functional yet. Expect these (known) limitations:

        * Changes you make to the scene or the viewport camera do not automatically trigger a refresh of the viewport widget.
          You need to explicitly call ``widget.refresh()`` to update the widget display whenever you change the scene.
        * Semi-transparent objects will likely be rendered incorrectly.
        * Viewport layers are not supported yet.

    These limitations will be resolved in a future update of the OVITO Python module.
    Please support the development of this new feature and report any issues you may encounter in our `issue tracker <https://gitlab.com/stuko/ovito/-/issues>`__
    or in the `OVITO forum <https://www.ovito.org/forum/>`__."""
        ...

    def render_anim(self, filename: str, size: Tuple[int, int]=(640, 480), fps: int=10, background: Color=(1.0, 1.0, 1.0), renderer: Optional[Renderer]=None, range: Optional[Tuple[int, int]]=None, every_nth: int=1, layout: Optional[Sequence[Tuple[Viewport, Tuple[float, float, float, float]]]]=None) -> None:
        """Renders an animation sequence.

:param str filename: The filename under which the rendered animation should be saved.
                     Supported video formats are: :file:`.avi`, :file:`.mp4`, :file:`.mov` and :file:`.gif`.
                     Alternatively, an image format may be specified (:file:`.png`, :file:`.jpeg`).
                     In this case, a series of image files will be produced, one for each frame, which
                     may be combined into an animation using an external video encoding tool of your choice.
:param size: The resolution of the movie in pixels.
:param fps: The number of frames per second of the encoded movie. This determines the playback speed of the animation.
:param background: An RGB triplet in the range [0,1] specifying the background color of the rendered movie.
:param renderer: The rendering engine to use. If none is specified, either OpenGL or Tachyon are used,
                 depending on the availability of OpenGL in the script execution context.
:param range: The interval of frames to render, specified in the form ``(from,to)``.
              Frame numbering starts at 0. If no interval is specified, the entire animation is rendered, i.e.
              frame 0 through (`FileSource.num_frames`-1).
:param every_nth: Frame skipping interval in case you don't want to render every frame of a very long animation.
:param layout: Optional definition of a multi-viewport layout to be rendered into the output image.

See also the :py:meth:`.render_image` method for a more detailed discussion of some of these parameters."""
        ...

    def render_image(self, size: Tuple[int, int]=(640, 480), frame: int=0, filename: Optional[str]=None, background: Color=(1.0, 1.0, 1.0), alpha: bool=False, renderer: Optional[Renderer]=None, crop: bool=False, layout: Optional[Sequence[Tuple[Viewport, Tuple[float, float, float, float]]]]=None) -> PySide6.QtGui.QImage:
        """Renders an image of the viewport's view.

:param size: A pair of integers specifying the horizontal and vertical dimensions of the output image in pixels.
:param int frame: The animation frame to render. Numbering starts at 0. See the `FileSource.num_frames` property for the number of loaded animation frames.
:param str filename: The file path under which the rendered image should be saved (optional).
                     Supported output formats are: :file:`.png`, :file:`.jpeg` and :file:`.tiff`.
:param background: A triplet of RGB values in the range [0,1] specifying the background color of the rendered image.
:param alpha: This option makes the background transparent so that the rendered image may later be superimposed on a different backdrop.
              When using this option, make sure to save the image in the PNG format in order to preserve the generated transparency information.
:param renderer: The rendering engine to use. If set to ``None``, either OpenGL or Tachyon are used,
                 depending on the availability of OpenGL in the current execution context.
:param crop: This option cuts away border areas of the rendered image filled with the background color; the resulting image may thus turn out smaller than the requested *size*.
:param layout: Optional definition of a multi-viewport layout to be rendered into the output image. The layout must be provided as a list of :py:class:`Viewport` objects
               and corresponding rectangular areas, which determine where each viewport's picture appears within the composed output image.
               Please make use of OVITO Pro's code generation function to learn how to construct the *layout* argument.
:returns: A `QImage <https://doc.qt.io/qtforpython/PySide6/QtGui/QImage.html>`__ object containing the rendered picture.

Populating the scene

Before rendering an image using this method, you should make sure the three-dimensional contains some
visible objects. Typically this involves calling the `Pipeline.add_to_scene()`
method on a pipeline to insert its output data into the scene::

   pipeline = import_file('simulation.dump')
   pipeline.add_to_scene()

Selecting the rendering backend

OVITO supports several different rendering backends for producing pictures of the three-dimensional scene:

    * :py:class:`OpenGLRenderer` (default)
    * :py:class:`TachyonRenderer`
    * :py:class:`OSPRayRenderer`

Each of these backends exhibits specific parameters that control the image quality and other aspect of the image
generation process. Typically, you would create an instance of one of these renderer classes, configure it and pass
it to the :py:meth:`!render_image()` method:

```python
  vp.render_image(filename='output/simulation.png', 
                  size=(320,240),
                  background=(0,0,0), 
                  renderer=TachyonRenderer(ambient_occlusion=False, shadows=False))
```

Post-processing images

If the ``filename`` parameter is omitted, the method does not save the rendered image to disk.
This gives you the opportunity to paint additional graphics on top before saving the
`QImage <https://doc.qt.io/qtforpython/PySide6/QtGui/QImage.html>`__ later using its ``save()`` method:

```python
  from ovito.vis import Viewport, TachyonRenderer
  from ovito.qt_compat import QtGui
  
  # Render an image of the three-dimensional scene:
  vp = Viewport(type=Viewport.Type.Ortho, camera_dir=(2, 1, -1))
  vp.zoom_all()
  image = vp.render_image(size=(320,240), renderer=TachyonRenderer())
  
  # Paint on top of the rendered image using Qt's drawing functions:
  painter = QtGui.QPainter(image)
  painter.drawText(10, 20, "Hello world!")
  del painter
  
  # Save image to disk:
  image.save("output/image.png")
```

As an alternative to the direct method demonstrated above, you can also make use of a :py:class:`PythonViewportOverlay`
to paint custom graphics on top of rendered images."""
        ...

    def zoom_all(self, size: Tuple[int, int]=(640, 480)) -> None:
        """Repositions the viewport camera such that all objects in the scene become completely visible.
The current orientation (:py:attr:`camera_dir`) of the viewport's camera is maintained but
the :py:attr:`camera_pos` and :py:attr:`fov` parameters are adjusted by this method.

:param size: Size in pixels of the image that is going to be renderer from this viewport.
             This information is used to compute the aspect ratio of the viewport rectangle into which
             the visible objects should be fitted. The tuple should match the *size* argument being passed
             to :py:meth:`render_image`.

Note that this method uses an axis-aligned bounding box computed at frame 0 of the
loaded trajectory enclosing all visible objects to adjust the viewport camera.
Make sure to call `Pipeline.add_to_scene()` first
to insert some visible object(s) into the scene."""
        ...