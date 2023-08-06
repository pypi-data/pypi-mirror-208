from __future__ import annotations
import ovito
import ovito.pipeline
from ..data import DataCollection
from ..modifiers import PythonScriptModifier
import abc
import os
import traits.api
from typing import List, Dict, Optional, Any, Generator, Union, Mapping, Sequence

class ModifierInterface(traits.api.HasStrictTraits):
    """
    Base: :py:class:`traits.has_traits.HasStrictTraits`

    Abstract base class for :ref:`Python script modifiers <writing_custom_modifiers>` that follow the :ref:`advanced programming interface <writing_custom_modifiers.advanced_interface>`.

    .. versionadded:: 3.8.0
    """

    # Import the InputSlot helper class defined by the C++ code into the namespace of this class.
    class InputSlot(PythonScriptModifier.InputSlot):
        """
        Represents the upstream pipeline generating the input data for a custom modifier implementation.
        """

        # Define these members only when generating the Sphinx documentation for the OVITO module.
        if os.environ.get('OVITO_SPHINX_BUILD', False):
            @property
            def num_frames(self) -> int:
                """
                The number of trajectory frames that the upstream pipeline connected to this input slot
                can produce.
                """
                return super().num_frames

            def compute(self, frame: int) -> DataCollection:
                """
                Computes the results of the upstream pipeline connected to this input slot.

                *frame* specifies the trajectory frame to retrieve, which must be in the range 0 to (:py:attr:`num_frames`-1).

                The slot uses a caching mechanism to keep the data for one or more frames in memory. Thus, invoking :py:meth:`!compute`
                repeatedly to retrieve the same frame will typically be very fast.

                :param frame: The trajectory frame to retrieve from the upstream pipeline.
                """
                return super().compute(frame)

    # Event trait which sub-classes should trigger whenver the number of output frames changes.
    update_output_frame_count = traits.api.Event(descr='Requests recomputation of the number of output animation frames')

    # Abstract method that must be implemented by all sub-classes:
    @abc.abstractmethod
    def modify(self, data: DataCollection, *, frame: int, input_slots: Dict[str, ModifierInterface.InputSlot], data_cache: DataCollection, **kwargs: Any) -> Optional[Generator[Union[str, float], None, None]]:
        """
        The actual work function which gets called by the pipeline system to let the modifier do its thing.

        :param data: Data snapshot which should be modified by the modifier function in place.
        :param frame: Zero-based trajectory frame number.
        :param input_slots: One or more :py:class:`InputSlot` objects representing the upstream data pipeline(s) connected to this modifier.
        :param data_cache: A data container (initially empty) which may be used by the modifier function to store intermediate results.
        :param kwargs: Other arguments that may be passed by the pipeline system. This parameter should be included for forward compatibility with future versions of OVITO.
        """
        raise NotImplementedError

    # Define the optional methods only when generating the Sphinx documentation for the OVITO module.
    if os.environ.get('OVITO_SPHINX_BUILD', False):
        def input_caching_hints(self, frame: int, *, input_slots: Dict[str, InputSlot], **kwargs: Any) -> Sequence[int] | Mapping[InputSlot, int | Sequence[int]]:
            """
            User-defined modifiers that :ref:`access multiple trajectory frames <writing_custom_modifiers.advanced_interface.trajectory>` in their :py:meth:`modify` method
            should implement this method to communicate the list of frames going to be needed. The pipeline system will keep the data of these trajectory frames
            in an internal cache to avoid unnecessary I/O and compute operations. See :ref:`writing_custom_modifiers.advanced_interface.caching`.

            :param frame: Zero-based trajectory frame number.
            :param input_slots: One or more :py:class:`InputSlot` objects representing the upstream data pipeline(s) connected to this modifier.

            If your modifier defines :ref:`additional input slots <writing_custom_modifiers.advanced_interface.additional_input_slots>`, the function must
            return a dictionary that specifies for each input slot, including the standard *upstream* slot, which input frame(s) should be cached. For example::

                extra_slot = OvitoObjectTrait(FileSource)

                def input_caching_hints(self, frame, **kwargs):
                    return {
                        'upstream': frame,
                        'extra_slot': 0
                    }

            .. note::

                This method is supposed to be implemented as part of a :ref:`user-defined modifier class <writing_custom_modifiers.advanced_interface>`
                but it should not be called by user code. The pipeline system will automatically invoke this method whenever necessary.
            """
            raise NotImplementedError

ovito.pipeline.ModifierInterface = ModifierInterface