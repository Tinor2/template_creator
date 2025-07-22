"""
Template Editor GUI - A user-friendly interface for the Template Editor
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from tkinter.filedialog import asksaveasfilename
import os
from pathlib import Path
from typing import Dict, Any
from datetime import datetime

# Import our template editor
import os
import sys
from pathlib import Path

# Add the parent directory to Python path
sys.path.append(str(Path(__file__).parent.parent))

from Main.template_editor import load_config, create_template, save_modified_template, load_workbook

class TemplateEditorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Template Editor")
        self.root.geometry("800x600")
        
        # Variables
        self.config = None
        self.template_vars = {}
        self.entries = {}
        
        # Set config path
        self.config_path = os.path.join(Path(__file__).parent, 'config.json')
        
        # Load configuration
        self.load_configuration()
        
        # Setup UI
        self.setup_ui()
    
    def load_configuration(self):
        """Load the configuration file"""
        try:
            self.config = load_config(self.config_path)
            if not self.config or 'files' not in self.config:
                messagebox.showerror("Error", "Invalid or empty configuration file.")
                return False
            return True
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load configuration: {str(e)}")
            return False
    
    def setup_ui(self):
        """Setup the user interface"""
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Template selection
        ttk.Label(main_frame, text="Select Template:", font=('Arial', 10, 'bold')).pack(anchor='w')
        
        self.template_var = tk.StringVar()
        self.template_combo = ttk.Combobox(
            main_frame,
            textvariable=self.template_var,
            values=list(self.config['files'].keys()) if self.config else [],
            state='readonly',
            font=('Arial', 10)
        )
        self.template_combo.pack(fill=tk.X, pady=(0, 10))
        self.template_combo.bind('<<ComboboxSelected>>', self.on_template_selected)
        
        # Input frame (will be populated when template is selected)
        self.input_frame = ttk.Frame(main_frame)
        self.input_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        
        # Canvas and scrollbar for the input frame
        self.canvas = tk.Canvas(self.input_frame, borderwidth=0)
        self.scrollbar = ttk.Scrollbar(self.input_frame, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )
        
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        # Pack the canvas and scrollbar
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        
        # Button and save location frame
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        # Save location frame
        save_frame = ttk.Frame(button_frame)
        save_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        ttk.Label(save_frame, text="Save To:").pack(side=tk.LEFT, padx=(0, 5))
        
        self.save_path_var = tk.StringVar()
        self.save_entry = ttk.Entry(save_frame, textvariable=self.save_path_var, state='readonly')
        self.save_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        ttk.Button(
            save_frame,
            text="Browse...",
            command=self.browse_save_location,
            width=10
        ).pack(side=tk.LEFT, padx=(5, 0))
        
        # Generate button
        self.generate_btn = ttk.Button(
            button_frame,
            text="Generate Document",
            command=self.generate_document,
            state=tk.DISABLED,
            width=20
        )
        self.generate_btn.pack(side=tk.RIGHT)
        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_bar = ttk.Label(
            self.root,
            textvariable=self.status_var,
            relief=tk.SUNKEN,
            anchor=tk.W,
            padding=(5, 2)
        )
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        self.update_status("Select a template to begin")
    
    def on_template_selected(self, event=None):
        """When a template is selected, load its fields"""
        # Clear previous inputs
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        self.entries.clear()
        
        # Get selected template
        template_name = self.template_var.get()
        if not template_name or not self.config or 'files' not in self.config:
            return
        
        template_config = self.config['files'].get(template_name)
        if not template_config:
            return
        
        # Create input fields
        try:
            excel_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), template_config['path'])
            if not os.path.exists(excel_path):
                messagebox.showerror("Error", f"Template file not found: {excel_path}")
                self.update_status("Error: Template file not found")
                return
                
            workbook = load_workbook(excel_path, data_only=True)
            
            # Add input fields
            for i, (key, value) in enumerate(template_config['mappings'].items()):
                # Get the question text from the key cell
                question = self.get_cell_value(workbook, key)
                
                # Create a frame for this input
                frame = ttk.Frame(self.scrollable_frame, padding=5)
                frame.pack(fill=tk.X, pady=2)
                
                # Add label
                label = ttk.Label(frame, text=f"{question}:", width=40, anchor='w')
                label.pack(side=tk.LEFT, padx=(0, 5), fill=tk.X, expand=True)
                
                # Add entry field
                entry = ttk.Entry(frame)
                entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
                self.entries[value] = entry  # Use the coordinate as the key
            
            self.generate_btn.config(state=tk.NORMAL)
            self.update_status(f"Loaded template: {template_name}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load template: {str(e)}")
            self.update_status("Error loading template")
    
    def get_cell_value(self, workbook, cell_ref):
        """Get value from a cell reference in the workbook"""
        try:
            if '!' in cell_ref:
                sheet_name, cell = cell_ref.split('!')
                sheet = workbook[sheet_name]
            else:
                sheet = workbook.active
                cell = cell_ref
            return str(sheet[cell].value or "")
        except Exception:
            return cell_ref  # Return the cell reference if can't read the cell
    
    def generate_document(self):
        """Generate the document with user input"""
        template_name = self.template_var.get()
        if not template_name or not self.config or 'files' not in self.config:
            return
            
        template_config = self.config['files'].get(template_name)
        if not template_config:
            return
            
        # Check if save location is specified
        save_path = self.save_path_var.get()
        if not save_path:
            messagebox.showwarning("Warning", "Please select a save location first.")
            return
            
        excel_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), template_config['path'])
        
        # Collect user inputs
        results = {}
        for coord, entry in self.entries.items():
            results[coord] = entry.get()
        
        # Save the modified template
        try:
            # Use the user-specified path
            saved_path = save_modified_template(excel_path, results, template_name, output_path=save_path)
            if saved_path:
                messagebox.showinfo("Success", f"Document saved to:\n{saved_path}")
                self.update_status(f"Document saved: {os.path.basename(saved_path)}")
                # Clear form
                for entry in self.entries.values():
                    entry.delete(0, tk.END)
                self.template_var.set('')
                self.generate_btn.config(state=tk.DISABLED)
            else:
                messagebox.showerror("Error", "Failed to save document")
                self.update_status("Error saving document")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate document: {str(e)}")
            self.update_status("Error generating document")
    
    def browse_save_location(self):
        """Open a dialog to choose save location"""
        template_name = self.template_var.get()
        if not template_name:
            return
            
        # Suggest a default filename
        default_name = f"{template_name.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        
        # Open file dialog
        file_path = tk.filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")],
            initialfile=default_name,
            title="Save As"
        )
        
        if file_path:
            self.save_path_var.set(file_path)
    
    def update_status(self, message: str):
        """Update the status bar"""
        self.status_var.set(message)
        self.root.update_idletasks()

def main():
    root = tk.Tk()
    app = TemplateEditorApp(root)
    
    # Center the window
    window_width = 800
    window_height = 600
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x = (screen_width // 2) - (window_width // 2)
    y = (screen_height // 2) - (window_height // 2)
    root.geometry(f'{window_width}x{window_height}+{x}+{y}')
    
    root.mainloop()

if __name__ == "__main__":
    main()
