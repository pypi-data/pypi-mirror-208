import collections.abc as collections
import numbers
import numpy
from . import PropertyContainer, Property

# Give the PropertyContainer class a dict-like interface for accessing properties by name:
collections.Mapping.register(PropertyContainer)

# len() function returns the number of properties when called on a PropertyContainer.
PropertyContainer.__len__ = lambda self: len(self.properties)

# Implementation of the printing method for the PropertyContainer class.
def _PropertyContainer__str__(self):
    return str(dict(self))
PropertyContainer.__str__ = _PropertyContainer__str__

# Returns a Python iterator yielding the names of all properties stored in the PropertyContainer.
def _PropertyContainer__iter__(self):
    for p in self.properties:
        yield p.name
PropertyContainer.__iter__ = _PropertyContainer__iter__

# Returns the property with the given name.
def _PropertyContainer__getitem__(self, key):
    if key.endswith('_'):
        if not self.is_safe_to_modify:
            raise ValueError("Requesting a mutable version of a property is only possible for a container that itself is mutable. "
                            "Make sure you are working with a mutable version of the {} object.".format(self.__class__.__name__))
        request_mutable = True
        key = key[:-1]
    else:
        request_mutable = False
    for p in self.properties:
        if p.name == key:
            if request_mutable:
                return self.make_mutable(p)
            else:
                return p
    raise KeyError("{} data object does not contain the property '{}'.".format(self.__class__.__name__, str(key)))
PropertyContainer.__getitem__ = _PropertyContainer__getitem__

# Assigns the property to the container.
# This is needed to make statements of the following kind work:
#
#    data.particles_['Position_'] += (0, 0, 1)
#
# That statement implicitly translates to
#
#    data.particles_['Position_'] = (data.particles_['Position_'] += (0, 0, 1))
#
# invoking this __setitem__() special method.
def _PropertyContainer__setitem__(self, key, value):
    if not isinstance(value, Property):
        raise ValueError("Expected a Property object. PropertyContainer only accepts Property objects as dictionary values.")
    if key.endswith('_'):
        key = key[:-1]
    if value.name != key:
        raise ValueError("Can only assign a Property whose name matches the key string. Consider using PropertyContainer.create_property() method instead.")
    # Accept only the existing property as new dictionary value:
    if self.get(key) is not value:
        raise ValueError("Can only re-assign an existing Property instance to the PropertyContainer but not a new instance. Consider using PropertyContainer.create_property() method instead if you want to assign a new property or replace the values of an existing property in the container.")
    # The following check is not needed as long as we only accept the existing property:
    #if not self.is_safe_to_modify:
    #    raise ValueError("Property assignment is only possible for a container that itself is mutable. "
    #                    "Make sure you are working with a mutable version of the {} object.".format(self.__class__.__name__))
PropertyContainer.__setitem__ = _PropertyContainer__setitem__

# Returns the property with the given name or the given default value if no such property exists in the container.
def _PropertyContainer_get(self, key, default=None):
    try: return self[key]
    except KeyError: return default
PropertyContainer.get = _PropertyContainer_get

# Removes the property with the given name from the container.
def _PropertyContainer__delitem__(self, key):
    for p in self.properties:
        if p.name == key:
            self._remove_property(p)
            return
    raise KeyError(f"{self.__class__.__name__} data object does not contain the property '{key}'.")
PropertyContainer.__delitem__ = _PropertyContainer__delitem__

# Returns the list of names of all properties in the PropertyContainer.
def _PropertyContainer_keys(self):
    return collections.KeysView(self)
PropertyContainer.keys = _PropertyContainer_keys

# Returns the list of name-property pairs in the PropertyContainer.
def _PropertyContainer_items(self):
    return collections.ItemsView(self)
PropertyContainer.items = _PropertyContainer_items

# Returns the list Property objects in the PropertyContainer.
def _PropertyContainer_values(self):
    return self.properties
PropertyContainer.values = _PropertyContainer_values

