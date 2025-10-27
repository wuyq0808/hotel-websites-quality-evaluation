# Web App Guide

## Quick Start

```bash
./run_webapp.sh
```

This will:
1. Activate the virtual environment
2. Install Flask if needed
3. Start the web server at http://localhost:5000
4. Open your browser automatically

## Using the Web App

### 1. Configure Your Evaluation
- **Test Stay**: Add cities and set check-in/check-out dates
- **Features to Test**: Enable features you want to evaluate
- **Site Instructions**: Customize browser agent instructions (collapsed by default)
- **Feature Prompts**: Customize evaluation criteria (collapsed by default)
- **System Prompts**: Modify agent behaviors (collapsed by default)

### 2. Run the Evaluation
1. Click **"Save & Run"** button
2. The log viewer appears automatically
3. Watch real-time output as the evaluation runs
4. Green pulsing indicator shows when running

### 3. Monitor Progress
- Logs update every 2 seconds
- Auto-scrolls to latest output
- Status indicator shows: Running, Completed, Error, or Stopped

### 4. Stop if Needed
- Click **"Stop"** button to gracefully halt the evaluation
- Current task will finish, then process stops
- Partial results are saved

## Features

### Real-time Log Viewing
- Terminal-style output in the browser
- Auto-refresh every 2 seconds
- Auto-scroll to latest logs
- Dark theme for comfortable viewing

### Process Control
- Start/Stop buttons
- Graceful shutdown handling
- Process status tracking
- Automatic state management

### Configuration Management
- All settings in one page
- YAML generation from UI
- Saved to `src/config.yaml`
- Same format as command-line tool

## Output Files

Results are saved to:
- **Text Recordings**: `quality_evaluation_output/text_recording/`
  - Organized by: feature → city → dates → website
- **Comparisons**: `quality_evaluation_output/comparison_analysis/`
  - Organized by: feature → city → dates
- **Logs**: `logs/evaluation_TIMESTAMP.log`
  - One file per run

## Architecture

```
config-editor.html (Frontend)
    ↓ HTTP API
web_app.py (Flask Server)
    ↓ subprocess
quality_evaluator_agent.py (Evaluation)
    ↓ writes to
logs/evaluation_TIMESTAMP.log
```

## API Endpoints

- `POST /api/save-config` - Save YAML configuration
- `POST /api/start` - Start evaluation process
- `POST /api/stop` - Stop running evaluation
- `GET /api/status` - Get process status
- `GET /api/logs` - Get current log file contents
- `GET /api/log-files` - List all log files

## Troubleshooting

### Port Already in Use
If port 5000 is busy:
```bash
# Edit src/web_app.py, change port on line:
app.run(port=5000, ...)
```

### Flask Not Installed
```bash
source venv/bin/activate
pip install flask>=2.3.0
```

### Logs Not Updating
- Check browser console for errors
- Ensure evaluation is running (status indicator)
- Refresh the page

### Process Won't Stop
- Try Stop button again
- Close the browser and restart web app
- Check `logs/` directory for error details

## Comparison with CLI

| Feature | Web App | CLI (`quality_evaluator_agent.py`) |
|---------|---------|-----------------------------------|
| Configuration | Browser UI | Edit `config.yaml` manually |
| Running | Click button | `python3 src/quality_evaluator_agent.py` |
| Logs | Real-time in browser | Terminal output |
| Stop | Stop button | Ctrl+C |
| Results | Same location | Same location |

Both methods use the same evaluation engine and produce identical results.

## Development

### Running Manually
```bash
# Activate environment
source venv/bin/activate

# Start server
python3 src/web_app.py
```

### Testing
1. Open http://localhost:5000
2. Configure a simple test (1 city, 1 feature, 1 website)
3. Click "Save & Run"
4. Verify logs appear
5. Click "Stop" and verify graceful shutdown

## Notes

- Each run creates a new timestamped log file
- Old logs are preserved in `logs/` directory
- Stop button sends SIGTERM for graceful shutdown
- Evaluation runs in a separate process
- Web server stays running between evaluations
