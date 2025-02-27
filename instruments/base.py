import time

from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QHBoxLayout, QPushButton
from PySide6.QtCore import QThread, Qt, Signal
from PySide6.QtGui import QDoubleValidator

class Channel(QThread):
    data_ready = Signal(type)
    def __init__(self, *args, **kwargs):
        super().__init__()
        self.is_running = True
        self.callbacks = []
        
    def register_callback(self, func):
        self.callbacks.append(func)

    def run(self):
        while self.is_running:
            for callback in self.callbacks:
                data = callback()
                self.data_ready.emit(data)
                time.sleep(0.5)
                
    def change_state(self, state: bool):
        self.is_running = state
        if self.is_running:
            self.start()
        else:
            self.terminate()
            self.wait()
            
                
    def stop(self):
        self.is_running = False
        self.quit()
        self.wait()

class Var(QWidget):
    def __init__(self, instr, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.instr = instr
        self._value = 0
        self.double_validator = QDoubleValidator()
        self.double_validator.setNotation(QDoubleValidator.Notation.StandardNotation)
        
        self.layout = QHBoxLayout(self)
        self.layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.setContentsMargins(0, 0, 0, 0)


    @property
    def value(self):
        return self._value
    
class WriteOnlyVar(Var):
    def __init__(self, instr, *args, **kwargs):
        super().__init__(instr, *args, **kwargs)
        
    def set_value(self, *args, **kwargs):
        """Set the value of the variable."""
        raise NotImplementedError
    
    
class ReadOnlyVar(Var):
    def __init__(self, instr, *args, **kwargs):
        super().__init__(instr, *args, **kwargs)
    
    def get_value(self, *args, **kwargs):
        raise NotImplementedError

class Address(WriteOnlyVar):
    connect_signal = Signal(bool)
    
    def __init__(self, instr):
        super().__init__(instr)
        self.connect_status = False
        self.label = QLabel("Address: ", parent=self)
        self._value = QLineEdit(placeholderText="i.e. GPIB0::1::INSTR", parent=self)
        self.connect_button = QPushButton("Connect", parent=self)
        self.connect_button.clicked.connect(self.connect_to_instr)
        self.con = QLabel(parent=self)
        self.con.setFixedSize(15, 15)
        self.con.setStyleSheet("border-radius: 7px; background-color: red;")
        self.layout.addWidget(self.label)
        self.layout.addWidget(self._value)
        self.layout.addWidget(self.connect_button)
        self.layout.addWidget(self.con)

    def connect_to_instr(self):
        if self.connect_status:
            self.instr.disconnect()
            self.con.setStyleSheet("border-radius: 7px; background-color: red;")
            self.connect_status = False
            self.connect_signal.emit(False)
            self.connect_button.setText("Connect")
        else:
            try:
                self.instr.connect(self._value.text())
                self.con.setStyleSheet("border-radius: 7px; background-color: green;")
                self.connect_status = True
                self.connect_signal.emit(True)
                self.connect_button.setText("Disconnect")
            except ValueError:
                pass

    @property
    def value(self):
        return self._value.text()

    @value.setter
    def value(self, value: str):
        self._value.setText(value)


class Instrument_GUI(QWidget):
    def __init__(self, name, instr, addr=None):
        super().__init__()
        self.instr = instr
        self.read_channel = Channel()
        
        self.layout = QVBoxLayout(self)
        label = QLabel(f"Instrument type: {name}", parent=self)
        label.setContentsMargins(0, 0, 0, 15)
        self.layout.addWidget(label, alignment=Qt.AlignmentFlag.AlignCenter)

        self._addr = Address(self.instr)
        if addr:
            self._addr.value = addr
        self._addr.connect_signal.connect(self.initialise)
        self.layout.addWidget(self._addr)
        
    def window(self):
        """Adding instrument specific widgets to the layout."""
        raise NotImplementedError
    
    def state(self, val: bool):
        """Get the state of the instrument."""
        raise NotImplementedError
    
    def initialise(self, state: bool):
        raise NotImplementedError
    
    def delete(self):
        self.read_channel.stop()
    
    @property
    def addr(self):
        return self._addr.value