# Internal helper function for registering standard property accessor fields for a PropertyContainer subclass.
def create_property_accessor(property_name, doc = None):
    base_property_name = property_name
    # Remove the leading underscore to get the actual property name.
    if base_property_name.endswith('_'):
        base_property_name = base_property_name[:-1]
    def getter(self):
        return self.get(property_name)
    def setter(self, val):
        # Detect trivial case where the property object is assigned to itself:
        if isinstance(val, Property) and val in self.properties and val.name == base_property_name:
            return
        self.create_property(base_property_name, data=val)
    return property(getter, setter, doc=doc)
PropertyContainer._create_property_accessor = staticmethod(create_property_accessor)

# Implementation of the PropertyContainer.create_property() method.
def _PropertyContainer_create_property(self, name, dtype=None, components=None, data=None):
    """
    Adds a new property to the container and optionally initializes it with
    the per-element data provided by the *data* parameter. The method returns the new :py:class:`Property`
    instance.

    The method allows to create *standard* as well as *user-defined* properties.
    To create a *standard* property, one of the :ref:`standard property names <particle-properties-list>` must be provided as *name* argument:

    .. literalinclude:: ../example_snippets/property_container.py
        :lines: 16-17

    The length of the provided *data* array must match the number of existing elements in the container, which is given by the :py:attr:`count` attribute.
    You can alternatively assign the per-element values to the property after its construction:

    .. literalinclude:: ../example_snippets/property_container.py
        :lines: 23-24

    To create a *user-defined* property, use a non-standard property name:

    .. literalinclude:: ../example_snippets/property_container.py
        :lines: 29-30

    In this case the data type and the number of vector components of the new property are inferred from
    the provided *data* Numpy array. Providing a one-dimensional array creates a scalar property while
    a two-dimensional array creates a vectorial property.
    Alternatively, the *dtype* and *components* parameters can be specified explicitly
    if you are going to assign the property values at a later time:

    .. literalinclude:: ../example_snippets/property_container.py
        :lines: 34-35

    If the property to be created already exists in the container, it is replaced with a :ref:`modifiable copy <data_ownership>` if necessary.
    The existing per-element data from the old property is retained if *data* is ``None``.

    Note: If the container contains no properties yet, then the number of elements (e.g. particles or bonds) is still undefined.
    In this case the :py:meth:`!create_property` method lets you *define* the number of elements when inserting the very first property
    by specifying a *data* array of the desired length. For example, to create a new :py:class:`Particles` container from scratch
    with 10 particles, a Numpy array of length 10 is used to initialize the ``Position`` particle property:

    .. literalinclude:: ../example_snippets/property_container.py
        :lines: 40-45

    After the initial ``Positions`` property has been created, the number of particles in the container is now determined and any
    subsequently added properties must have the exact same length.

    :param name: Either a :ref:`standard property type constant <particle-properties-list>` or a name string.
    :param data: An optional data array with per-element values for initializing the new property.
                    The size of the array must match the element :py:attr:`count` of the container
                    and the shape must be consistent with the number of components of the property to be created.
    :param dtype: The element data type when creating a user-defined property. Must be either ``int`` or ``float``.
    :param int components: The number of vector components when creating a user-defined property.
    :returns: The newly created :py:class:`Property` object.
    """

    # Process 'name' function parameter.
    if isinstance(name, numbers.Integral):
        if name <= 0:
            raise TypeError("Invalid standard property type.")
        property_type = name
    else:
        property_name = name
        property_type = self.standard_property_type_id(property_name)

    # Process 'components' function parameter.
    if isinstance(components, numbers.Integral):
        component_count = components
        component_names = []
    elif isinstance(components, collections.Iterable):
        component_names = list(components)
        component_count = len(component_names)
    else:
        component_count = None
        component_names = []

    if property_type != 0:
        if component_count is not None:
            raise ValueError("Specifying a vector component count or component list for a standard property is not allowed.")
        if dtype is not None:
            raise ValueError("Specifying a data type for a standard property is not allowed.")
    else:
        if component_count is None or dtype is None:
            if data is None:
                raise ValueError("Must provide a 'data' array if data type or component count are not specified.")
        if data is not None:
            data = numpy.asanyarray(data)
        if component_count is None:
            if data.ndim < 1 or data.ndim > 2:
                raise ValueError("Provided data array must be either 1 or 2-dimensional.")
            component_count = data.shape[1] if data.ndim==2 else 1
        if dtype is None:
            dtype = data.dtype
        if component_count < 1:
            raise ValueError(f"Invalid number of vector components specified for a user-defined property: {component_count}")
        if not property_name or '.' in property_name:
            raise ValueError(f"Invalid name for a property: '{property_name}'. Name contains illegal characters or is empty.")

        # Translate data type from Python to Qt metatype id.
        if dtype in (int, numpy.int32):
            dtype = Property.DataType.Int
        elif dtype in (numpy.longlong, numpy.int64):
            dtype = Property.DataType.Int64
        elif dtype == float:
            dtype = Property.DataType.Float
        else:
            raise TypeError("Invalid property dtype. Only 'int', 'int32', 'int64' and 'float' are supported.")

    # Check whether property already exists in the container.
    existing_prop = None
    for prop in self.properties:
        if property_type != 0 and prop.type == property_type:
            existing_prop = prop
        elif property_type == 0 and prop.name == property_name:
            existing_prop = prop

    num_elements = self.count
    if len(self.properties) == 0:
        if data is not None:
            num_elements = len(data)
        elif num_elements == 0:
            raise RuntimeError("Cannot create first property without initial data, because the container's element count is still undefined. Either provide a data array or set the container's element count first.")

    if existing_prop is None:
        # If property does not exist yet in the container, create and add a new Property instance.
        if property_type != 0:
            prop = self.create_standard_property(property_type, data is None, len(data) if data is not None and num_elements == 0 else num_elements)
        else:
            prop = self.create_user_property(property_name, dtype, component_count, data is None, len(data) if data is not None and num_elements == 0 else num_elements, component_names)
    else:
        # Make sure the data layout of the existing property is compatible with the requested layout.
        if component_count is not None and existing_prop.component_count != component_count:
            raise ValueError(f"Existing property '{existing_prop.name}' has {existing_prop.component_count} vector component(s), but {component_count} component(s) have been requested for the new property.")
        if dtype is not None and existing_prop.data_type != dtype:
            from ovito.qt_compat import QtCore
            raise ValueError(f"Existing property '{existing_prop.name}' has data type '{QtCore.QMetaType.typeName(existing_prop.data_type)}', but data type '{QtCore.QMetaType.typeName(dtype)}' has been requested for the new property.")

        # Make a copy of the existing property so that we can safely modify it.
        prop = self.make_mutable(existing_prop)

    # Initialize property with per-element data if provided.
    if data is not None:
        with prop:
            prop[...] = data
    return prop
