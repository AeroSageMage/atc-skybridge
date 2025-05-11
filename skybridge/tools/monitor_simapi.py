import os
import json
import time
import threading
from datetime import datetime
import tkinter as tk
from tkinter import ttk

class SimAPIMonitor:
    def __init__(self, root):
        self.root = root
        self.root.title("SayIntentions SimAPI Monitor")
        
        # Set up file paths in local directory
        self.base_path = os.path.join(os.getcwd(), 'external_atc_layer', 'SayIntentionsAI')
        self.input_path = os.path.join(self.base_path, 'simAPI_input.json')
        self.output_path = os.path.join(self.base_path, 'simAPI_output.jsonl')
        
        # Create main frame
        self.main_frame = ttk.Frame(root, padding="10")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Create path display
        self.create_path_display()
        
        # Create input file display
        self.create_input_display()
        
        # Create output file display
        self.create_output_display()
        
        # Create control buttons
        self.create_control_buttons()
        
        # Initialize monitoring
        self.running = False
        self.update_thread = None
        
    def create_path_display(self):
        path_frame = ttk.LabelFrame(self.main_frame, text="File Paths", padding="5")
        path_frame.grid(row=0, column=0, padx=5, pady=5, sticky=(tk.W, tk.E))
        
        # Input path
        ttk.Label(path_frame, text="Input:").grid(row=0, column=0, sticky=tk.W)
        ttk.Label(path_frame, text=self.input_path).grid(row=0, column=1, sticky=tk.W)
        
        # Output path
        ttk.Label(path_frame, text="Output:").grid(row=1, column=0, sticky=tk.W)
        ttk.Label(path_frame, text=self.output_path).grid(row=1, column=1, sticky=tk.W)
        
    def create_input_display(self):
        input_frame = ttk.LabelFrame(self.main_frame, text="SimAPI Input File", padding="5")
        input_frame.grid(row=1, column=0, padx=5, pady=5, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Create text widget for input file with scrollbar
        input_container = ttk.Frame(input_frame)
        input_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.input_text = tk.Text(input_container, height=30, width=80, wrap=tk.WORD)
        input_scrollbar = ttk.Scrollbar(input_container, orient="vertical", command=self.input_text.yview)
        self.input_text.configure(yscrollcommand=input_scrollbar.set)
        
        self.input_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        input_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.input_text.config(state=tk.DISABLED)
        
    def create_output_display(self):
        output_frame = ttk.LabelFrame(self.main_frame, text="SimAPI Output File", padding="5")
        output_frame.grid(row=2, column=0, padx=5, pady=5, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Create text widget for output file with scrollbar
        output_container = ttk.Frame(output_frame)
        output_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.output_text = tk.Text(output_container, height=15, width=80, wrap=tk.WORD)
        output_scrollbar = ttk.Scrollbar(output_container, orient="vertical", command=self.output_text.yview)
        self.output_text.configure(yscrollcommand=output_scrollbar.set)
        
        self.output_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        output_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.output_text.config(state=tk.DISABLED)
        
    def create_control_buttons(self):
        control_frame = ttk.Frame(self.main_frame)
        control_frame.grid(row=3, column=0, pady=5)
        
        self.start_button = ttk.Button(control_frame, text="Start Monitoring", command=self.toggle_monitoring)
        self.start_button.pack(side=tk.LEFT, padx=5)
        
        self.clear_button = ttk.Button(control_frame, text="Clear Display", command=self.clear_display)
        self.clear_button.pack(side=tk.LEFT, padx=5)
        
        # Add create directory button
        self.create_dir_button = ttk.Button(control_frame, text="Create Directory", command=self.create_directory)
        self.create_dir_button.pack(side=tk.LEFT, padx=5)
        
    def create_directory(self):
        """Create the SayIntentions directory if it doesn't exist"""
        try:
            os.makedirs(self.base_path, exist_ok=True)
            self.update_status("Directory created successfully")
        except Exception as e:
            self.update_status(f"Error creating directory: {str(e)}")
            
    def update_status(self, message):
        """Update status message in the input display"""
        self.input_text.config(state=tk.NORMAL)
        self.input_text.delete(1.0, tk.END)
        self.input_text.insert(tk.END, f"Status: {message}\n")
        self.input_text.config(state=tk.DISABLED)
        
    def toggle_monitoring(self):
        if not self.running:
            self.start_monitoring()
        else:
            self.stop_monitoring()
            
    def start_monitoring(self):
        self.running = True
        self.start_button.config(text="Stop Monitoring")
        
        # Start update thread
        self.update_thread = threading.Thread(target=self.update_loop)
        self.update_thread.daemon = True
        self.update_thread.start()
        
    def stop_monitoring(self):
        self.running = False
        self.start_button.config(text="Start Monitoring")
        
    def clear_display(self):
        self.input_text.config(state=tk.NORMAL)
        self.input_text.delete(1.0, tk.END)
        self.input_text.config(state=tk.DISABLED)
        
        self.output_text.config(state=tk.NORMAL)
        self.output_text.delete(1.0, tk.END)
        self.output_text.config(state=tk.DISABLED)
        
    def update_loop(self):
        last_input_mtime = 0
        last_output_mtime = 0
        
        while self.running:
            try:
                # Check input file
                if os.path.exists(self.input_path):
                    current_mtime = os.path.getmtime(self.input_path)
                    if current_mtime > last_input_mtime:
                        last_input_mtime = current_mtime
                        with open(self.input_path, 'r') as f:
                            try:
                                data = json.load(f)
                                self.update_input_display(data)
                            except json.JSONDecodeError as e:
                                self.update_input_display({"error": f"Invalid JSON: {str(e)}"})
                
                # Check output file
                if os.path.exists(self.output_path):
                    current_mtime = os.path.getmtime(self.output_path)
                    if current_mtime > last_output_mtime:
                        last_output_mtime = current_mtime
                        with open(self.output_path, 'r') as f:
                            try:
                                lines = f.readlines()
                                if lines:
                                    self.update_output_display(lines)
                            except Exception as e:
                                self.update_output_display([f"Error reading output file: {str(e)}"])
                
                time.sleep(0.5)  # Check every 500ms
                
            except Exception as e:
                print(f"Error in update loop: {e}")
                time.sleep(1)
                
    def update_input_display(self, data):
        self.input_text.config(state=tk.NORMAL)
        self.input_text.delete(1.0, tk.END)
        self.input_text.insert(tk.END, f"Last Update: {datetime.now().strftime('%H:%M:%S')}\n\n")
        self.input_text.insert(tk.END, json.dumps(data, indent=2))
        self.input_text.config(state=tk.DISABLED)
        
    def update_output_display(self, lines):
        self.output_text.config(state=tk.NORMAL)
        self.output_text.delete(1.0, tk.END)
        self.output_text.insert(tk.END, f"Last Update: {datetime.now().strftime('%H:%M:%S')}\n\n")
        for line in lines:
            try:
                data = json.loads(line.strip())
                self.output_text.insert(tk.END, json.dumps(data, indent=2) + "\n")
            except json.JSONDecodeError:
                self.output_text.insert(tk.END, f"Invalid JSON: {line}\n")
        self.output_text.config(state=tk.DISABLED)

if __name__ == "__main__":
    root = tk.Tk()
    app = SimAPIMonitor(root)
    root.mainloop() 