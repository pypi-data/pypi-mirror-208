import napari
from napari.components.layerlist import LayerList
from napari.layers import Layer
from typing import List


class ViewerAbstraction:
    """
    Provides a layer of abstraction over the Napari viewer,
    mostly to protect against API changes and make unit testing easier
    """

    def __init__(self, viewer: napari.Viewer):
        if viewer is None:
            raise ValueError("viewer")
        self._viewer = viewer
        self._active_layer_list: List[Layer] = []

    @property
    def events(self):
        return self._viewer.events

    def get_layers(self) -> LayerList:
        """
        Get a list of all image layers currently loaded in the Napari viewer

        inputs:
            viewer (Viewer): the Napari viewer
        """
        return self._viewer.layers

    def get_active_layer(self) -> List[Layer]:
        """
        Get the layer currently active (selected) in the Napari viewer

        inputs:
            viewer (Viewer): the Napari viewer
        """
        # ORIGINAL
        # if self._viewer.layers.selection.active:
        #     return [self._viewer.layers.selection.active]
        # else:
        #     # two or more layers are selected, return all
        #     # return list(self._viewer.layers.selection._set)  # JAH: does removing the ._set work?
        #     print(f"retuning list of selection, {self._viewer.layers.selection}")
        #     # NOTE: set is not ordered, but our selections need to be ordered... so
        #     return list(self._viewer.layers.selection)
        # HACK
        if self._viewer.layers.selection.active:
            self._active_layer_list = [self._viewer.layers.selection.active]
            self.set_active_layer(self._active_layer_list[0])
            return self._active_layer_list
        else:
            # two or more layers are selected, return all
            # return list(self._viewer.layers.selection._set)  # JAH: does removing the ._set work?
            # NOTE: set is not ordered, but our selections need to be ordered... so
            active_layer_list = self._active_layer_list
            return active_layer_list
            # print(f"retuning list of selection, {self._viewer.layers.selection}")
            # # return list(self._viewer.layers.selection)

    def set_active_layer(self, layer: Layer):
        self._viewer.layers.selection.active = layer

    def set_active_layer_list(self, layers: List[Layer]):
        # selection = self._viewer.layers.selection
        self._active_layer_list = layers
        # self._viewer.layers.selection.active = layer

    def add_image_layer(self, image_data, name: str) -> Layer:
        """
        Add a new image layer to the Napari viewer
        :param: image_data: image layer pixel data
        :param: name: new layer name
        """
        return self._viewer.add_image(image_data, name=name)

    def get_theme(self):
        return self._viewer.theme


# TODO:  add methods to discard and add active layers
