# SkyBridge

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

SkyBridge is a powerful bridge between flight simulators and SayIntentions.AI, providing real-time aircraft state management and radio/transponder control. It enables seamless integration between your flight simulator and SayIntentions.AI's advanced ATC capabilities.

## 🌟 Features

- **Real-time Aircraft State Monitoring**
  - Position tracking (latitude, longitude, altitude)
  - Speed and heading information
  - Aircraft configuration status
  - Engine and system monitoring

- **Radio Management**
  - COM1/COM2 frequency control
  - Active/Standby frequency switching
  - Radio state monitoring
  - Frequency validation

- **Transponder Control**
  - Mode C/S support
  - Squawk code management
  - Transponder state monitoring

- **SayIntentions.AI Integration**
  - Automatic state synchronization
  - Command processing
  - Real-time feedback
  - Error handling and recovery

- **Modern GUI Interface**
  - Clean, intuitive design
  - Real-time status updates
  - Visual feedback for changes
  - Easy configuration

## 📋 Requirements

- Python 3.8 or higher
- tkinter (usually comes with Python)
- Flight simulator with UDP output capability
- SayIntentions.AI account

## 🚀 Installation

1. Clone the repository:
```bash
git clone https://github.com/AeroSageMage/atc-skybridge.git
cd atc-skybridge
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Install the package (optional):
```bash
pip install -e .
```

## 💻 Usage

1. Start your flight simulator
2. Configure your simulator's UDP output:
   - Port: 49002
   - Format: JSON
   - Update Rate: 20Hz

3. Run SkyBridge:
```bash
python -m skybridge.main
```

4. Use the GUI to monitor and control your aircraft's systems

## 🔧 Configuration

### Simulator UDP Settings

- **Port**: 49002
- **Format**: JSON
- **Update Rate**: 20Hz

### SayIntentions.AI Integration

SkyBridge automatically creates and manages the necessary files for SayIntentions.AI integration:
- `simAPI_input.json`: Contains current aircraft state
- `simAPI_output.jsonl`: Receives commands from SayIntentions.AI

## 🏗️ Project Structure

```
skybridge/
├── core/           # Core functionality
│   ├── aircraft_state.py
│   ├── radio_manager.py
│   └── transponder_manager.py
├── data/           # Data handling
│   └── simapi_handler.py
├── gui/            # User interface
│   └── radio_display.py
├── tools/          # Utility tools
│   └── udp_receiver.py
└── main.py         # Application entry point
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- SayIntentions.AI for their innovative ATC solution
- The flight simulation community for their support and feedback
- All contributors who help improve this project 