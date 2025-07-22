"""
Template Editor - A tool for editing templates from Excel files
"""

import json
from openpyxl import load_workbook
from typing import Dict, Tuple, Any
import os
import shutil
from datetime import datetime
from pathlib import Path

def load_config(config_path: str = None) -> Dict:
    """Load configuration from JSON file"""
    if config_path is None:
        # Default to config.json in the Main directory
        config_path = os.path.join(Path(__file__).parent, 'config.json')
    
    try:
        with open(config_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: {config_path} not found")
        return {}
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON in {config_path}")
        return {}

def get_cell_value(workbook: Any, cell_ref: str) -> str:
    """Get value from a cell reference in the workbook"""
    try:
        # Split the reference into sheet name and cell (if sheet is specified)
        if '!' in cell_ref:
            sheet_name, cell = cell_ref.split('!')
            sheet = workbook[sheet_name]
        else:
            sheet = workbook.active
            cell = cell_ref
        return str(sheet[cell].value)
    except Exception as e:
        print(f"Error reading cell {cell_ref}: {str(e)}")
        return ""

def create_template(excel_path: str, config: Dict[str, str]) -> Dict[str, Any]:
    """
    Create template from Excel file using configuration
    
    Args:
        excel_path: Path to the Excel file
        config: Dictionary mapping cell references to their values
    
    Returns:
        Dictionary containing the template data, mapping coordinates to user responses
    """
    try:
        # Load workbook
        workbook = load_workbook(excel_path, data_only=True)
        
        # Initialize results dictionary
        results: Dict[str, str] = {}
        
        # Process each mapping
        for key, value in config.items():
            # Get the question text from the key cell
            question = get_cell_value(workbook, key)
            # Get the coordinate that will be used as the key
            coordinate = value
            
            # Get user input
            user_input = input(f"{question}: ")
            
            # Store the user input using the coordinate as the key
            results[coordinate] = user_input
            
        return results
        
    except Exception as e:
        print(f"Error creating template: {str(e)}")
        return {}

def display_available_templates(config: Dict) -> None:
    """Display available templates to the user"""
    print("Available templates:")
    for i, template_name in enumerate(config['files'].keys(), 1):
        print(f"{i}. {template_name}")

def get_template_selection(config: Dict) -> str:
    """Get user's template selection"""
    while True:
        display_available_templates(config)
        try:
            choice = int(input("\nSelect a template (enter number): "))
            if 1 <= choice <= len(config['files']):
                return list(config['files'].keys())[choice - 1]
            print("Invalid selection. Please try again.")
        except ValueError:
            print("Please enter a number.")

def save_modified_template(template_path: str, results: Dict[str, str], template_name: str, output_path: str = None) -> str:
    # Ensure template path is absolute
    if not os.path.isabs(template_path):
        template_path = os.path.join(Path(__file__).parent.parent, template_path)
    """
    Save a modified copy of the template with user input
    
    Args:
        template_path: Path to the original template
        results: Dictionary mapping coordinates to user responses
        template_name: Name of the template (for generating output filename if output_path is not provided)
        output_path: Optional custom output path. If not provided, a default path will be generated.
        
    Returns:
        Path to the saved file
    """
    try:
        if not output_path:
            # Create Results directory if it doesn't exist
            results_dir = Path(Path(__file__).parent.parent) / "Results"
            results_dir.mkdir(exist_ok=True)
        
            # Generate output path if not provided
            if not output_path:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_filename = f"{template_name.replace(' ', '_')}_{timestamp}.xlsx"
                output_path = str(results_dir / output_filename)
        
        # Ensure the output directory exists
        output_dir = os.path.dirname(output_path)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
        # Copy the template to the new location
        shutil.copy2(template_path, output_path)
        
        # Load the workbook and update cells
        workbook = load_workbook(output_path)
        
        for coordinate, value in results.items():
            # Handle sheet references (e.g., 'Sheet1!A1')
            if '!' in coordinate:
                sheet_name, cell_ref = coordinate.split('!')
                sheet = workbook[sheet_name]
                cell = cell_ref
            else:
                sheet = workbook.active
                cell = coordinate
            
            # Update the cell value
            sheet[cell] = value
        
        # Save the modified workbook
        workbook.save(output_path)
        return str(output_path)
        
    except Exception as e:
        print(f"Error saving modified template: {str(e)}")
        return ""

def main():
    # Load configuration
    config = load_config("Main/config.json")
    
    if not config:
        print("No valid configuration found. Please create a config.json file.")
        return
    
    # Get template selection
    template_name = get_template_selection(config)
    template_config = config['files'][template_name]
    
    # Get full path to Excel file
    excel_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), template_config['path'])
    
    # Create template
    results = create_template(excel_path, template_config['mappings'])
    
    if results:
        # Save modified template
        saved_path = save_modified_template(excel_path, results, template_name)
        
        if saved_path:
            print(f"\nTemplate created successfully! Saved to: {saved_path}")
            print("\nUpdated values:")
            for coord, value in results.items():
                print(f"{coord}: {value}")
        else:
            print("\nError: Could not save the modified template.")

if __name__ == "__main__":
    main()
