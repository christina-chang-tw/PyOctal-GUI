from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QLabel, QComboBox
from PySide6.QtCore import Qt, Slot
import pyvisa

from pyoctal.instruments import AgilentE3640A

from instruments.base import Instrument_GUI, WriteOnlyVar, ReadOnlyVar

class Voltage(WriteOnlyVar):
    def __init__(self, instr, *args, **kwargs):
        super().__init__(instr, *args, **kwargs)
        self.label = QLabel("Voltage [V]: ", parent=self)
        self._value = QLineEdit("0", parent=self)
        self._value.editingFinished.connect(self.set_value)
        self.layout.addWidget(self.label, 2)
        self.layout.addWidget(self._value, 2)
    
    @Slot()
    def set_value(self):
        self.instr.set_volt(self._value.text())
        
    def update_value_max(self, vlim: float):
        self.double_validator.setBottom(0.0)
        self.double_validator.setTop(float(vlim))
        self._value.setValidator(self.double_validator)
        
    def get_value(self):
        pass
    
class VoltageLimit(WriteOnlyVar):
    def __init__(self, instr, *args, **kwargs):
        super().__init__(instr, *args, **kwargs)
        self.label = QLabel("Voltage limit [V]: ", parent=self)
        self._value = QLineEdit("0", parent=self)
        self._value.editingFinished.connect(self.set_value)

        self.layout.addWidget(self.label, 2)
        self.layout.addWidget(self._value, 2)
    
    @Slot()
    def set_value(self):
        _, curr_lim = self.instr.get_params()
        self.instr.set_params(self._value.text(), curr_lim)
        
    def update_value_max(self):
        max_value = self.instr.get_volt_max()
        self.double_validator.setBottom(0.0)
        self.double_validator.setTop(float(max_value))
        self._value.setValidator(self.double_validator)
        
    def callback(self, func: callable):
        self._value.textChanged.connect(func)
    
class Current(ReadOnlyVar):
    def __init__(self, instr, *args, **kwargs):
        super().__init__(instr, *args, **kwargs)
        self.label = QLabel("Current [A]: ", parent=self)
        self._value = QLabel(parent=self)
        self._value.setContentsMargins(6, 0, 0, 0)
        self.get_value()
        self.layout.addWidget(self.label, 2)
        self.layout.addWidget(self._value, 2)
        
    def get_value(self):
        return self.instr.get_curr()
        
    def update_value(self, value: float):
        print(f"Current - Updated value: {value}")
        self._value.setText(str(value))

        
class CurrentLimit(ReadOnlyVar):
    def __init__(self, instr, *args, **kwargs):
        super().__init__(instr, *args, **kwargs)
        self.label = QLabel("Current limit [A]: ", parent=self)
        self._value = QLineEdit("0", parent=self)
        self._value.editingFinished.connect(self.set_value)
        self.layout.addWidget(self.label, 2)
        self.layout.addWidget(self._value, 2)
    
    @Slot()
    def set_value(self):
        volt_lim, _ = self.instr.get_params()
        self.instr.set_params(volt_lim, self._value.text())
        
    def update_value_max(self):
        max_value = self.instr.get_curr_max()
        self.double_validator.setBottom(0.0)
        self.double_validator.setTop(float(max_value))
        self._value.setValidator(self.double_validator)

    
class VRange(WriteOnlyVar):
    def __init__(self, instr, *args, **kwargs):
        super().__init__(instr, *args, **kwargs)
        self.label = QLabel("Range: ", parent=self)
        self._value = QComboBox(parent=self)
        self._value.currentTextChanged.connect(self.set_value)
        self._value.addItems(["LOW", "HIGH"])
        self.layout.addWidget(self.label, 2)
        self.layout.addWidget(self._value, 2)
        
    def set_value(self, value: str=None):
        if value is None:
            value = self._value.currentText()
        self.instr.set_vrange(value)
    
    def callback(self, func: callable):
        self._value.currentTextChanged.connect(func)


class AgilentE3640A_GUI(Instrument_GUI):
    def __init__(self, rm: pyvisa.ResourceManager, *args, **kwargs):
        super().__init__(name="Agilent E3640A", instr=AgilentE3640A(), rm=rm, *args, **kwargs)
        self.window()
        self.layout.alignment = Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter
        
    def window(self):
        self.widget = QWidget()
        
        # instantiate widgets
        self.widget_layout = QVBoxLayout(self.widget)
        self.vrange = VRange(self.instr, parent=self)
        self.voltage = Voltage(self.instr, parent=self)
        self.voltage_lim = VoltageLimit(self.instr, parent=self)
        self.current = Current(self.instr, parent=self)
        self.current_lim = CurrentLimit(self.instr, parent=self)
        self.widget_layout.addWidget(self.vrange)
        self.widget_layout.addWidget(self.voltage)
        self.widget_layout.addWidget(self.voltage_lim)
        self.widget_layout.addWidget(self.current)
        self.widget_layout.addWidget(self.current_lim)
        
        # set up callbacks
        self.vrange.callback(self.voltage_lim.update_value_max)
        self.vrange.callback(self.current_lim.update_value_max)
        self.voltage_lim.callback(self.voltage.update_value_max)
        self.read_channel.register_callback(self.current.get_value)
        self.read_channel.data_ready.connect(self.current.update_value)
        
        self.voltage.update_value_max(self.voltage_lim.value.text())

        self.layout.addWidget(self.widget)
        self.layout.addStretch(1)
        
    def initialise(self, state: bool):
        if state is False:
            return
        
        self.vrange.set_value()
        self.voltage_lim.update_value_max()
        self.voltage_lim.set_value()
        self.voltage.update_value_max(self.voltage_lim.value.text())
        self.voltage.set_value()
        self.current_lim.update_value_max()
        self.current_lim.set_value()

    def state(self, val: bool):
        self.instr.set_output_state(val)
        self.read_channel.change_state(val)            