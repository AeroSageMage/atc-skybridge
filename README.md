# SkyBridge

SkyBridge is a bridge between flight simulators and SayIntentions.AI, providing real-time aircraft state management and radio/transponder control.

## Features

- Real-time aircraft state monitoring
- Radio frequency management (COM1/COM2)
- Transponder control
- SayIntentions.AI integration
- Modern GUI interface

## Requirements

- Python 3.8+
- tkinter
- Flight simulator with UDP output capability

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/SkyBridge.git
cd SkyBridge
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

1. Start your flight simulator
2. Run SkyBridge:
```bash
python -m skybridge.main
```

3. Configure your simulator's UDP output to match SkyBridge's settings
4. Use the GUI to monitor and control your aircraft's systems

## Configuration

### Simulator UDP Settings

- Port: 49002
- Format: JSON
- Update Rate: 20Hz

### SayIntentions.AI Integration

SkyBridge automatically creates and manages the necessary files for SayIntentions.AI integration:
- `simAPI_input.json`: Contains current aircraft state
- `simAPI_output.jsonl`: Receives commands from SayIntentions.AI

## Development

### Project Structure

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

### Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

MIT License - see LICENSE file for details 