"""This module provides specific `trait types <https://docs.enthought.com/traits/traits_user_manual/intro.html>`__ which
are used in the context of custom modifiers and other extension classes to
define additional object parameters.
They supplement the `generic trait types <https://docs.enthought.com/traits/traits_user_manual/defining.html#predefined-traits>`__
provided by the `Traits <https://docs.enthought.com/traits/index.html>`__ Python package."""
__all__ = ['OvitoObjectTrait', 'ColorTrait']
from __future__ import annotations
from typing import Tuple, Type, Any, Union
import traits.api
import ovito.pipeline
import ovito.data
import ovito.vis

class OvitoObjectTrait(traits.api.Instance):
    """A `trait type <https://docs.enthought.com/traits/traits_user_manual/intro.html>`__ whose value is an instance of a class from the :py:mod:`ovito` package."""

    def __init__(self, klass: Type[Union[ovito.vis.DataVis, ovito.pipeline.Modifier, ovito.pipeline.FileSource, ovito.pipeline.StaticSource, ovito.data.DataObject]], **params: Any) -> None:
        """:param klass: The object class type to instantiate.
:param params: All other keyword parameters are forwarded to the constructor of the object class."""
        ...

class ColorTrait(traits.api.BaseTuple):
    """A `trait type <https://docs.enthought.com/traits/traits_user_manual/intro.html>`__ whose value is a tuple with three floats that represent the RGB values of a color."""

    def __init__(self, default: Tuple[float, float, float]=(1.0, 1.0, 1.0), **metadata: Any) -> None:
        """:param default: The initial color value to be assigned to the parameter trait."""
        ...