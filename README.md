# Quality Evaluation Tool

Automated website quality evaluation tool using browser agents and AI.

## Quick Start

```bash
# First time setup
./setup_build_env.sh

# Build executable
./build.sh

# Run
cd dist
./quality_evaluation
```

## Configuration

Edit `config.yaml` to customize:
- **Websites** to test (Google Travel, Skyscanner, Booking.com, Agoda)
- **Features** to evaluate (autocomplete, relevance, partner mix, distance accuracy)
- **Cities** to test
- **Prompts** for evaluation criteria

All settings are documented inline in `config.yaml`.

## Building Release Binary

See [BUILD_QUICKSTART.md](BUILD_QUICKSTART.md) for quick reference
See [RELEASE_GUIDE.md](RELEASE_GUIDE.md) for detailed instructions

## Project Structure

```
quality_evaluation/
├── src/
│   ├── quality_evaluator_agent.py   # Main entry point
│   ├── strands_browser_direct.py    # Browser agent
│   ├── config_loader.py             # Configuration loader
│   ├── custom_browser.py            # Browser tool extensions
│   ├── aws_credential_setup.py      # AWS authentication
│   ├── config.yaml                  # Settings & prompts (EDIT THIS)
│   ├── constants.py                 # Deprecated - use config.yaml
│   └── __init__.py                  # Package initialization
├── requirements.txt                 # Python dependencies
├── build.sh                         # Build script
├── setup_build_env.sh               # Environment setup
├── quality_evaluation.spec          # PyInstaller spec
├── bin/                             # AWS authentication binaries
│   ├── mshell                       # Shell for AWS auth
│   └── saml2aws                     # SAML authentication
├── venv/                            # Python virtual environment (auto-created)
├── scripts/                         # Utility scripts (Confluence tools)
└── dist/                            # Build output
    ├── quality_evaluation           # Executable
    └── config.yaml                  # Bundled config
```

## Usage

### Run from Source
```bash
source venv/bin/activate && python3 src/quality_evaluator_agent.py
```

### Run from Binary
```bash
cd dist
./quality_evaluation
```

### Edit Configuration
```bash
vim config.yaml
# Enable websites, features, add cities, modify prompts
./build.sh  # Rebuild if needed
```

## Output

Results are saved to:
- `quality_evaluation_output/text_recording/` - Individual website recordings
- `quality_evaluation_output/comparison_analysis/` - Comparison reports

## Requirements

- Python 3.9+
- Dependencies listed in `requirements.txt`
- Playwright browsers (installed automatically by setup script)

**Note**: This project uses `strands-agents` and `strands-agents-tools` - the AWS-backed AI agents framework for building intelligent agents with model-driven approaches.

## Distribution

Create release package:
```bash
cd dist
tar -czf quality_evaluation_release.tar.gz quality_evaluation config.yaml
```

Share the tarball with colleagues. They can:
1. Extract it
2. Edit `config.yaml`
3. Run `./quality_evaluation`

## Documentation

- **BUILD_QUICKSTART.md** - Quick build reference
- **RELEASE_GUIDE.md** - Detailed build guide
- **config.yaml** - All settings with inline documentation

## Development

```bash
# Setup environment
./setup_build_env.sh

# Activate venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run directly
python3 src/quality_evaluator_agent.py

# Build after changes
./build.sh
```

## Notes

- Uses own virtual environment at `quality_evaluation/venv`
- Config file is self-documented (no separate user guide needed)
- Executable bundles config.yaml (users can edit it)
- No default config - fails if config.yaml missing
