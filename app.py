import sys
import json
from typing import Dict

from PySide6 import QtCore
from PySide6.QtWidgets import QApplication, QLabel,QWidget, QHBoxLayout, QDialog, QVBoxLayout, QDialogButtonBox, QComboBox, QPushButton, QLineEdit, QFileDialog, QListView, QStackedWidget, QSizePolicy
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QStandardItemModel, QStandardItem, QIcon
import pyvisa

from instruments import Agilent8163B_GUI, Agilent8164B_GUI, AgilentE3640A_GUI

class Instrument:
    """Represents an instrument object with name and type."""
    instrument_map = {
        "Agilent8163B": Agilent8163B_GUI,
        "Agilent8164B": Agilent8164B_GUI,
        "AgilentE3640A": AgilentE3640A_GUI,
    }
    
    def __init__(self, row: int, name: str, instr_type: str, rm: pyvisa.ResourceManager, active: bool=False):
        self.row = row
        self.id = name
        self.instr_type = instr_type
        self._gui = self.instrument_map[instr_type](rm=rm)
        self.active = active

    @property
    def gui(self):
        return self._gui
    
    def to_dict(self):
        """Convert instrument object to dictionary for saving."""
        return {"row": self.row, "id": self.id, "type": self.instr_type, "addr": self._gui.addr}

    @classmethod
    def from_dict(cls, data: Dict, rm: pyvisa.ResourceManager):
        """Create an Instrument object from a dictionary."""
        instr = cls(data["row"], data["id"], data["type"], rm=rm, active=False)
        instr.gui.addr = data["addr"]
        return instr


