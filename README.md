# AutoInput-BMKGsoftV2

A modern automated data input application for BMKG Satu platform, built with PyQt6 and Playwright.

## Features

- Modern PyQt6-based user interface with a clean, professional design
- Automated data input for BMKG Satu platform
- METAR code processing and submission
- Browser automation using Playwright
- Multi-threaded processing for responsive UI
- Configurable logging system
- Auto-sending capability for periodic data submission
- Support for Excel/CSV file input
- Customizable UI themes and settings

## Requirements

- Python 3.9 or higher
- PyQt6
- Playwright
- Other dependencies (see requirements.txt)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/AutoInput-BMKGsoftV2.git
cd AutoInput-BMKGsoftV2
```

2. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Install Playwright browsers:
```bash
playwright install
```

## Usage

1. Run the application:
```bash
python -m src.ui.modern_app
```

2. Select the input file (Excel/CSV format)
3. Choose the observation hour
4. Click "Open Browser" to start the browser session
5. Click "Run Auto Input" to begin processing

## Configuration

The application can be configured through the `config/config.yaml` file, which includes settings for:

- Browser behavior
- UI customization
- Logging
- Automation parameters
- Security settings
- Monitoring options

## Project Structure

```
AutoInput-BMKGsoftV2/
├── src/
│   ├── core/           # Core functionality
│   ├── ui/             # User interface components
│   ├── utils/          # Utility functions
│   └── data/           # Data handling
├── config/             # Configuration files
├── logs/               # Log files
├── tests/              # Test files
└── requirements.txt    # Project dependencies
```

## Development

To contribute to the project:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests:
```bash
pytest
```
5. Submit a pull request

## Logging

The application uses a comprehensive logging system with different log files:

- `app.log`: General application logs
- `browser.log`: Browser automation logs
- `error.log`: Error-specific logs

Logs are automatically rotated to prevent excessive disk usage.

## Author

- Zulkifli Ramadhan (zulkiflirmdn@gmail.com)

## License

This project is licensed under the MIT License - see the LICENSE file for details. 