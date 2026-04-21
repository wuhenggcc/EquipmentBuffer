import serial
import time
from math import floor


class Positioner:
    """
    original code by Matthieu Doat.
    For controlling the home made rotator of TULIPS"""
    def __init__(self):
        self.verbose = True
        self.ser = None
        self.position = 0
        self.target_position = 0
        self.bst_voltage = 0
        self.bst_target_voltage = 0
        self.bst_voltage_limit = 0
        self.bst_pot_factor = 0     # Measured voltage = Real voltage * factor 
        self.sig_pot_factor = 0 
        self.opamp_gain = 0
        self.step_factor = 0    # Degrees = Number of steps * step_factor(bst_voltage)
        self.stick_time = 0
        self.P = 0
        self.I = 0
        self.D = 0
        self.max_angle = 270
        self.min_angle = 0

    def connect(self, port, baudrate=9600, timeout=1):
        if self.ser and self.ser.is_open:
            if self.verbose:
                print("Already connected.")
            return

        self.ser = serial.Serial(port, baudrate, timeout=timeout)
        if self.verbose:
            print(f"Connected to {port}")
        time.sleep(1)

    def is_connected(self):
        if self.ser == None:
            return False
        return True

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
        
    def set_p(self, value):
        value = float(value)
        assert value >= 0, "The P value should be positive."
        self.ser.write("SET_P:{}\n".format(value).encode())
        result = self.ser.readline().decode().strip()
        try:
            def_value = float(result.split("DEF_P:")[1])
            assert def_value==value, "The defined value does not correspond to the expected value {} != {}".format(def_value, value)
            if self.verbose:
                print("P value as succesfully been set to :{}".format(def_value))
        except:
            raise Exception("The P value as not succesfully been set, result:", result)
        
    def set_i(self, value):
        value = float(value)
        assert value >= 0, "The I value should be positive."
        self.ser.write("SET_I:{}\n".format(value).encode())
        result = self.ser.readline().decode().strip()
        try:
            def_value = float(result.split("DEF_I:")[1])
            assert def_value==value, "The defined value does not correspond to the expected value {} != {}".format(def_value, value)
            if self.verbose:
                print("I value as succesfully been set to :{}".format(def_value))
        except:
            raise Exception("The I value as not succesfully been set, result:", result)
    
    def set_d(self, value):
        value = float(value)
        assert value >= 0, "The D value should be positive."
        self.ser.write("SET_D:{}\n".format(value).encode())
        result = self.ser.readline().decode().strip()
        try:
            def_value = float(result.split("DEF_D:")[1])
            assert def_value==value, "The defined value does not correspond to the expected value {} != {}".format(def_value, value)
            if self.verbose:
                print("D value as succesfully been set to :{}".format(def_value))
        except:
            raise Exception("The D value as not succesfully been set, result:", result)
    
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
        assert self.target_position <= self.max_angle, "The target angle is greater than the max angle."
        assert self.target_position >= self.min_angle, "The target angle is smaller than the min angle."
        while abs(self.target_position-self.position) > 0.1:
            if self.target_position > self.position:
                self.set_forward()
                new_step_number = int(abs(self.target_position-self.position)/self.step_factor)
                if new_step_number == 0:
                    new_step_number = 5
                self.set_step_number(new_step_number)
            else:
                self.set_backward()
                new_step_number = int(abs(self.target_position-self.position)/self.step_factor)
                if new_step_number == 0:
                    new_step_number = 5
                self.set_step_number(new_step_number)
            while self.get_step_number() != 0:
                pass
            self.position = self.pot_pzo_to_angle(self.read_pot_pzo())

    def update_boost_voltage(self, new_voltage):
        assert self.bst_voltage_limit >= new_voltage, "The new voltage is above the limit."
        self.set_bst_val(floor(1023*new_voltage*self.bst_pot_factor/5))

    def measure_bst_voltage(self):
        self.bst_voltage = 5*self.read_pot_bst()/(1023*self.bst_pot_factor)
        return self.bst_voltage

    def measure_current_position(self):
        self.position = self.pot_pzo_to_angle(self.read_pot_pzo())
        return self.position
    
    def init(self):
        self.set_stick_time(self.stick_time)
        self.update_boost_voltage(self.bst_target_voltage)
        self.set_dac_max(self.bst_target_voltage*4095/(5*self.opamp_gain))
        self.set_p(self.P)
        self.set_i(self.I)
        self.set_d(self.D)

                         


    