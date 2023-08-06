"""
This module contains classes that are part of OVITO's data pipeline system.

**Pipelines:**

  * :py:class:`Pipeline`
  * :py:class:`Modifier` (base class of all built-in modifiers)
  * :py:class:`ModifierInterface` (base class of user-defined modifiers)

**Data sources:**

  * :py:class:`StaticSource`
  * :py:class:`FileSource`
  * :py:class:`PythonScriptSource`

"""

__all__ = ['Pipeline', 'Modifier', 'StaticSource', 'FileSource', 'PythonScriptSource', 'ModifierInterface']