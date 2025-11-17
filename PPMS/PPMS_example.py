import requests
import traceback


class PPMSExample():
    def __init__(self, host="127.0.0.1", port=5001):
        self.url_data = f"http://{host}:{port}/data"
        self.url_cmd = f"http://{host}:{port}/command"


    def get_field(self):
        data = self.get_all()
        return data.get("field", None) if data else None

    def get_temperature(self):
        data = self.get_all()
        return data.get("temperature", None) if data else None
    
    def get_rotator(self):
        data = self.get_all()
        return data.get("rotator", None) if data else None

    def get_all(self):
        """Send GET request to the Flask server."""
        try:
            response = requests.get(self.url_data, timeout=2)
            response.raise_for_status()
            data = response.json()
            print(data)
            return data
        except Exception as e:
            msg = f"Request error: {e}\n{traceback.format_exc()}"
            print(msg)
            return {}
    
    def send_command(self, cmd, args=None):
        """Send a command to the PPMS Flask server."""
        if args is None:
            args = {}
        try:
            payload = {"command": cmd, "args": args}
            # print("Sending command:", payload)
            response = requests.post(self.url_cmd, json=payload, timeout=3)
            response.raise_for_status()
            data = response.json()
            print("Command response:", data)
            return data
        except Exception as e:
            msg = f"Command error: {e}\n{traceback.format_exc()}"
            print(msg)
            return {}
    
    def set_field(self, target_field, ramp_rate, approach='linear'):
        cmd_arg = {
            "target": target_field,
            "rate": ramp_rate,
            "approach": approach,
        }
        return self.send_command("set_field", cmd_arg)

    def set_temperature(self, target_temp, ramp_rate, approach='linear'):
        cmd_arg = {
            "target": target_temp,
            "rate": ramp_rate,
            "approach": approach,
        }
        return self.send_command("set_temperature", cmd_arg)
    
    def set_rotator(self, target, rate, approach='linear'):
        pass