class InstrSelectionDialog(QDialog):
    """The popped up dialog for selecting an instrument to add to the list."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Select Instrument")
        self.setStyleSheet("font-size: 14px;")

        layout = QVBoxLayout(self)
        
        # Name of the instrument
        layout.addWidget(QLabel("Name of the instrument:"))
        self.name = QLineEdit()
        self.name.setPlaceholderText("Enter a unique name")
        layout.addWidget(self.name)

        # Dropdown with instrument choices
        self.combo_box = QComboBox()
        self.combo_box.addItems(["Agilent8163B", "Agilent8164B", "AgilentE3640A"])
        layout.addWidget(QLabel("Choose an instrument:"))
        layout.addWidget(self.combo_box)
        

        # OK & Cancel buttons
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

    def get_selected_instrument(self):
        """ Get the selected instrument name and type."""
        instrument_type = self.combo_box.currentText()
        name = self.name.text().strip()
        name = name if name else self.combo_box.currentText()
        return name, instrument_type
    

class MyMainWidget(QWidget):
    """ Main widget for the application."""
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Instrument controller")
        self.setStyleSheet("font-size: 14px;")
        self.layout = QHBoxLayout(self)
        self.rm = pyvisa.ResourceManager()
        self.instrs = []
        
        self.icon = QIcon()
        self.icon.addFile("owl.png")
        self.setWindowIcon(self.icon)
        
        # Instrument list layout
        self.select_container = QWidget(self)
        self.select_container.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self.select_layout = QVBoxLayout(self.select_container)
        self.select_layout.addWidget(QLabel("Instrument list:"))
        
        self.list_view = QListView(self)
        self.list_view.spacing()
        self.model = QStandardItemModel(self)
        self.list_view.setModel(self.model)
        self.list_view.clicked.connect(self.on_instrument_selected)
        self.model.itemChanged.connect(self.handle_checkbox_toggle)
        self.select_layout.addWidget(self.list_view)
        
        # button layout under the list
        button_layout = QHBoxLayout()
        self.save_button = QPushButton("Save", parent=self)
        self.save_button.clicked.connect(self.save_state)
        button_layout.addWidget(self.save_button)

        self.load_button = QPushButton("Load", parent=self)
        self.load_button.clicked.connect(self.load_state)
        button_layout.addWidget(self.load_button)
        button_layout.addStretch()

        self.add_button = QPushButton("+", parent=self)
        self.add_button.clicked.connect(self.show_add_dialog)
        button_layout.addWidget(self.add_button)

        self.remove_button = QPushButton("-", parent=self)
        self.remove_button.clicked.connect(self.remove_instrument)
        button_layout.addWidget(self.remove_button)
        
        self.select_layout.addLayout(button_layout)
        self.layout.addWidget(self.select_container)

        # Stacked widget for instrument GUIs
        self.instr_stack = QStackedWidget(self)
        self.instr_stack.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        placeholder = QLabel("No Instrument Selected")
        placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.instr_stack.addWidget(placeholder)
        
        self.layout.addWidget(self.instr_stack)
        self.layout.setStretch(0, 1)
        self.layout.setStretch(1, 5)


    @QtCore.Slot()
    def on_instrument_selected(self, index):
        """Show the GUI for the selected instrument."""
        self.instr_stack.setCurrentIndex(index.row()+1)


    @QtCore.Slot()
    def show_add_dialog(self):
        """Show the instrument selection dialog and add the selected instrument."""
        dialog = InstrSelectionDialog()
        if dialog.exec():  # If the user presses OK
            name, instr_type = dialog.get_selected_instrument()
            uuid = self.get_unique_name(name)
            instr = Instrument(self.model.rowCount(), uuid, instr_type, rm=self.rm, active=False)
            self.add_instrument_to_list(instr)


    @QtCore.Slot()
    def remove_instrument(self):
        """Remove the selected instrument from the list."""
        selected_indexes = self.list_view.selectedIndexes()
        if selected_indexes:
            index = selected_indexes[0]  # Get the first selected index
            self.model.removeRow(index.row())  # Remove the row from the model
        instr = self.instrs.pop([i for i, obj in enumerate(self.instrs) if obj.row == index.row()][0])
        instr.gui.delete()


    @QtCore.Slot()
    def add_instrument_to_list(self, instr: QWidget):
        """Add an instrument to the model while storing its metadata."""
        item = QStandardItem(instr.id)
        item.setCheckable(True)
        item.setCheckState(Qt.CheckState.Unchecked if not instr.active else Qt.CheckState.Checked)
        item.setData(instr, Qt.ItemDataRole.UserRole)
        self.model.appendRow(item)
        self.instr_stack.addWidget(instr.gui)
        self.instrs.append(instr)

    @QtCore.Slot()
    def handle_checkbox_toggle(self, item):
        """Only toggle instrument activation if the checkbox was clicked."""
        instr = item.data(Qt.ItemDataRole.UserRole)
        if instr:
            instr.active = item.checkState() == Qt.CheckState.Checked
            instr.gui.state(instr.active)


    def get_unique_name(self, name):
        """Ensure the name is unique by appending a number if necessary."""
        existing_names = [self.model.item(i).text() for i in range(self.model.rowCount())]

        if name not in existing_names:
            return name

        # If the name exists, append a number to make it unique
        count = 1
        new_name = f"{name} ({count})"
        while new_name in existing_names:
            count += 1
            new_name = f"{name} ({count})"

        return new_name
    
    def save_state(self):
        """Save the window state and list to a JSON file."""
        file_path, _ = QFileDialog.getSaveFileName(self, "Save State", "", "JSON Files (*.json)")

        if not file_path:
            return  # User canceled the save dialog

        state_data = {
            "window_geometry": self.geometry().getRect(),
            "instrument_list": [i.to_dict() for i in self.instrs]
        }

        with open(file_path, "w", encoding="utf-8") as file:
            json.dump(state_data, file, indent=4)
    

    def load_state(self):
        """Load the window state and list from a JSON file."""
        file_path, _ = QFileDialog.getOpenFileName(self, "Load State", "", "JSON Files (*.json)")

        if not file_path:
            return

        try:
            with open(file_path, "r") as file:
                state_data = json.load(file)

            self.model.clear()  # Clear existing data
            for instrument_data in state_data.get("instrument_list", []):
                instrument = Instrument.from_dict(instrument_data, rm=self.rm)
                self.add_instrument_to_list(instrument)

        except Exception as e:
            print(f"Failed to load state: {e}")


if __name__ == "__main__":
    app = QApplication([])

    widget = MyMainWidget()
    widget.resize(800, 600)
    widget.show()

    sys.exit(app.exec())