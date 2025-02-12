class AgilentE3640A_Dummy:
    def __init__(self):
        self.volt = 0
        self.vrange = "LOW"
        self.volt_lim = 0
        self.volt_max = 8
        self.curr_lim = 0
        self.curr_max = 3
        self.curr = 5
        self.state = 0
        self.address = "GPIB0::5::INSTR"
        
    def connect(self, address: str):
        """ Connect to the instrument. """
        if address == self.address:
            print(f"Connected to {address}")
        else:
            raise ValueError("Invalid address")
        
    def set_vrange(self, vrange: str):
        """ Set the voltage range. """
        print(f"Setting voltage range: {vrange}")
        self.vrange = vrange
        if self.vrange == "HIGH":
            print("Voltage range set to HIGH")
            self.volt_max = 20
            self.curr_max = 1.5
        else:
            self.volt_max = 8
            self.curr_max = 3
    
    def set_volt(self, volt: float):
        """ Set the laser voltage [V]. """
        print(f"Setting voltage: voltage {volt}")
        self.volt = volt
        
    def get_curr(self):
        """ Set the laser current [A]. """
        return self.curr
    
    def get_volt_max(self):
        return self.volt_max
    
    def get_curr_max(self):
        return self.curr_max
        
    def set_params(self, volt: float, curr: float):
        """ Set the laser voltage [V] and current [A]. """
        print(f"Setting limit: apply {volt} , {curr}")
        self.volt_lim = volt
        self.curr_lim = curr
        
    def get_params(self): # return [volt, curr]
        """ Get the laser voltage [V] and current [A]. """
        return self.volt_lim, self.curr_lim
    
    def set_output_state(self, state: bool):
        """ Set the voltage output state. """
        self.state = state
        print(f"Status: {state}")
        
    def disconnect(self):
        """ Disconnect from the instrument. """
        print("Disconnected")
    

class Agilent816xB_Dummy:
    def __init__(self):
        self.laser_wav = 1550 # nm
        self.detect_wv = 1550 # nm
        self.detect_pw = 5 # mW
        self.laser_pw = 10
        self.period = 0.1
        self.address = "GPIB0::20::INSTR"
        self.state = 0
        
    def connect(self, address: str):
        """ Connect to the instrument. """
        if address == self.address:
            print(f"Connected to {address}")
        else:
            raise ValueError("Invalid address")
    
    def set_laser_wav(self, wv):
        self.laser_wav = wv
        print(f"Setting laser wavelength: {wv}")
        
    def set_detect_wav(self, wv: float):
        """ Set the detector wavelength [nm]. """
        self.detect_wv = wv
        print(f"Setting detector wavelength: {wv}")
        
    def set_laser_pow(self, power: float):
        """ Set the laser power [dBm]. """
        self.laser_pw = power
        print(f"Setting laser power: {power} dBm")
        
    def get_laser_wav(self):
        """ Get the laser wavelength [nm]. """
        return self.laser_wav
    
    def get_detect_wav(self):
        """ Get the detector wavelength [nm]. """
        return self.detect_wv
    
    def get_detect_pow(self) -> float:
        """ Get the detector power. """
        return self.detect_pw
    
    def set_laser_unit(self, unit: str):
        """ Set the laser unit. """
        print(f"Setting laser unit: {unit}")
        
    def set_detect_unit(self, unit: str):
        """ Set the laser unit. """
        print(f"Setting detect unit: {unit}")
    
    def set_detect_avgtime(self, period: float):
        """ Set the detector average time [s]. """
        self.period = period
        print(f"Setting detector average time: {period} s")
        
    def set_laser_state(self, state: bool):
        """ Set the voltage output state. """
        self.state = state
        print(f"Status: {state}")
        
    def disconnect(self):
        """ Disconnect from the instrument. """
        print("Disconnected")