PropertyContainer.create_property = _PropertyContainer_create_property

# Implementation of the PropertyContainer.delete_elements() method.
def _PropertyContainer_delete_elements(self, mask):
    """
    Deletes a subset of the elements from this container. The elements to be deleted must be specified in terms
    of a 1-dimensional mask array having the same length as the container (see :py:attr:`count`).
    The method will delete those elements whose corresponding mask value is non-zero, i.e., the ``i``-th element
    will be deleted if ``mask[i]!=0``.

    For example, to delete all currently selected particles, i.e., the subset of particles whose ``Selection`` property
    is non-zero, one would simply write:

    .. literalinclude:: ../example_snippets/property_container_delete_elements.py
        :lines: 10-10

    The effect of this statement is the same as for applying the :py:class:`~ovito.modifiers.DeleteSelectedModifier` to the particles list.
    """
    mask_arr = numpy.asanyarray(mask)
    if mask_arr.shape != (self.count, ):
        raise ValueError(f"Mask array must be a 1-d array of length {self.count}, matching the element count in the PropertyContainer.")
    return self._delete_elements(mask_arr)
PropertyContainer.delete_elements = _PropertyContainer_delete_elements

# Implementation of the PropertyContainer.delete_indices() method.
def _PropertyContainer_delete_indices(self, indices):
    """
    Deletes a subset of the elements from this container. The elements to be deleted must be specified in terms
    of a sequence of indices, all in the range 0 to :py:attr:`count`-1. The method accepts any type of iterable object,
    including sequence types and generators.

    For example, to delete every other particle, one could use Python's ``range()`` function to generate
    all even indices up to the length of the particle container:

    .. literalinclude:: ../example_snippets/property_container_delete_elements.py
        :lines: 25-25
    """
    return self._delete_indices(indices)
PropertyContainer.delete_indices = _PropertyContainer_delete_indices
