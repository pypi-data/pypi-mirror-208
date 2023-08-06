"""
.. versionadded:: 3.8.0

This module provides specific `trait types <https://docs.enthought.com/traits/traits_user_manual/intro.html>`__ which
are used in the context of :ref:`custom modifiers <writing_custom_modifiers>` and other extension classes to
:ref:`define additional object parameters <writing_custom_modifiers.advanced_interface.user_params>`.
They supplement the `generic trait types <https://docs.enthought.com/traits/traits_user_manual/defining.html#predefined-traits>`__
provided by the `Traits <https://docs.enthought.com/traits/index.html>`__ Python package.
"""

import traits.api

__all__ = ['OvitoObjectTrait', 'ColorTrait']

# A parameter traits that has an instance of a OvitoObject-derived class as value.
class OvitoObjectTrait(traits.api.Instance):
    """A `trait type <https://docs.enthought.com/traits/traits_user_manual/intro.html>`__ whose value is an instance of a class from the :py:mod:`ovito` package."""
    def __init__(self, klass, factory=None, **params):
        """
        :param klass: The object class type to instantiate.
        :param params: All other keyword parameters are forwarded to the constructor of the object class.
        """
        params['_load_user_defaults_in_gui'] = True # Initialize object parameters to user default values when running in the GUI environment.
        super().__init__(klass, factory=factory, kw=params)

# A parameter trait whose value is a RGB tuple with values from 0 to 1.
# The default value is (1.0, 1.0, 1.0).
class ColorTrait(traits.api.BaseTuple):
    """A `trait type <https://docs.enthought.com/traits/traits_user_manual/intro.html>`__ whose value is a tuple with three floats that represent the RGB values of a color."""
    def __init__(self, default=(1.0, 1.0, 1.0), **metadata):
        """
        :param default: The initial color value to be assigned to the parameter trait.
        """
        super().__init__(default, **metadata)
