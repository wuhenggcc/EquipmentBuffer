import serial
import time
from math import floor


class PositionerDriver:
    """
    original code by Matthieu Doat.
    For controlling the home made rotator of TULIPS"""
    def __init__(self, address: str):
        self.address = address
        self.verbose = True
        self.ser = None

        ### Positioner parameters shouldn't be changed by the user
        self.bst_voltage = 0
        self.bst_target_voltage = 40
        self.bst_voltage_limit = 50
        self.bst_pot_factor = 0.026455     # Measured voltage = Real voltage * factor 
        self.sig_pot_factor = 0.0266 
        self.opamp_gain = 37.899
        self.step_factor = 0.012    # Degrees = Number of steps * step_factor(bst_voltage)
        self.stick_time = 3000 ### unit of us
        self.max_position = 290
        self.min_position = 50

        self._offset_angle = 10
        self.max_angle = self.max_position+self._offset_angle
        self.min_angle = self.min_position+self._offset_angle

        self._P = 10
        self._I = 10
        self._D = 0
        self._position = 170
        self._target_position = 170
        print(f"Angles must be in between {self.min_angle} and {self.max_angle} degrees.")

    def init(self):
        self.set_stick_time(self.stick_time)
        self.update_boost_voltage(self.bst_target_voltage)
        self.set_dac_max(self.bst_target_voltage*4095/(5*self.opamp_gain))
        self.set_pid("P", self._P)
        self.set_pid("I", self._I)
        self.set_pid("D", self._D)
        self.measure_current_position()

    def connect(self, port=None, baudrate=9600, timeout=1):
        if self.ser and self.ser.is_open:
            if self.verbose:
                print("Already connected.")
            return
        port = self.address if port is None else port
        self.ser = serial.Serial(port, baudrate, timeout=timeout)
        if self.verbose:
            print(f"Connected to {port}")
        time.sleep(1)

    def is_connected(self):
        if self.ser is None:
            return False
        return True

    def query_command(self, command, param=None):
        if param is None:
            command_str = f"{command}\n"
        else:
            command_str = f"{command}:{param}\n"
        self.ser.write(command_str.encode())
        time.sleep(0.04)
        result = self.ser.readline().decode().strip()
        return result

    @property
    def position(self):
        return self._position

    @position.setter
    def position(self, value):
        self.target_position = value
        self.update_position()

    @property
    def target_position(self):
        return self._target_position

    @target_position.setter
    def target_position(self, value):
        if value < self.min_position or value > self.max_position:
            raise ValueError(f"The target position should be between {self.min_position} and {self.max_position} degrees.")
        self._target_position = value

    @property
    def offset_angle(self):
        return self._offset_angle

    @property
    def angle(self):
        return self.position + self.offset_angle

    @angle.setter
    def angle(self, value: float):
        value = float(value)
        if value < self.min_angle or value > self.max_angle:
            raise ValueError(f"The angle should be between {self.min_angle} and {self.max_angle} degrees.")
        self.position = value - self.offset_angle

    @property
    def P(self):
        return self._P

    @property
    def I(self):
        return self._I
    
    @property
    def D(self):
        return self._D

    @P.setter
    def P(self, value):
        value = float(value)
        if value < 0:
            raise ValueError("The P value should be positive.")
        self.set_pid("P", value)
        self._P = value
    
    @I.setter
    def I(self, value):
        value = float(value)
        if value < 0:
            raise ValueError("The I value should be positive.")
        self.set_pid("I", value)
        self._I = value
    
    @D.setter
    def D(self, value):
        value = float(value)
        if value < 0:
            raise ValueError("The D value should be positive.")
        self.set_pid("D", value)
        self._D = value

    def set_pid(self, param, value):
        if param not in ["P", "I", "D"]:
            raise ValueError("The parameter should be P, I or D.")
        result = self.query_command(f"SET_{param}", value)
        try:
            def_value = float(result.split(f"DEF_{param}:")[1])
            assert def_value==value, "The defined value does not correspond to the expected value {} != {}".format(def_value, value)
            if self.verbose:
                print(f"{param} value as succesfully been set to :{def_value}")
        except:
            raise Exception(f"The {param} value as not succesfully been set, result:", result)

    def read_pot_pzo(self):
        self.ser.write("READ_POT_PZO\n".encode())
        time.sleep(0.04)
        result = self.ser.readline().decode().strip()
        try:
            value = int(result.split("POT_PZO:")[1])
            if value > 35000:
                value = 0
            if self.verbose:
                print("The current value of the positioner potentiometer is :", value)
            return value
        except:
            raise Exception("Read pot pzo encoutered an error, result:", result)
        
    def read_pot_bst(self):
        self.ser.write("READ_POT_BST\n".encode())
        result = self.ser.readline().decode().strip()
        try:
            value = int(result.split("POT_BST:")[1])
            if self.verbose:
                print("The current value of the boost potentiometer is :", value)
            return value
        except:
            raise Exception("Read pot bst encoutered an error, result:", result)

    def read_pot_sig(self):
        self.ser.write("READ_POT_SIG\n".encode())
        result = self.ser.readline().decode().strip()
        try:
            value = int(result.split("POT_SIG:")[1])
            if self.verbose:
                print("The current value of the signal potentiometer is :", value)
            return value
        except:
            raise Exception("Read pot sig encoutered an error, result:", result)


    def set_bst_val(self, value):
        value = int(value)
        assert value < 1024 and value >= 0, "The value should be between 0 and 1023"
        self.ser.write("SET_BST:{}\n".format(value).encode())
        result = self.ser.readline().decode().strip()
        try:
            def_value = int(result.split("DEF_BST:")[1])
            assert def_value==value, "The defined value does not correspond to the expected value {} != {}".format(def_value, value)
            if self.verbose:
                print("Value for bst_val as succesfully been set to :{}".format(def_value))
        except:
            raise Exception("The value for bst_val as not succesfully been set, result:", result)
    
    def set_dac_max(self, value):
        value = int(value)
        assert value <= 4095 and value >= 0, "The value should be between 0 and 4095"
        self.ser.write("SET_DAC:{}\n".format(value).encode())
        result = self.ser.readline().decode().strip()
        try:
            def_value = int(result.split("DEF_DAC:")[1])
            assert def_value==value, "The defined value does not correspond to the expected value {} != {}".format(def_value, value)
            if self.verbose:
                print("Value for dac_max as succesfully been set to :{}".format(def_value))
        except:
            raise Exception("The value for dac_max as not succesfully been set, result:", result)
        

    def set_step_number(self, value):
        value = int(value)
        assert value < 50000 and value >= 0, "This value should not be too high and should be greater than 0."
        self.ser.write("SET_STEP:{}\n".format(value).encode())
        result = self.ser.readline().decode().strip()
        try:
            def_value = int(result.split("DEF_STEP:")[1])
            assert def_value==value, "The defined value does not correspond to the expected value {} != {}".format(def_value, value)
            if self.verbose:
                print("Value for step_number as succesfully been set to :{}".format(def_value))
        except:
            raise Exception("The value for step_number as not succesfully been set, result:", result)
        
    def get_step_number(self):
        self.ser.write("GET_STEP\n".encode())
        result = self.ser.readline().decode().strip()
        try:
            value = int(result.split("NUM_STEP:")[1])
            if self.verbose:
                print("The remaining number of step is :", value)
            return value
        except:
            raise Exception("Get step encoutered an error, result:", result)
        
        
    def set_stick_time(self, value):
        value = int(value)
        assert value <= 100000 and value >= 3000, "The stick time should be between 3e3µs (3ms) and 1e6µs (100ms)."
        self.ser.write("SET_TIME:{}\n".format(value).encode())
        result = self.ser.readline().decode().strip()
        try:
            def_value = int(result.split("DEF_TIME:")[1])
            assert def_value==value, "The defined value does not correspond to the expected value {} != {}".format(def_value, value)
            if self.verbose:
                print("Value for stick_time as succesfully been set to :{}".format(def_value))
        except:
            raise Exception("The value for stick_time as not succesfully been set, result:", result)
    
    def set_forward(self):
        self.ser.write("SET_FW\n".encode())
        result = self.ser.readline().decode().strip()
        assert result == "DEF_FW", "There was a problem during the forward configuration."
        if self.verbose:
            print("Succesfully set in forward mode.")
    
    def set_backward(self):
        self.ser.write("SET_BW\n".encode())
        result = self.ser.readline().decode().strip()
        assert result == "DEF_BW", "There was a problem during the backward configuration."
        if self.verbose:
            print("Succesfully set in backward mode.")

    def pot_pzo_to_angle(self, pot_pzo_val):
        return (pot_pzo_val/32744)*(360*0.919674) # Previoulsy was 3707/4033

    def update_position(self):
        current_position = self.position
        while abs(self.target_position-current_position) > 0.1:
            if self.target_position > current_position:
                self.set_forward()
                new_step_number = int(abs(self.target_position-current_position)/self.step_factor)
                if new_step_number == 0:
                    new_step_number = 5
                self.set_step_number(new_step_number)
            else:
                self.set_backward()
                new_step_number = int(abs(self.target_position-current_position)/self.step_factor)
                if new_step_number == 0:
                    new_step_number = 5
                self.set_step_number(new_step_number)
            while self.get_step_number() != 0:
                pass
            self.measure_current_position()
            current_position = self.pot_pzo_to_angle(self.read_pot_pzo())
        self.measure_current_position()

    def update_boost_voltage(self, new_voltage):
        assert self.bst_voltage_limit >= new_voltage, "The new voltage is above the limit."
        self.set_bst_val(floor(1023*new_voltage*self.bst_pot_factor/5))

    def measure_bst_voltage(self):
        self.bst_voltage = 5*self.read_pot_bst()/(1023*self.bst_pot_factor)
        return self.bst_voltage

    def measure_current_position(self):
        self._position = self.pot_pzo_to_angle(self.read_pot_pzo())
        return self._position
    
