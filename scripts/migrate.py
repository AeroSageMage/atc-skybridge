#!/usr/bin/env python3
import os
import shutil
from pathlib import Path

def copy_and_adapt_file(src_path, dst_path, replacements=None):
    """Copy a file and adapt its contents with replacements"""
    if not os.path.exists(src_path):
        print(f"Source file not found: {src_path}")
        return False
    
    # Create destination directory if it doesn't exist
    os.makedirs(os.path.dirname(dst_path), exist_ok=True)
    
    # Read source file
    with open(src_path, 'r') as f:
        content = f.read()
    
    # Apply replacements
    if replacements:
        for old, new in replacements.items():
            content = content.replace(old, new)
    
    # Write to destination
    with open(dst_path, 'w') as f:
        f.write(content)
    
    print(f"Copied and adapted: {dst_path}")
    return True

def main():
    # Define source and destination paths
    src_base = Path("../external_atc_layer")
    dst_base = Path("skybridge")
    
    # Define file mappings with replacements
    file_mappings = {
        # Core files
        "core/aircraft_state.py": {
            "from external_atc_layer": "from skybridge",
            "external_atc_layer": "skybridge"
        },
        "core/radio_manager.py": {
            "from external_atc_layer": "from skybridge",
            "external_atc_layer": "skybridge"
        },
        "core/transponder_manager.py": {
            "from external_atc_layer": "from skybridge",
            "external_atc_layer": "skybridge"
        },
        
        # Data files
        "data/simapi_handler.py": {
            "from external_atc_layer": "from skybridge",
            "external_atc_layer": "skybridge"
        },
        
        # GUI files
        "gui/radio_display.py": {
            "from external_atc_layer": "from skybridge",
            "from tools.rewinger": "from skybridge.tools.udp_receiver",
            "external_atc_layer": "skybridge"
        }
    }
    
    # Copy and adapt files
    for src_rel, replacements in file_mappings.items():
        src_path = src_base / src_rel
        dst_path = dst_base / src_rel
        copy_and_adapt_file(src_path, dst_path, replacements)

if __name__ == "__main__":
    main() 