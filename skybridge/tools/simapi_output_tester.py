import os
import json
import time

# List of SimAPI output variables and example values (from documentation)
OUTPUT_VARIABLES = [
    {"setvar": "AUDIO_PANEL_VOLUME_SET", "value": 50},  # 50% intercom volume
    {"setvar": "COM1_VOLUME_SET", "value": 75},        # 75% COM1 volume
    {"setvar": "COM2_RADIO_SET_HZ", "value": 123455000}, # 123.455 MHz for COM2 active
    {"setvar": "COM2_RADIO_SWAP", "value": 1},         # Swap COM2 active/standby
    {"setvar": "COM2_STBY_RADIO_SET_HZ", "value": 121800000}, # 121.800 MHz for COM2 standby
    {"setvar": "COM2_VOLUME_SET", "value": 60},        # 60% COM2 volume
    {"setvar": "COM_RADIO_SET_HZ", "value": 127950000}, # 127.950 MHz for COM1 active
    {"setvar": "COM_RADIO_SWAP", "value": 1},          # Swap COM1 active/standby
    {"setvar": "COM_STBY_RADIO_SET_HZ", "value": 118300000}, # 118.300 MHz for COM1 standby
    {"setvar": "XPNDR_SET", "value": 7700},            # Transponder code 7700
]

# Mapping from output setvar to input variable name and conversion function
OUTPUT_TO_INPUT_MAP = {
    "AUDIO_PANEL_VOLUME_SET": ("AUDIO PANEL VOLUME", int),
    "COM1_VOLUME_SET": ("COM VOLUME:1", int),
    "COM2_RADIO_SET_HZ": ("COM ACTIVE FREQUENCY:2", lambda v: int(round(float(v) * 1e6)) if float(v) < 1000 else int(v)),
    "COM2_RADIO_SWAP": (None, None),  # No direct input variable
    "COM2_STBY_RADIO_SET_HZ": ("COM STANDBY FREQUENCY:2", lambda v: int(round(float(v) * 1e6)) if float(v) < 1000 else int(v)),
    "COM2_VOLUME_SET": ("COM VOLUME:2", int),
    "COM_RADIO_SET_HZ": ("COM ACTIVE FREQUENCY:1", lambda v: int(round(float(v) * 1e6)) if float(v) < 1000 else int(v)),
    "COM_RADIO_SWAP": (None, None),  # No direct input variable
    "COM_STBY_RADIO_SET_HZ": ("COM STANDBY FREQUENCY:1", lambda v: int(round(float(v) * 1e6)) if float(v) < 1000 else int(v)),
    "XPNDR_SET": ("TRANSPONDER CODE:1", int),
}

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_PATH = os.path.join(os.path.dirname(SCRIPT_DIR), 'SayIntentionsAI')
OUTPUT_PATH = os.path.join(BASE_PATH, 'simAPI_output.jsonl')
INPUT_PATH = os.path.join(BASE_PATH, 'simAPI_input.json')

os.makedirs(BASE_PATH, exist_ok=True)

# Track failed cycles for each variable
fail_counts = {var['setvar']: 0 for var in OUTPUT_VARIABLES}

def read_input_var(input_data, var_name):
    # Try to find the variable in the input JSON structure
    try:
        return input_data['sim']['variables'][var_name]
    except Exception:
        return None

def main():
    print(f"Writing test requests to {OUTPUT_PATH} (Ctrl+C to stop)...")
    idx = 0
    current_req = None
    setvar = None
    value = None
    fail_count = 0
    while True:
        if current_req is None:
            # Write a new request
            current_req = OUTPUT_VARIABLES[idx]
            setvar = current_req['setvar']
            value = current_req['value']
            fail_count = 0
            with open(OUTPUT_PATH, 'a') as f:
                json.dump(current_req, f)
                f.write('\n')
            print(f"Wrote: {current_req}")
        # Check input file for the requested variable (if mappable)
        input_var, conv = OUTPUT_TO_INPUT_MAP.get(setvar, (None, None))
        if input_var:
            matched = False
            try:
                with open(INPUT_PATH, 'r') as fin:
                    input_data = json.load(fin)
                input_val = read_input_var(input_data, input_var)
                if input_val is not None:
                    expected_val = conv(value) if conv else value
                    if isinstance(expected_val, int) and isinstance(input_val, int):
                        if abs(input_val - expected_val) < 100:
                            matched = True
                    else:
                        if str(input_val) == str(expected_val):
                            matched = True
            except Exception as e:
                print(f"[DEBUG] Could not read input file: {e}")
            if matched:
                print(f"[OK] {setvar} matched in input.")
                fail_count = 0
                idx = (idx + 1) % len(OUTPUT_VARIABLES)
                current_req = None
                time.sleep(1)
                continue
            else:
                fail_count += 1
                if fail_count >= 2:
                    print(f"[DEBUG] Variable '{setvar}' not matched in input after 2 cycles. Last expected: {expected_val}, last input: {input_val}")
                    fail_count = 0
                    idx = (idx + 1) % len(OUTPUT_VARIABLES)
                    current_req = None
        else:
            # No input variable to check, just move to next
            idx = (idx + 1) % len(OUTPUT_VARIABLES)
            current_req = None
        time.sleep(1)

if __name__ == "__main__":
    main() 