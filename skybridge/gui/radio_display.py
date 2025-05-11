import tkinter as tk
from tkinter import ttk
import threading
import time
import os

from skybridge.core.aircraft_state import AircraftStateManager
from skybridge.core.radio_manager import RadioManager
from skybridge.core.transponder_manager import TransponderManager
from skybridge.data.simapi_handler import SimAPIHandler
from skybridge.tools.udp_receiver import UDPReceiver

class RadioDisplay:
    def __init__(self, root):
        self.root = root
        self.root.title("Radio Display")
        
        # Initialize managers
        self.aircraft_state = AircraftStateManager()
        self.radio_manager = RadioManager()
        self.transponder_manager = TransponderManager()
        
        # Initialize SimAPI handler
        self.simapi_handler = SimAPIHandler(
            os.path.join(os.getcwd(), 'SayIntentionsAI')
        )
        
        # Initialize UDP receiver
        self.sim_udp_receiver = UDPReceiver()
        self.sim_udp_receiver.start_receiving()
        
        # SimAPI update thread
        self.running = False
        self.update_thread = None
        
        # Continuous adjustment variables
        self.adjustment_running = False
        self.adjustment_after_id = None
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(expand=True, fill='both', padx=5, pady=5)
        
        # Create main frame for radio display
        self.main_frame = ttk.Frame(self.notebook, padding="10")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Create aircraft config frame
        self.config_frame = ttk.Frame(self.notebook, padding="10")
        self.config_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Add frames to notebook
        self.notebook.add(self.main_frame, text="Radio Display")
        self.notebook.add(self.config_frame, text="Aircraft Config")
        
        # Create radio and transponder section
        self.create_radio_transponder_section()
        
        # Create aircraft info section
        self.create_aircraft_info_section()
        
        # Create control buttons
        self.create_control_buttons()
        
        # Create aircraft configuration section
        self.create_aircraft_config_section()
        
        # Configure grid weights
        self.main_frame.columnconfigure(0, weight=1)
        self.main_frame.columnconfigure(1, weight=1)
        self.main_frame.columnconfigure(2, weight=1)
        self.config_frame.columnconfigure(0, weight=1)
        self.config_frame.columnconfigure(1, weight=1)
    
    def create_radio_transponder_section(self):
        """Create an integrated radio and transponder section"""
        # Main container frame
        radio_frame = ttk.LabelFrame(self.main_frame, text="Radio", padding="5")
        radio_frame.grid(row=0, column=0, columnspan=2, padx=5, pady=5, sticky=(tk.W, tk.E))
        
        # COM1 Section
        com1_frame = ttk.LabelFrame(radio_frame, text="COM 1", padding="5")
        com1_frame.grid(row=0, column=0, padx=5, pady=5, sticky=(tk.W, tk.E))
        
        # COM1 Active
        active_frame1 = ttk.Frame(com1_frame)
        active_frame1.grid(row=0, column=0, padx=5, pady=2)
        ttk.Label(active_frame1, text="ACTIVE").grid(row=0, column=0)
        self.active_label1 = ttk.Label(active_frame1, text=f"{self.radio_manager.active_freq_1:.3f}", font=('Arial', 12))
        self.active_label1.grid(row=1, column=0)
        
        # COM1 Standby
        standby_frame1 = ttk.Frame(com1_frame)
        standby_frame1.grid(row=1, column=0, padx=5, pady=2)
        ttk.Label(standby_frame1, text="STBY").grid(row=0, column=0)
        self.standby_label1 = ttk.Label(standby_frame1, text=f"{self.radio_manager.standby_freq_1:.3f}", font=('Arial', 12))
        self.standby_label1.grid(row=1, column=0)
        
        # COM1 Controls
        controls1 = ttk.Frame(com1_frame)
        controls1.grid(row=0, column=1, rowspan=2, padx=5)
        # Coarse controls
        coarse_frame1 = ttk.Frame(controls1)
        coarse_frame1.grid(row=0, column=0, padx=2)
        ttk.Label(coarse_frame1, text="Coarse").grid(row=0, column=0, columnspan=2)
        up_coarse1 = ttk.Button(coarse_frame1, text="↑", command=lambda: self.adjust_frequency(1, 'coarse', 1))
        up_coarse1.grid(row=1, column=0)
        down_coarse1 = ttk.Button(coarse_frame1, text="↓", command=lambda: self.adjust_frequency(1, 'coarse', -1))
        down_coarse1.grid(row=2, column=0)
        # Fine controls
        fine_frame1 = ttk.Frame(controls1)
        fine_frame1.grid(row=0, column=1, padx=2)
        ttk.Label(fine_frame1, text="Fine").grid(row=0, column=0, columnspan=2)
        up_fine1 = ttk.Button(fine_frame1, text="↑")
        up_fine1.grid(row=1, column=0)
        down_fine1 = ttk.Button(fine_frame1, text="↓")
        down_fine1.grid(row=2, column=0)
        # Bind mouse events for continuous adjustment
        up_fine1.bind('<ButtonPress-1>', lambda e: self.start_continuous_adjustment(1, 'fine', 1))
        up_fine1.bind('<ButtonRelease-1>', lambda e: self.stop_continuous_adjustment())
        down_fine1.bind('<ButtonPress-1>', lambda e: self.start_continuous_adjustment(1, 'fine', -1))
        down_fine1.bind('<ButtonRelease-1>', lambda e: self.stop_continuous_adjustment())
        # Swap button
        ttk.Button(controls1, text="SWAP", command=lambda: self.swap_frequencies(1)).grid(row=1, column=0, columnspan=2, pady=5)
        
        # COM2 Section
        com2_frame = ttk.LabelFrame(radio_frame, text="COM 2", padding="5")
        com2_frame.grid(row=0, column=1, padx=5, pady=5, sticky=(tk.W, tk.E))
        
        # COM2 Active
        active_frame2 = ttk.Frame(com2_frame)
        active_frame2.grid(row=0, column=0, padx=5, pady=2)
        ttk.Label(active_frame2, text="ACTIVE").grid(row=0, column=0)
        self.active_label2 = ttk.Label(active_frame2, text=f"{self.radio_manager.active_freq_2:.3f}", font=('Arial', 12))
        self.active_label2.grid(row=1, column=0)
        
        # COM2 Standby
        standby_frame2 = ttk.Frame(com2_frame)
        standby_frame2.grid(row=1, column=0, padx=5, pady=2)
        ttk.Label(standby_frame2, text="STBY").grid(row=0, column=0)
        self.standby_label2 = ttk.Label(standby_frame2, text=f"{self.radio_manager.standby_freq_2:.3f}", font=('Arial', 12))
        self.standby_label2.grid(row=1, column=0)
        
        # COM2 Controls
        controls2 = ttk.Frame(com2_frame)
        controls2.grid(row=0, column=1, rowspan=2, padx=5)
        # Coarse controls
        coarse_frame2 = ttk.Frame(controls2)
        coarse_frame2.grid(row=0, column=0, padx=2)
        ttk.Label(coarse_frame2, text="Coarse").grid(row=0, column=0, columnspan=2)
        up_coarse2 = ttk.Button(coarse_frame2, text="↑", command=lambda: self.adjust_frequency(2, 'coarse', 1))
        up_coarse2.grid(row=1, column=0)
        down_coarse2 = ttk.Button(coarse_frame2, text="↓", command=lambda: self.adjust_frequency(2, 'coarse', -1))
        down_coarse2.grid(row=2, column=0)
        # Fine controls
        fine_frame2 = ttk.Frame(controls2)
        fine_frame2.grid(row=0, column=1, padx=2)
        ttk.Label(fine_frame2, text="Fine").grid(row=0, column=0, columnspan=2)
        up_fine2 = ttk.Button(fine_frame2, text="↑")
        up_fine2.grid(row=1, column=0)
        down_fine2 = ttk.Button(fine_frame2, text="↓")
        down_fine2.grid(row=2, column=0)
        # Bind mouse events for continuous adjustment
        up_fine2.bind('<ButtonPress-1>', lambda e: self.start_continuous_adjustment(2, 'fine', 1))
        up_fine2.bind('<ButtonRelease-1>', lambda e: self.stop_continuous_adjustment())
        down_fine2.bind('<ButtonPress-1>', lambda e: self.start_continuous_adjustment(2, 'fine', -1))
        down_fine2.bind('<ButtonRelease-1>', lambda e: self.stop_continuous_adjustment())
        # Swap button
        ttk.Button(controls2, text="SWAP", command=lambda: self.swap_frequencies(2)).grid(row=1, column=0, columnspan=2, pady=5)
    
    def create_aircraft_info_section(self):
        """Create the aircraft information section"""
        # Aircraft Info Frame
        aircraft_frame = ttk.LabelFrame(self.main_frame, text="Aircraft Information", padding="5")
        aircraft_frame.grid(row=1, column=0, padx=5, pady=5, sticky=(tk.W, tk.E))
        
        # Create labels and entry fields for each aircraft info
        self.aircraft_labels = {}
        self.aircraft_entries = {}
        
        # First row: editable fields (callsign and type)
        row = 0
        for field in ['callsign', 'type']:
            ttk.Label(aircraft_frame, text=f"{field.title()}:").grid(row=row, column=0, padx=5, pady=2, sticky=tk.W)
            self.aircraft_entries[field] = ttk.Entry(aircraft_frame, width=20)
            self.aircraft_entries[field].grid(row=row, column=1, padx=5, pady=2, sticky=tk.W)
            self.aircraft_entries[field].insert(0, getattr(self.aircraft_state.state, field))
            row += 1
            
        # Add a separator
        ttk.Separator(aircraft_frame, orient='horizontal').grid(row=row, column=0, columnspan=2, sticky='ew', pady=5)
        row += 1
        
        # Second row: read-only fields (position, altitude, heading)
        for field in ['position', 'altitude', 'heading']:
            ttk.Label(aircraft_frame, text=f"{field.title()}:").grid(row=row, column=0, padx=5, pady=2, sticky=tk.W)
            self.aircraft_entries[field] = ttk.Entry(aircraft_frame, width=20, state='readonly')
            self.aircraft_entries[field].grid(row=row, column=1, padx=5, pady=2, sticky=tk.W)
            self.aircraft_entries[field].insert(0, getattr(self.aircraft_state.state, field))
            row += 1
            
        # Transponder Section
        xpdr_frame = ttk.LabelFrame(self.main_frame, text="Transponder", padding="5")
        xpdr_frame.grid(row=1, column=1, padx=5, pady=5, sticky=(tk.W, tk.E))
        
        # Transponder Code
        code_frame = ttk.Frame(xpdr_frame)
        code_frame.grid(row=0, column=0, padx=5, pady=2)
        ttk.Label(code_frame, text="CODE").grid(row=0, column=0)
        self.transponder_label = ttk.Label(code_frame, text=f"{self.transponder_manager.code:04d}", font=('Arial', 12))
        self.transponder_label.grid(row=1, column=0)
        
        # Transponder Controls
        xpdr_controls = ttk.Frame(xpdr_frame)
        xpdr_controls.grid(row=0, column=1, padx=5)
        
        # Create numpad
        numpad_frame = ttk.Frame(xpdr_controls)
        numpad_frame.grid(row=0, column=0, padx=2)
        
        # Create buttons for digits 0-7 (max value for each digit in squawk code)
        for i in range(8):
            row = i // 4
            col = i % 4
            ttk.Button(numpad_frame, text=str(i), 
                      command=lambda x=i: self.set_transponder_digit(x)).grid(row=row, column=col, padx=1, pady=1)
        
        # Transponder Mode
        mode_frame = ttk.Frame(xpdr_frame)
        mode_frame.grid(row=1, column=0, columnspan=2, padx=5, pady=2)
        self.mode_var = tk.StringVar(value="3")
        modes = [("OFF", "0"), ("STBY", "1"), ("ON", "3"), ("ALT", "4"), ("GND", "5")]
        for i, (text, value) in enumerate(modes):
            ttk.Radiobutton(mode_frame, text=text, value=value, 
                           variable=self.mode_var, 
                           command=self.update_transponder_mode).grid(row=0, column=i, padx=2)
        
        # IDENT Button
        self.ident_button = ttk.Button(xpdr_frame, text="IDENT", 
                                     command=self.toggle_ident,
                                     state='normal' if self.transponder_manager.mode == 3 else 'disabled')
        self.ident_button.grid(row=2, column=0, columnspan=2, pady=5)
    
    def create_control_buttons(self):
        """Create control buttons for starting/stopping data reception"""
        control_frame = ttk.Frame(self.main_frame)
        control_frame.grid(row=2, column=0, columnspan=3, pady=5)
        
        self.start_button = ttk.Button(control_frame, text="Start SimAPI", command=self.toggle_reception)
        self.start_button.pack(side=tk.LEFT, padx=5)
        
        # Add SimAPI changes section
        self.create_simapi_changes_section()
    
    def create_simapi_changes_section(self):
        """Create a section to display pending SimAPI changes"""
        changes_frame = ttk.LabelFrame(self.main_frame, text="Pending Changes", padding="5")
        changes_frame.grid(row=3, column=0, columnspan=3, padx=5, pady=5, sticky=(tk.W, tk.E))
        
        # Create a text widget for displaying changes
        self.changes_text = tk.Text(changes_frame, height=4, width=50, wrap=tk.WORD)
        self.changes_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.changes_text.config(state='disabled')  # Make it read-only
        
        # Add a scrollbar
        scrollbar = ttk.Scrollbar(changes_frame, orient="vertical", command=self.changes_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.changes_text.configure(yscrollcommand=scrollbar.set)
        
        # Initialize changes list
        self.pending_changes = []
    
    def adjust_frequency(self, radio_num: int, adjustment_type: str, direction: int):
        """Adjust the frequency for the specified radio"""
        new_freq = self.radio_manager.adjust_frequency(radio_num, adjustment_type, direction)
        if radio_num == 1:
            self.standby_label1.config(text=f"{new_freq:.3f}")
        else:
            self.standby_label2.config(text=f"{new_freq:.3f}")
    
    def swap_frequencies(self, radio_num: int):
        """Swap active and standby frequencies for the specified radio"""
        active, standby = self.radio_manager.swap_frequencies(radio_num)
        if radio_num == 1:
            self.active_label1.config(text=f"{active:.3f}")
            self.standby_label1.config(text=f"{standby:.3f}")
        else:
            self.active_label2.config(text=f"{active:.3f}")
            self.standby_label2.config(text=f"{standby:.3f}")
    
    def adjust_transponder(self, direction: int):
        """Adjust the transponder code"""
        new_code = self.transponder_manager.adjust_code(direction)
        self.transponder_label.config(text=f"{new_code:04d}")
    
    def update_transponder_mode(self):
        """Update the transponder mode based on radio button selection"""
        mode = int(self.mode_var.get())
        self.transponder_manager.set_mode(mode)
        self.ident_button.config(state='normal' if mode == 3 else 'disabled')
    
    def toggle_ident(self):
        """Toggle the IDENT state"""
        ident = self.transponder_manager.toggle_ident()
        if ident:
            self.root.after(18000, lambda: self.transponder_manager.toggle_ident())
    
    def toggle_reception(self):
        """Toggle the reception of SimAPI data"""
        if not self.running:
            self.start_reception()
        else:
            self.stop_reception()
    
    def start_reception(self):
        """Start receiving simulator data and SimAPI integration"""
        self.running = True
        self.start_button.config(text="Stop SimAPI")
        
        # Start update thread
        self.update_thread = threading.Thread(target=self.update_simapi_loop)
        self.update_thread.daemon = True
        self.update_thread.start()
    
    def stop_reception(self):
        """Stop receiving simulator data and SimAPI integration"""
        self.running = False
        self.start_button.config(text="Start SimAPI")
    
    def update_simapi_loop(self):
        """Update SimAPI data and handle output requests"""
        while self.running:
            try:
                # Get latest simulator data
                data = self.sim_udp_receiver.get_latest_data()
                if data and data.get('gps'):
                    # Update aircraft state
                    self.aircraft_state.update_from_gps(data['gps'], data.get('attitude'))
                    
                    # Update aircraft info display
                    state = self.aircraft_state.get_state()
                    for field in ['position', 'altitude', 'heading']:
                        self.aircraft_entries[field].config(state='normal')
                        self.aircraft_entries[field].delete(0, tk.END)
                        self.aircraft_entries[field].insert(0, getattr(state, field))
                        self.aircraft_entries[field].config(state='readonly')
                
                # Always update SimAPI data, regardless of GPS data
                state = self.aircraft_state.get_state()
                simapi_data = self.simapi_handler.create_simapi_data(
                    state.__dict__,
                    self.radio_manager.get_radio_state(),
                    self.transponder_manager.get_transponder_state()
                )
                self.simapi_handler.write_input_data(simapi_data)
                
                # Check for SimAPI output requests
                output_data = self.simapi_handler.read_output_data()
                if output_data:
                    self.handle_simapi_output(output_data)
                
                time.sleep(0.75)  # Update every 750ms as per SimAPI docs
                
            except Exception as e:
                print(f"Error in SimAPI update loop: {e}")
                time.sleep(1)  # Wait a bit longer on error
    
    def handle_simapi_output(self, output_data: dict):
        """Handle SimAPI output data and update the display accordingly"""
        setvar = output_data.get('setvar')
        
        if setvar in ['COM_RADIO_SET_HZ', 'COM2_RADIO_SET_HZ']:
            # Convert Hz to MHz
            new_freq = float(output_data['value']) / 1000000
            radio_num = int(output_data['radio'])
            
            # Add to pending changes
            change = {
                'type': 'radio',
                'radio': radio_num,
                'value': new_freq,
                'description': f"Set COM{radio_num} active frequency to {new_freq:.3f} MHz"
            }
            self.add_pending_change(change)
            
            # Update radio display
            self.radio_manager.set_active_frequency(radio_num, new_freq)
            if radio_num == 1:
                self.active_label1.config(text=f"{new_freq:.3f}")
            else:
                self.active_label2.config(text=f"{new_freq:.3f}")
        
        elif setvar in ['COM_STBY_RADIO_SET_HZ', 'COM2_STBY_RADIO_SET_HZ']:
            # Convert Hz to MHz
            new_freq = float(output_data['value']) / 1000000
            radio_num = int(output_data['radio'])
            
            # Add to pending changes
            change = {
                'type': 'radio',
                'radio': radio_num,
                'value': new_freq,
                'description': f"Set COM{radio_num} standby frequency to {new_freq:.3f} MHz"
            }
            self.add_pending_change(change)
            
            # Update radio display
            if radio_num == 1:
                self.radio_manager.standby_freq_1 = new_freq
                self.standby_label1.config(text=f"{new_freq:.3f}")
            else:
                self.radio_manager.standby_freq_2 = new_freq
                self.standby_label2.config(text=f"{new_freq:.3f}")
        
        elif setvar in ['COM_RADIO_SWAP', 'COM2_RADIO_SWAP']:
            radio_num = int(output_data['radio'])
            
            # Add to pending changes
            change = {
                'type': 'radio_swap',
                'radio': radio_num,
                'description': f"Swap COM{radio_num} active and standby frequencies"
            }
            self.add_pending_change(change)
            
            # Swap frequencies
            self.swap_frequencies(radio_num)
        
        elif setvar == 'XPNDR_SET':
            new_code = int(output_data['value'])
            change = {
                'type': 'transponder',
                'value': new_code,
                'description': f"Set transponder code to {new_code:04d}"
            }
            self.add_pending_change(change)
            
            # Update transponder display
            self.transponder_manager.code = new_code
            self.transponder_label.config(text=f"{new_code:04d}")
        
        elif setvar == 'AUDIO_PANEL_VOLUME_SET':
            volume = int(output_data['value'])
            change = {
                'type': 'volume',
                'value': volume,
                'description': f"Set intercom volume to {volume}%"
            }
            self.add_pending_change(change)
            
            # Update volume (if we had a volume control in the UI)
            # self.update_volume('intercom', volume)
        
        elif setvar == 'COM1_VOLUME_SET':
            volume = int(output_data['value'])
            change = {
                'type': 'volume',
                'value': volume,
                'description': f"Set COM1 volume to {volume}%"
            }
            self.add_pending_change(change)
            
            # Update volume (if we had a volume control in the UI)
            # self.update_volume('com1', volume)
        
        elif setvar == 'COM2_VOLUME_SET':
            volume = int(output_data['value'])
            change = {
                'type': 'volume',
                'value': volume,
                'description': f"Set COM2 volume to {volume}%"
            }
            self.add_pending_change(change)
            
            # Update volume (if we had a volume control in the UI)
            # self.update_volume('com2', volume)
    
    def add_pending_change(self, change: dict):
        """Add a pending change to the display"""
        self.pending_changes.append(change)
        self.update_changes_display()
    
    def update_changes_display(self):
        """Update the changes display with current pending changes"""
        self.changes_text.config(state='normal')
        self.changes_text.delete(1.0, tk.END)
        
        if not self.pending_changes:
            self.changes_text.insert(tk.END, "No pending changes")
        else:
            for change in self.pending_changes[-3:]:  # Show last 3 changes
                self.changes_text.insert(tk.END, f"• {change['description']}\n")
        
        self.changes_text.config(state='disabled')
    
    def start_continuous_adjustment(self, radio_num: int, adjustment_type: str, direction: int):
        """Start continuous frequency adjustment"""
        self.adjustment_running = True
        self._do_continuous_adjustment(radio_num, adjustment_type, direction)
    
    def stop_continuous_adjustment(self):
        """Stop continuous frequency adjustment"""
        self.adjustment_running = False
        if self.adjustment_after_id:
            self.root.after_cancel(self.adjustment_after_id)
            self.adjustment_after_id = None
    
    def _do_continuous_adjustment(self, radio_num: int, adjustment_type: str, direction: int):
        """Perform continuous frequency adjustment"""
        if self.adjustment_running:
            self.adjust_frequency(radio_num, adjustment_type, direction)
            # Schedule next adjustment with increasing delay for smoother control
            delay = 250 if adjustment_type == 'coarse' else 190  # Faster for fine adjustment
            self.adjustment_after_id = self.root.after(delay, 
                lambda: self._do_continuous_adjustment(radio_num, adjustment_type, direction))

    def set_transponder_digit(self, digit: int):
        """Set a digit in the transponder code"""
        current_code = self.transponder_manager.code
        # Shift current code left by one digit and add new digit
        new_code = ((current_code * 10) + digit) % 10000
        self.transponder_manager.code = new_code
        self.transponder_label.config(text=f"{new_code:04d}")
        
        # Update SimAPI data immediately
        state = self.aircraft_state.get_state()
        simapi_data = self.simapi_handler.create_simapi_data(
            state.__dict__,
            self.radio_manager.get_radio_state(),
            self.transponder_manager.get_transponder_state()
        )
        self.simapi_handler.write_input_data(simapi_data)

    def create_aircraft_config_section(self):
        """Create the aircraft configuration section"""
        # Create main container
        config_container = ttk.LabelFrame(self.config_frame, text="Aircraft Configuration", padding="5")
        config_container.grid(row=0, column=0, columnspan=2, padx=5, pady=5, sticky=(tk.W, tk.E))
        
        # Engine Type
        engine_frame = ttk.Frame(config_container)
        engine_frame.grid(row=0, column=0, padx=5, pady=2, sticky=tk.W)
        ttk.Label(engine_frame, text="Engine Type:").grid(row=0, column=0, sticky=tk.W)
        self.engine_type_var = tk.StringVar(value="1")
        engine_types = [
            ("Piston", "0"),
            ("Jet", "1"),
            ("None", "2"),
            ("Helicopter", "3"),
            ("Unsupported", "4"),
            ("Turboprop", "5")
        ]
        for i, (text, value) in enumerate(engine_types):
            ttk.Radiobutton(engine_frame, text=text, value=value,
                           variable=self.engine_type_var,
                           command=self.update_engine_type).grid(row=0, column=i+1, padx=2)
        
        # Aircraft Weight
        weight_frame = ttk.Frame(config_container)
        weight_frame.grid(row=1, column=0, padx=5, pady=2, sticky=tk.W)
        ttk.Label(weight_frame, text="Total Weight (lbs):").grid(row=0, column=0, sticky=tk.W)
        self.weight_var = tk.StringVar(value="150000")
        weight_entry = ttk.Entry(weight_frame, textvariable=self.weight_var, width=10)
        weight_entry.grid(row=0, column=1, padx=5)
        ttk.Button(weight_frame, text="Update",
                  command=self.update_weight).grid(row=0, column=2, padx=5)
        
        # Sea Level Pressure
        pressure_frame = ttk.Frame(config_container)
        pressure_frame.grid(row=2, column=0, padx=5, pady=2, sticky=tk.W)
        ttk.Label(pressure_frame, text="Sea Level Pressure (inHg):").grid(row=0, column=0, sticky=tk.W)
        self.pressure_var = tk.StringVar(value="29.92")
        pressure_entry = ttk.Entry(pressure_frame, textvariable=self.pressure_var, width=10)
        pressure_entry.grid(row=0, column=1, padx=5)
        ttk.Button(pressure_frame, text="Update",
                  command=self.update_pressure).grid(row=0, column=2, padx=5)
        
        # Typical Descent Rate
        descent_frame = ttk.Frame(config_container)
        descent_frame.grid(row=3, column=0, padx=5, pady=2, sticky=tk.W)
        ttk.Label(descent_frame, text="Typical Descent Rate (fpm):").grid(row=0, column=0, sticky=tk.W)
        self.descent_var = tk.StringVar(value="1000")
        descent_entry = ttk.Entry(descent_frame, textvariable=self.descent_var, width=10)
        descent_entry.grid(row=0, column=1, padx=5)
        ttk.Button(descent_frame, text="Update",
                  command=self.update_descent_rate).grid(row=0, column=2, padx=5)
        
        # Electrical System
        electrical_frame = ttk.LabelFrame(config_container, text="Electrical System", padding="5")
        electrical_frame.grid(row=4, column=0, padx=5, pady=5, sticky=(tk.W, tk.E))
        
        # Master Battery
        self.master_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(electrical_frame, text="Master Battery",
                       variable=self.master_var,
                       command=self.update_electrical).grid(row=0, column=0, padx=5)
        
        # COM1 Circuit
        self.com1_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(electrical_frame, text="COM1 Circuit",
                       variable=self.com1_var,
                       command=self.update_electrical).grid(row=0, column=1, padx=5)
        
        # COM2 Circuit
        self.com2_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(electrical_frame, text="COM2 Circuit",
                       variable=self.com2_var,
                       command=self.update_electrical).grid(row=0, column=2, padx=5)
        
        # Wind Data
        wind_frame = ttk.LabelFrame(config_container, text="Wind Data", padding="5")
        wind_frame.grid(row=5, column=0, padx=5, pady=5, sticky=(tk.W, tk.E))
        
        # Wind Direction
        ttk.Label(wind_frame, text="Direction (degrees):").grid(row=0, column=0, padx=5)
        self.wind_dir_var = tk.StringVar(value="0")
        ttk.Entry(wind_frame, textvariable=self.wind_dir_var, width=8).grid(row=0, column=1, padx=5)
        
        # Wind Velocity
        ttk.Label(wind_frame, text="Velocity (kts):").grid(row=0, column=2, padx=5)
        self.wind_vel_var = tk.StringVar(value="0")
        ttk.Entry(wind_frame, textvariable=self.wind_vel_var, width=8).grid(row=0, column=3, padx=5)
        
        # Update Wind Button
        ttk.Button(wind_frame, text="Update Wind",
                  command=self.update_wind).grid(row=0, column=4, padx=5)

    def update_engine_type(self):
        """Update engine type"""
        try:
            engine_type = int(self.engine_type_var.get())
            self.aircraft_state.set_engine_type(engine_type)
        except ValueError:
            pass

    def update_weight(self):
        """Update aircraft weight"""
        try:
            weight = int(self.weight_var.get())
            self.aircraft_state.set_total_weight(weight)
        except ValueError:
            pass

    def update_pressure(self):
        """Update sea level pressure"""
        try:
            pressure = float(self.pressure_var.get())
            # Convert from inHg to inHg*100 (e.g., 29.92 -> 2992)
            pressure_int = int(pressure * 100)
            self.aircraft_state.set_sea_level_pressure(pressure_int)
        except ValueError:
            pass

    def update_descent_rate(self):
        """Update typical descent rate"""
        try:
            rate = int(self.descent_var.get())
            self.aircraft_state.set_typical_descent_rate(rate)
        except ValueError:
            pass

    def update_electrical(self):
        """Update electrical system state"""
        self.aircraft_state.set_electrical_state(
            self.master_var.get(),
            self.com1_var.get(),
            self.com2_var.get()
        )

    def update_wind(self):
        """Update wind data"""
        try:
            direction = int(self.wind_dir_var.get())
            velocity = int(self.wind_vel_var.get())
            self.aircraft_state.set_wind_data(direction, velocity)
        except ValueError:
            pass

if __name__ == "__main__":
    root = tk.Tk()
    app = RadioDisplay(root)
    root.mainloop() 