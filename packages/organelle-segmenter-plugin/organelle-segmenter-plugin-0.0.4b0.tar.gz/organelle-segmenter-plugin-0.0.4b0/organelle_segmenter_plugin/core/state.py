from organelle_segmenter_plugin.util.lazy import lazy_property
from organelle_segmenter_plugin.model.segmenter_model import SegmenterModel


class State:
    """
    Application state wrapper.
    Use this class as a way to easily store and access stateful data that needs to be shared accross controllers
    """

    @lazy_property
    def segmenter_model(self) -> SegmenterModel:
        return SegmenterModel()
