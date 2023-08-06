from typing import List
from pathlib import Path

# from aicssegmentation.workflow.workflow_definition import WorkflowDefinition
from infer_subc.workflow.workflow_definition import WorkflowDefinition
from napari.layers.base.base import Layer
from qtpy.QtWidgets import (
    QComboBox,
    QLabel,
    QVBoxLayout,
    QWidget,
)
from qtpy.QtGui import QStandardItem, QStandardItemModel
from qtpy import QtCore

from organelle_segmenter_plugin.model.channel import Channel
from organelle_segmenter_plugin.model.segmenter_model import SegmenterModel
from organelle_segmenter_plugin.controller._interfaces import IWorkflowSelectController
from organelle_segmenter_plugin.core.view import View
from organelle_segmenter_plugin.widgets.form import Form, FormRow
from organelle_segmenter_plugin.widgets.warning_message import WarningMessage
from organelle_segmenter_plugin.util.ui_utils import UiUtils
from organelle_segmenter_plugin.widgets.file_input import FileInput, FileInputMode


from organelle_segmenter_plugin.widgets.workflow_buttons import WorkflowButtons
from ._main_template import MainTemplate


class WorkflowSelectView(View):
    _combo_layers: QComboBox
    # _combo_channels: QComboBox
    _load_image_warning: WarningMessage
    _workflow_buttons: WorkflowButtons
    _channels_note: QLabel
    # _combo_workflows: QComboBox
    # _workflows: List[WorkflowDefinition]
    # _workflow_names: List[str]
    _field_add_workflow: FileInput

    def __init__(self, controller: IWorkflowSelectController):
        super().__init__(template_class=MainTemplate)

        if controller is None:
            raise ValueError("controller")
        self._controller = controller
        self.setObjectName("workflowSelectView")

    def load(self, model: SegmenterModel):
        self._setup_ui()

        self.update_layers(model.layers, model.selected_layer)
        # self.update_channels(model.channels, model.selected_channel)
        self._load_workflows(model.workflows)

    #    # JAH: combo_box_workflows
    #     # self._workflows = self._controller._workflow_engine._load_workflow_definitions()
    #     # self.update_workflows(self._workflows)
    #     self.update_workflows(model.workflows)

    def _setup_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

        # Title
        workflow_selection_title = QLabel("Workflow selection steps:")
        workflow_selection_title.setObjectName("workflowSelectionTitle")

        # Warning
        self._load_image_warning = WarningMessage("Open a 3D image in Napari first!")
        self._load_image_warning.setVisible(False)

        # Dropdowns
        layers_dropdown = UiUtils.dropdown_row("1.", "Select multichannel 3D Napari image layer", enabled=False)
        self._combo_layers = layers_dropdown.widget
        self._combo_layers.setStyleSheet("QComboBox { combobox-popup: 0; }")
        self._combo_layers.setMaxVisibleItems(20)
        self._combo_layers.activated.connect(self._combo_layers_activated)


        # channels_dropdown = UiUtils.dropdown_row("2.", "Select Channels)", enabled=False)
        # self._combo_channels = channels_dropdown.widget
        # self._combo_channels.setStyleSheet("QComboBox { combobox-popup: 0; }")
        # self._combo_channels.setMaxVisibleItems(20)
        # self._combo_channels.activated.connect(self._combo_channels_activated)

        self._channels_note = QLabel() # in case we want to update selection?
        self._channels_note.setText("----ALL CHANNELS-----")
        channels_note_label = FormRow("2.  Channels", self._channels_note)

        # Workflow config add
        self._field_add_workflow = FileInput(
            mode=FileInputMode.FILE, filter="Json file (*.json)", placeholder_text="None loaded..."
        )
        add_workflow = FormRow("3.  Add  workflow:", self._field_add_workflow)
        self._field_add_workflow.file_selected.connect(self._form_field_changed)

        layer_channel_selections = QWidget()
        layer_channel_selections.setLayout(Form([layers_dropdown, channels_note_label, add_workflow]))

        # Add all widgets
        widgets = [
            workflow_selection_title,
            self._load_image_warning,
            layer_channel_selections,
        ]
        for widget in widgets:
            layout.addWidget(widget)

        self._workflow_buttons = WorkflowButtons()
        self._workflow_buttons.workflowSelected.connect(self._workflow_selected)
        self.layout().addWidget(self._workflow_buttons)

        # TODO:  add alternative "load workflow widget here"
        # e.g. from batch_processing_view
        ## Workflow config
        ## self.field_workflow_config = FileInput(
        ##     mode=FileInputMode.FILE, filter="Json file (*.json)", placeholder_text="Load a JSON workflow file..."
        ## )
        ## self.field_workflow_config.file_selected.connect(self._form_field_changed)
        ## row1 = FormRow("1.  Load workflow:", self.field_workflow_config)

    def update_layers(self, layers: List[str], selected_layer: Layer = None):
        """
        Update / repopulate the list of selectable layers
        Inputs:
            layers: List of layer names
            selected_layer_name: (optional) name of the layer to pre-select
        """
        self._reset_combo_box(self._combo_layers)

        if layers is None or len(layers) == 0:
            self._load_image_warning.setVisible(True)
            self._combo_layers.setEnabled(False)
        else:
            # reverse layer list when adding to combobox
            # to mimic layer list on napari ui
            self._combo_layers.addItems(layers[::-1])
            if selected_layer is not None:
                self._combo_layers.setCurrentText(selected_layer.name)
            self._combo_layers.setEnabled(True)
            self._load_image_warning.setVisible(False)


    # def update_channels(self, channels: List[Channel], selected_channel: Channel = None):
    #     """
    #     Update / repopulate the list of selectable channels
    #     Inputs:
    #         channels: List of channel names
    #     """
    #     self._reset_combo_box(self._combo_channels)
    #     # JAH:  make a default "negative" channel to NOT choose one...
    #     if channels is None or len(channels) == 0:
    #         self._combo_channels.setEnabled(False)
    #     else:
    #         model = QStandardItemModel()
    #         model.appendRow(QStandardItem(self._combo_channels.itemText(0)))

    #         for channel in channels:
    #             item = QStandardItem(channel.display_name)
    #             item.setData(channel, QtCore.Qt.UserRole)
    #             model.appendRow(item)

    #         self._combo_channels.setModel(model)

    #         if selected_channel is not None:
    #             # TODO relying on display name isn't the best as it will probably
    #             #      cause issues if channel names aren't unique
    #             # TODO refactor by making Channel derive from QStandardItem and do something like this:
    #             #      selected_index = model.indexFromItem(selected_channel)
    #             #      self.combo_channels.setCurrentIndex(selected_index)
    #             self._combo_channels.setCurrentText(selected_channel.display_name)

    #         self._combo_channels.setEnabled(True)

    def update_workflows(self, enabled: bool):
        """
        Update state of workflow list
        Inputs:
            enabled: True to enable the list, False to disable it
        """
        self._workflow_buttons.setEnabled(enabled)

    def _load_workflows(self, workflows: List[WorkflowDefinition]):
        """
        Load workflows into workflow grid
        """
        # self._workflow = workflows
        # self._workflow_names = [wf.name for wf in workflows]
        self._workflow_buttons.load_workflows(workflows)

    def _reset_combo_box(self, combo: QComboBox):
        """
        Reset a combo box to its original state, keeping the header but removing all other items
        """
        if combo.count() > 0:
            header = combo.itemText(0)
            combo.clear()
            combo.addItem(header)

    #####################################################################
    # Event handlers
    #####################################################################

    def _combo_layers_activated(self, index: int):
        if index == 0:  # index 0 is the dropdown header
            self._controller.unselect_layer()
        else:
            self._controller.select_layer(self._combo_layers.itemText(index))

    # def _combo_channels_activated(self, index: int):
    #     if index == 0:
    #         self._controller.unselect_channel()
    #     else:
    #         self._controller.select_channel(self._combo_channels.itemData(index, role=QtCore.Qt.UserRole))

    def _workflow_selected(self, workflow_name: str):
        self._controller.select_workflow(workflow_name)


    def _form_field_changed(self, value):
        workflow_configs = self._field_add_workflow.selected_file
        for wf in workflow_configs:
            self._controller.add_workflow(wf)
            self._workflow_buttons._add_new_button(Path(wf).stem)
        self.update_workflows(enabled=True)
        # send signal to workflow_buttons
        