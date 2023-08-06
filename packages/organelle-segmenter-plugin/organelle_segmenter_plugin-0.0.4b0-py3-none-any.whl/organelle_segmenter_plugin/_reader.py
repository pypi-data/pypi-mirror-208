# from napari_plugin_engine import napari_hook_implementation
from typing import Union, Sequence, Optional, List, Any, Dict, Optional, Callable, Tuple

from pathlib import Path

FullLayerData = Tuple[Any, Dict, str]
LayerData = Union[Tuple[Any], Tuple[Any, Dict], FullLayerData]

PathLike = Union[str, Path]
# PathOrPaths = Union[str, Sequence[str]]
PathOrPaths = Union[PathLike, Sequence[PathLike]]
ReaderFunction = Callable[[PathOrPaths], List[LayerData]]


SUPPORTED_FILENAME_PATTERNS = (".xyz", ".czi", ".tif", ".tiff")

from infer_subc.core.file_io import reader_function


# NPE2 style
def napari_get_reader(path: PathOrPaths) -> Optional[ReaderFunction]:
    # If we recognize the format, we return the actual reader function
    # Only support single path
    if isinstance(path, list):
        # logger.info("ORGANELLE-SEGMENTER: Multi-file reading not yet supported.")
        print("ORGANELLE-SEGMENTER: Multi-file reading not yet supported.")
        return None

    if isinstance(path, str) and path.endswith(SUPPORTED_FILENAME_PATTERNS):
        if path.endswith(".xyz"):
            print("BAGGGING OUT>>>>>>")
            return None
        else:
            return xyz_file_reader

    # otherwise we return None.
    return None


def xyz_file_reader(path: PathOrPaths) -> List[LayerData]:
    data, meta, layer_type = reader_function(path)[0]

    # fix name and channel_axis
    name = Path(path).stem
    # channel_axis = meta.pop("channel_axis")
    channel_names = meta.pop("name")  # list of names for each layer
    # scale = meta.pop("scale")
    # meta["_channel_axis"] = channel_axis
    # meta["_scale"] = scale  # this makes things easier later
    meta["channel_names"] = channel_names
    meta["file_name"] = name

    # HACK: prevent numeric start of layer names
    layer_attributes = {"name": "-" + name, "metadata": meta}
    # layer_type = "image"
    return [(data, layer_attributes, layer_type)]  # (data,meta) is fine since 'image' is default

