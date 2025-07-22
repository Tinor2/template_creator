# Template Editor

A simple, cross-platform application for filling out Excel templates with a user-friendly interface.

## Features

- Cross-platform (Windows and macOS)
- No installation required (standalone executable)
- User-friendly GUI
- Template-based system
- Customizable configuration

## Project Structure

The project is organized as follows:

```
Main/
├── config.json          # Template configurations
├── gui.py              # Main application GUI
├── template_editor.py  # Core functionality
├── Templates/          # Directory containing Excel templates
└── Results/           # Directory where generated files are saved
```

## Running the Application

1. Ensure you have Python 3.7+ installed
2. Navigate to the Main directory:
   ```bash
   cd Main
   ```
3. Run the application:
   ```bash
   python gui.py
   ```

## Usage

1. Select a template from the dropdown menu
2. Fill in the required fields
3. Click "Generate Document" to create your template

## Template Configuration

The application uses `config.json` for template configuration. Each template entry should specify:
- `path`: Relative path to the Excel template file
- `mappings`: Dictionary mapping question cells to answer cells

Example configuration:
```json
{
    "files": {
        "Template Name": {
            "path": "Templates/template.xlsx",
            "mappings": {
                "A1": "B1",
                "A2": "B2"
            }
        }
    }
}
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.