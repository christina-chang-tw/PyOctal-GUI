from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QComboBox, QLineEdit
from PySide6.QtCore import Qt, Slot
import pyvisa

from pyoctal.instruments import Agilent8163B, Agilent8164B

from instruments.base import Instrument_GUI, WriteOnlyVar, ReadOnlyVar
from unit import si_convert

class InputWavelength(WriteOnlyVar):
    """Input wavelength for the laser."""
    def __init__(self, instr):
        super().__init__(instr)
        self.label = QLabel("Input Wavelength: ")
        self._value = QLineEdit("1550")
        self._value.editingFinished.connect(self.set_value)
        self.unit = QComboBox()
        self.unit.addItems(["nm", "um"])
        self.layout.addWidget(self.label, 2)
        self.layout.addWidget(self._value, 2)
        self.layout.addWidget(self.unit, 1)
    
    @Slot()
    def set_value(self):
        """Set the input wavelength of the laser."""
        unit = self.unit.currentText()
        value = float(self._value.text())
        if unit != "nm":
            value = si_convert(value, unit, "s")
        self.instr.set_laser_wav(value)

    
class InputPower(WriteOnlyVar):
    """Input power for the laser."""
    def __init__(self, instr):
        super().__init__(instr)

        self.label = QLabel("Input Power: ")
        self._value = QLineEdit("0")
        self._value.editingFinished.connect(self.set_value)
        
        self.unit = QComboBox()
        self.unit.addItems(["dBm", "mW"])
        self.unit.currentTextChanged.connect(self.set_unit)
        
        self.layout.addWidget(self.label, 2)
        self.layout.addWidget(self._value, 2)
        self.layout.addWidget(self.unit, 1)
    
    @Slot()
    def set_value(self):
        """Set the input power of the laser."""
        self.instr.set_laser_pow(self._value.text())
        
    @Slot()
    def set_unit(self, value: str=None):
        """Set the unit of the input power."""
        if value is None:
            value = self.unit.currentText()
        self.instr.set_laser_unit(value)

   
class OutputWavelength(WriteOnlyVar):
    """Output wavelength for the laser."""
    def __init__(self, instr):
        super().__init__(instr)
        
        self.label = QLabel("Output Wavelength: ")
        self._value = QLineEdit("1550")
        self._value.editingFinished.connect(self.set_value)

        self.unit = QComboBox()
        self.unit.addItems(["nm", "um"])

        self.layout.addWidget(self.label, 2)
        self.layout.addWidget(self._value, 2)
        self.layout.addWidget(self.unit, 1)
    
    @Slot()
    def set_value(self):
        """Set the output wavelength of the laser."""
        unit = self.unit.currentText()
        value = self._value.text()
        if unit != "nm":
            value = si_convert(value, unit, "m")
        self.instr.set_detect_wav(value)
         
class OutputPower(ReadOnlyVar):
    """Output power for the laser."""
    def __init__(self, instr):
        super().__init__(instr)
        
        self.label = QLabel("Output Power: ")
        self._value = QLabel("-----")
        self._value.setContentsMargins(6, 0, 0, 0)

        self.unit = QComboBox()
        self.unit.addItems(["dBm", "mW"])
        self.unit.currentTextChanged.connect(self.set_unit)

        self.layout.addWidget(self.label, 2)
        self.layout.addWidget(self._value, 2)
        self.layout.addWidget(self.unit, 1)
    
    @Slot()
    def set_unit(self, value: str=None):
        """Set the unit of the output power."""
        if value is None:
            value = self.unit.currentText()
        self.instr.set_detect_unit(value)
         
    def get_value(self) -> float:
        """Get the output power of the laser."""
        return self.instr.get_detect_pow()
    
    @Slot()
    def update_value(self, value: float):
        """Update the output power of the laser."""
        self._value.setText(str(value))
        
    @Slot()
    def default(self):
        """Set the output power to default to distinguish between the laser on/off state."""
        self._value.setText("-----")
        
class AverageTime(WriteOnlyVar):
    """Average time for the laser."""
    def __init__(self, instr):
        super().__init__(instr)
        self.label = QLabel("Average Time: ")
        self._value = QLineEdit("100")
        self._value.editingFinished.connect(self.set_value)

        self.unit = QComboBox()
        self.unit.addItems(["ms", "us", "s"])
        self.layout.addWidget(self.label, 2)
        self.layout.addWidget(self._value, 2)
        self.layout.addWidget(self.unit, 1)
    
    @Slot()
    def set_value(self):
        """Set the average time of the laser."""
        unit = self.unit.currentText()
        value = float(self._value.text())
        if unit != "s":
            value = si_convert(value, unit, "s")
        self.instr.set_detect_avgtime(value)


class Agilent816xB_GUI(Instrument_GUI):
    """GUI for the Agilent 816xB series."""
    def __init__(self, name: str, instr, *args, **kwargs):
        super().__init__(name=name, instr=instr, *args, **kwargs)
        self.window()
        self.layout.alignment = Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter     
        
    def window(self):
        """Create the GUI window for this specific instrument."""
        self.widget = QWidget(self)
        self.widget_layout = QVBoxLayout(self.widget)
        self.input_wavelength = InputWavelength(self.instr)
        self.input_power = InputPower(self.instr)
        self.output_wavelength = OutputWavelength(self.instr)
        self.output_power = OutputPower(self.instr)
        self.average_time = AverageTime(self.instr)
        
        self.widget_layout.addWidget(self.input_wavelength)
        self.widget_layout.addWidget(self.input_power)
        self.widget_layout.addWidget(self.output_wavelength)
        self.widget_layout.addWidget(self.output_power)
        self.widget_layout.addWidget(self.average_time)
        
        self.read_channel.register_callback(self.output_power.get_value)
        self.read_channel.data_ready.connect(self.output_power.update_value)
        
        self.layout.addWidget(self.widget)
        self.layout.addStretch(1)
        
    def initialise(self, state: bool):
        """Initialise the instrument."""
        if state is False:
            return

        self.input_wavelength.set_value()
        self.input_power.set_unit()
        self.input_power.set_value()
        self.output_wavelength.set_value()
        self.output_power.set_unit()
        self.average_time.set_value()
        self.state(False)
        
    def state(self, val: bool):
        """Turn the laser on/off."""
        self.instr.set_laser_state(val)
        self.read_channel.change_state(val)
        self.output_power.default()
    

class Agilent8164B_GUI(Agilent816xB_GUI):
    """GUI for the Agilent 8164B."""
    def __init__(self, rm: pyvisa.ResourceManager, *args, **kwargs):
        super().__init__(name="Agilent 8164B",
                         instr=Agilent8164B(rm=rm), *args, **kwargs)

class Agilent8163B_GUI(Agilent816xB_GUI):
    """GUI for the Agilent 8163B."""
    def __init__(self, rm: pyvisa.ResourceManager, *args, **kwargs):
        super().__init__(name="Agilent 8163B",
                         instr=Agilent8163B(rm=rm), *args, **kwargs)
