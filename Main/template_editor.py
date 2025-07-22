"""
File name: template_editor.py
Template Editor - A tool for editing templates from Excel files
"""

from calendar import c
import json
import sys  # Added missing import
from openpyxl import load_workbook
from typing import Dict, Tuple, Any
import os
import shutil
from datetime import datetime
from pathlib import Path

def get_base_path():
    """Gets the base path of the project, supporting PyInstaller."""
    if getattr(sys, 'frozen', False):
        # The path of the executable
        return os.path.dirname(sys.executable)
    else:
        # The path of this file (template_editor.py) is .../Main/template_editor.py
        # We need the Main directory (the directory containing this file).
        return os.path.dirname(os.path.abspath(__file__))

def load_config(config_path: str) -> Dict:
    """Load configuration from JSON file"""
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Configuration file not found at {config_path}")
    
    with open(config_path, 'r') as f:
        config = json.load(f)
    
    # Make template paths absolute relative to the Main directory
    # Since template_editor.py is in Main/, we get the Main directory
    main_directory = os.path.dirname(os.path.abspath(__file__))
    
    for category in config.get('files', {}).values():
        for template_details in category.values():
            if 'path' in template_details and not os.path.isabs(template_details['path']):
                template_details['path'] = os.path.join(main_directory, template_details['path'])
    return config

def save_config(config_path: str, config_data: Dict):
    """Save the configuration dictionary to the JSON file."""
    with open(config_path, 'w') as f:
        json.dump(config_data, f, indent=2)

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
    for category_name, category in config['files'].items():
        for i, template_name in enumerate(category.keys(), 1):
            print(f"{category_name} - {i}. {template_name}")

def get_template_selection(config: Dict) -> Tuple[str, str]:
    """Get user's template selection"""
    while True:
        display_available_templates(config)
        try:
            category_name = input("\nEnter category name: ")
            choice = int(input("\nEnter template number: "))
            if category_name in config['files']:
                if 1 <= choice <= len(config['files'][category_name]):
                    return category_name, list(config['files'][category_name].keys())[choice - 1]
            print("Invalid selection. Please try again.")
        except ValueError:
            print("Please enter a number.")

def save_modified_template(template_path: str, results: Dict[str, str], output_path: str) -> str:
    """
    Creates and saves a modified copy of the template with the given results.
    """
    if not os.path.exists(template_path):
        raise FileNotFoundError(f"Template file not found: {template_path}")

    # Ensure the output directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # Copy the template to the new path
    shutil.copy2(template_path, output_path)

    # Load the new workbook and update cells
    wb = load_workbook(output_path)
    for coordinate, value in results.items():
        if not value:
            continue
        try:
            sheet_name, cell = (coordinate.split('!') if '!' in coordinate else (None, coordinate))
            sheet = wb[sheet_name] if sheet_name else wb.active
            sheet[cell] = value
        except Exception as e:
            print(f"Warning: Could not write to cell {coordinate}: {e}")
    
    wb.save(output_path)
    return output_path

def process_template_generation(
    config: Dict,
    config_path: str,
    category_name: str,
    template_name: str,
    user_inputs: Dict[str, str],
    quantity: int,
    output_dir: str
) -> list[str]:
    """
    Orchestrates the generation of templates, including serial number handling.
    """
    template_config = config['files'][category_name][template_name]
    template_path = template_config['path']
    
    # The last mapping is assumed to be the serial number
    serial_number_key = list(template_config['mappings'].values())[-1]
    base_serial_number = user_inputs.get(serial_number_key)

    if not base_serial_number:
        raise ValueError("Serial number is missing from user inputs.")

    generated_files = []
    serial_numbers_data = config.get('serial_numbers', {})

    for i in range(quantity):
        # Get the current count for this serial number, or start at 0
        current_count = serial_numbers_data.get(base_serial_number, 0)
        new_count = current_count + 1
        
        # Update the serial number for this specific template
        unique_serial_number = f"{base_serial_number}-{new_count}"
        results_for_this_file = user_inputs.copy()
        results_for_this_file[serial_number_key] = unique_serial_number
        
        # Define the output filename
        output_filename = f"{template_name.replace(' ', '_')}_{unique_serial_number}.xlsx"
        output_path = os.path.join(output_dir, output_filename)
        
        # Save the individual file
        save_modified_template(template_path, results_for_this_file, output_path)
        generated_files.append(output_path)
        
        # Update the count in our dictionary for the next iteration
        serial_numbers_data[base_serial_number] = new_count

    # After the loop, save the updated config file with the new serial counts
    config['serial_numbers'] = serial_numbers_data
    save_config(config_path, config)
    
    return generated_files

config = load_config("Main/config.json")
