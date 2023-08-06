from qtpy.QtWidgets import QComboBox, QListWidget

from organelle_segmenter_plugin.widgets.form import FormRow
from qtpy.QtWidgets import QAbstractItemView


class UiUtils:
    @staticmethod
    def dropdown_row(label: str, placeholder: str = None, default: str = None, options=None, enabled=False) -> FormRow:
        """
        Given the contents of a dropdown and a label, return a FormRow containing
        a label and a QComboBox widget that can be used with the custom Form widget
        """
        dropdown = QComboBox()
        dropdown.setDisabled(not enabled)
        dropdown.setStyleSheet("QComboBox { combobox-popup: 0; }")
        if placeholder is not None:
            dropdown.addItem(placeholder)
        if options is not None:
            str_options = [str(option) for option in options]
            dropdown.addItems(str_options)
        if placeholder is None and default is not None and options is not None:
            default_index = options.index(default)
            dropdown.setCurrentIndex(default_index)

        return FormRow(label, dropdown)

    @staticmethod
    def multi_dropdown_row(
        label: str, placeholder: str = None, default: str = None, options=None, enabled=False
    ) -> FormRow:
        """
        Given the contents of a dropdown and a label, return a FormRow containing
        a label and a QListWidget widget that can be used with the custom Form widget
        """
        dropdown = QListWidget()
        dropdown.setDisabled(not enabled)
        dropdown.setStyleSheet("QComboBox { combobox-popup: 0; }")
        dropdown.setSelectionMode(QAbstractItemView.MultiSelection)
        if placeholder is not None:
            dropdown.addItem(placeholder)
        if options is not None:
            str_options = [str(option) for option in options]
            dropdown.addItems(str_options)
        if placeholder is None and default is not None and options is not None:
            default_index = options.index(default)
            dropdown.setCurrentIndex(default_index)

        return FormRow(label, dropdown)
