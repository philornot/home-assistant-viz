# Home Assistant Automation Visualizer

Visualize your Home Assistant automations as interactive, responsive HTML diagrams.

## Features

- Real-time automation workflow visualization
- Responsive HTML/CSS layout - works on any screen size
- Each automation displayed as a separate, interactive card
- Auto-refresh every 30 seconds
- Connection fallback support
- Colored logging with file rotation
- Clean, modular architecture

## Setup

### Development (Windows)

```powershell
# Create virtual environment
python -m venv venv
.\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure - create .env file
Copy-Item .env.example .env
# Edit .env with your HA token

# Run
python app.py
```

### Production (Raspberry Pi)

```bash
# Setup Python environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Configure - create .env file
cp .env.example .env
# Edit .env with your HA token

# Run
python3 app.py
```

### Configuration

Create `.env` file from template:
```bash
cp .env.example .env
```

Edit `.env` with your settings:
- `HA_TOKEN` - Home Assistant long-lived access token (required)
- `FLASK_PORT` - Server port (default: 5001)
- `DEBUG` - Enable debug mode (default: False)

Get your HA token: Settings → People → Your User → Security → Long-Lived Access Tokens

## Usage

Access the visualizer at `http://localhost:5001` (or your RPi IP).

The page will automatically refresh every 30 seconds, or click "Refresh Now" for manual updates.

## Port Check

```bash
# Linux/macOS
sudo lsof -i :5001

# Windows
netstat -ano | findstr :5001
```

## License

MIT License - see LICENSE file for details