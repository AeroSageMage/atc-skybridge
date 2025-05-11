import os
import json
import time
from typing import Dict, Any, Optional
from datetime import datetime

class SimAPIHandler:
    """Handles SimAPI file I/O operations"""
    
    def __init__(self, base_path: str = None):
        if base_path is None:
            # If no base path provided, use the script's directory
            script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            self.base_path = os.path.join(script_dir, 'SayIntentionsAI')
        else:
            self.base_path = base_path
            
        self.input_path = os.path.join(self.base_path, 'simAPI_input.json')
        self.output_path = os.path.join(self.base_path, 'simAPI_output.jsonl')
        
        # Create SimAPI directory if it doesn't exist
        os.makedirs(self.base_path, exist_ok=True)
    
    def write_input_data(self, data: Dict[str, Any]):
        """Write data to the SimAPI input file"""
        try:
            with open(self.input_path, 'w') as f:
                json.dump(data, f, indent=2)
            return True
        except Exception as e:
            print(f"Error writing SimAPI input: {e}")
            return False
    
    def read_output_data(self) -> Optional[Dict[str, Any]]:
        """Read and process the SimAPI output file"""
        if not os.path.exists(self.output_path):
            return None
            
        try:
            with open(self.output_path, 'r') as f:
                for line in f:
                    try:
                        data = json.loads(line.strip())
                        setvar = data.get('setvar')
                        
                        if setvar == 'COM_RADIO_SET_HZ':
                            # Convert Hz to MHz for COM1 active
                            return {
                                'setvar': setvar,
                                'radio': '1',
                                'value': data['value']
                            }
                        elif setvar == 'COM2_RADIO_SET_HZ':
                            # Convert Hz to MHz for COM2 active
                            return {
                                'setvar': setvar,
                                'radio': '2',
                                'value': data['value']
                            }
                        elif setvar == 'COM_STBY_RADIO_SET_HZ':
                            # Convert Hz to MHz for COM1 standby
                            return {
                                'setvar': setvar,
                                'radio': '1',
                                'value': data['value'],
                                'is_standby': True
                            }
                        elif setvar == 'COM2_STBY_RADIO_SET_HZ':
                            # Convert Hz to MHz for COM2 standby
                            return {
                                'setvar': setvar,
                                'radio': '2',
                                'value': data['value'],
                                'is_standby': True
                            }
                        elif setvar == 'COM_RADIO_SWAP':
                            return {
                                'setvar': setvar,
                                'radio': '1'
                            }
                        elif setvar == 'COM2_RADIO_SWAP':
                            return {
                                'setvar': setvar,
                                'radio': '2'
                            }
                        elif setvar == 'XPNDR_SET':
                            return {
                                'setvar': setvar,
                                'value': int(data['value'])
                            }
                        elif setvar == 'AUDIO_PANEL_VOLUME_SET':
                            return {
                                'setvar': setvar,
                                'value': int(data['value'])
                            }
                        elif setvar == 'COM1_VOLUME_SET':
                            return {
                                'setvar': setvar,
                                'value': int(data['value'])
                            }
                        elif setvar == 'COM2_VOLUME_SET':
                            return {
                                'setvar': setvar,
                                'value': int(data['value'])
                            }
                    except json.JSONDecodeError:
                        continue
                        
            # Clear the output file after reading
            open(self.output_path, 'w').close()
            return None
            
        except Exception as e:
            print(f"Error reading SimAPI output: {e}")
            return None
    
    def create_simapi_data(self, 
                          aircraft_state: Dict[str, Any],
                          radio_state: Dict[str, Any],
                          transponder_state: Dict[str, Any]) -> Dict[str, Any]:
        """Create the complete SimAPI input data structure"""
        # Calculate wheel RPM based on ground state
        is_on_ground = aircraft_state['on_ground']
        wheel_rpm = 0
        if is_on_ground and aircraft_state['ground_speed'] > 0.1:
            # When on ground, wheel RPM is roughly proportional to ground speed
            # Using a factor of 10 to convert m/s to a reasonable RPM value
            wheel_rpm = int(aircraft_state['ground_speed'] * 10)

        # Calculate airspeeds
        ground_speed_kts = int(aircraft_state['ground_speed'] * 1.94384)  # Convert m/s to knots
        # Convert altitude from meters to feet
        altitude_m = float(aircraft_state['altitude'].split()[0])
        altitude_ft = int(altitude_m * 3.28084)
        
        # Calculate indicated airspeed (IAS)
        # For now, we'll use ground speed as a base, but this should be replaced with actual IAS from the simulator
        indicated_airspeed = ground_speed_kts
        
        # Calculate true airspeed (TAS) based on altitude
        # TAS = IAS * (1 + (altitude/1000) * 0.02)
        true_airspeed = int(indicated_airspeed * (1 + (altitude_ft/1000) * 0.02))

        # Get magnetic heading and variation
        magnetic_heading = int(float(aircraft_state['heading'].strip('°'))) - aircraft_state['magvar']
        magnetic_heading = magnetic_heading % 360  # Normalize to 0-360 range

        # Calculate indicated altitude based on pressure
        # Convert pressure from inHg*100 to inHg
        current_pressure = aircraft_state['sea_level_pressure'] / 100.0
        # Calculate pressure difference from standard (29.92)
        pressure_diff = 29.92 - current_pressure
        # Adjust indicated altitude (1000ft per 0.01 inHg)
        indicated_altitude = altitude_ft + int(pressure_diff * 1000)

        return {
            "sim": {
                "variables": {
                    # Aircraft state
                    "AIRSPEED INDICATED": indicated_airspeed,
                    "AIRSPEED TRUE": true_airspeed,
                    "ENGINE TYPE": aircraft_state['engine_type'],
                    "INDICATED ALTITUDE": indicated_altitude,
                    "MAGNETIC COMPASS": magnetic_heading,
                    "MAGVAR": aircraft_state['magvar'],
                    "PLANE ALT ABOVE GROUND MINUS CG": 0 if aircraft_state['on_ground'] else altitude_ft,
                    "PLANE ALTITUDE": altitude_ft,
                    "PLANE BANK DEGREES": int(aircraft_state['bank']),
                    "PLANE HEADING DEGREES TRUE": int(float(aircraft_state['heading'].strip('°'))),
                    "PLANE LATITUDE": aircraft_state['latitude'],
                    "PLANE LONGITUDE": aircraft_state['longitude'],
                    "PLANE PITCH DEGREES": int(aircraft_state['pitch']),
                    "SEA LEVEL PRESSURE": aircraft_state['sea_level_pressure'],
                    "SIM ON GROUND": 1 if aircraft_state['on_ground'] else 0,
                    "TOTAL WEIGHT": aircraft_state['total_weight'],
                    "VERTICAL SPEED": aircraft_state['vertical_speed'],
                    "WHEEL RPM:1": wheel_rpm,
                    
                    # Additional aircraft state
                    "TYPICAL DESCENT RATE": aircraft_state['typical_descent_rate'],
                    "AMBIENT WIND DIRECTION": aircraft_state['ambient_wind_direction'],
                    "AMBIENT WIND VELOCITY": aircraft_state['ambient_wind_velocity'],
                    "LOCAL TIME": aircraft_state['local_time'],
                    "ZULU TIME": aircraft_state['zulu_time'],
                    
                    # Electrical and circuit states
                    "ELECTRICAL MASTER BATTERY:0": 1 if aircraft_state['electrical_master_battery'] else 0,
                    "CIRCUIT COM ON:1": 1 if aircraft_state['circuit_com1'] else 0,
                    "CIRCUIT COM ON:2": 1 if aircraft_state['circuit_com2'] else 0,
                    
                    # Additional variables from SayIntentions.AI example
                    "TITLE": "Aerofly FS4",
                    "ATC MODEL": "ATCCOM.AC_MODEL A320.0.text",
                    "PLANE TOUCHDOWN LATITUDE": 0,
                    "PLANE TOUCHDOWN LONGITUDE": 0,
                    "PLANE TOUCHDOWN NORMAL VELOCITY": 0,
                    "INTERCOM SYSTEM ACTIVE": 0,
                    "AUDIO PANEL VOLUME": 75,
                    "COM VOLUME:1": 46,
                    "COM VOLUME:2": 81,
                    "WING SPAN": 36,
                    "ZULU DAY OF YEAR": int(datetime.now().strftime('%j')),
                    
                    # Radio state
                    **radio_state,
                    
                    # Transponder state
                    **transponder_state
                },
                "exe": "aerofly_fs_4.exe",
                "simapi_version": "1.0",
                "name": "Aerofly",
                "version": "1.0",
                "adapter_version": "1.0"
            }
        } 