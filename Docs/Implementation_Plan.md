# Implementation Plan for Template Generator Enhancements

This document outlines the step-by-step plan to implement the features described in `Brief_220725.md`. The implementation will adhere to the guidelines in `RULES.md` and will be confined to the `Main/` directory.

## Core Objective

To enhance the template generator with two main features:
1.  **Template Categorization:** Allow users to first select a category and then a template within that category.
2.  **Serial Number & Quantity Management:** Implement a robust system for generating multiple templates with unique, auto-incrementing serial numbers.

## Part 1: Consolidating Configuration and State

As per the suggestion to simplify file management, the serial number tracking data will be merged into `config.json`. This centralizes all data into a single file while logically separating static configuration from dynamic state using distinct top-level keys.

### 1.1. Updated `config.json` Structure

The `config.json` file will be restructured to include a new top-level key, `serial_numbers`, alongside the categorized `files` key.

**Proposed Structure:**
```json
{
  "files": {
    "Packing Lists": {
      "Packing List 33kV Single Manual": {
        "path": "...",
        "mappings": { ... }
      }
    },
    "ITP": {
      "ITP 33kV Single Manual": {
        "path": "...",
        "mappings": { ... }
      }
    }
  },
  "serial_numbers": {
    "1234": 1,
    "1235": 2
  }
}
```

### 1.2. Changes to `template_editor.py`

- The `load_config` function will remain largely the same but will now also provide access to the `serial_numbers` dictionary.
- A new function, `save_config(config_data)`, will be created. This function will be responsible for writing the entire updated configuration object (including the modified serial numbers) back to `config.json` atomically to prevent data corruption.

## Part 2: Template Categorization

### 2.1. `gui.py` - UI Changes

1.  **Add Category Combobox:** A new `ttk.Combobox` for selecting the template category will be added to the top of the UI.
2.  **Update Template Combobox:** The existing template `Combobox` will be initially disabled.
3.  **Implement `on_category_selected`:** An event handler will be created. When a category is selected:
    - It will enable the template `Combobox`.
    - It will populate the template `Combobox` with only the templates belonging to the selected category.

## Part 3: Serial Number and Quantity Management

### 3.1. `gui.py` - UI and Logic Changes

1.  **Add Quantity Input:** A new `ttk.Entry` field for **"Quantity"** will be added to the UI.
2.  **Update `generate_document` Method:** This method will be the primary driver.
    - It will read the selected template, all user inputs, and the quantity.
    - It will identify the base serial number from the input fields (as it's the last one).
    - It will call a new central processing function in `template_editor.py` (e.g., `process_template_generation`) to handle the main logic.

### 3.2. `template_editor.py` - Core Logic Implementation

1.  **Create `process_template_generation` function:** This new function will orchestrate the entire process.
    - **Inputs:** It will take the template details, user data, quantity, and the full config object.
    - **Looping:** It will loop from 1 to the specified quantity.
    - **Serial Number Logic (inside the loop):**
        1.  Get the current count for the base serial number from `config['serial_numbers']`. If it doesn't exist, the starting count is 0.
        2.  Increment the count to get the new suffix for the unique serial number (e.g., `1234-1`, `1234-2`).
        3.  Update the user data dictionary with this new, unique serial number.
        4.  Update the `serial_numbers` dictionary in memory with the new total count for the base serial number.
    - **File Naming:** The output filename will be changed from a timestamp to the format: `{template_name}_{unique_serial_number}.xlsx`.
    - **Saving:** It will call the existing `save_modified_template` function (with modifications) to save each of the generated files.
2.  **Modify `save_modified_template`:**
    - This function will be simplified to focus only on creating a single Excel file from the provided data, without generating filenames or handling directories.
3.  **Final Save:** After the generation loop in `process_template_generation` is complete, it will call the new `save_config` function once to write the updated serial number counts back to `config.json`.

This plan covers all requirements from the brief while incorporating your feedback for a more streamlined file structure.
