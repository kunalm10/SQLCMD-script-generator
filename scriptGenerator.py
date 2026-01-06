# -------------------------------
# Standard library imports
# -------------------------------

import csv                       # Used to read the CSV file (server, database)
from pathlib import Path         # Safer path handling across Windows
from datetime import datetime    # Used to generate timestamped output filenames

# -------------------------------
# GUI-related imports (Tkinter)
# -------------------------------

import tkinter as tk                             # Core Tkinter GUI library
from tkinter import filedialog, messagebox       # File picker and popup dialogs


# -------------------------------
# Tool metadata (display-only)
# -------------------------------

TOOL_NAME = "SQLCMD Multi-Server Script Generator"
TOOL_VERSION = "1.0.0"


# -------------------------------
# Core logic: generate SQLCMD file
# -------------------------------

def generate_sqlcmd(csv_path: Path, sql_script_path: Path) -> Path:
    """
    Reads server/database pairs from CSV
    Generates a SQLCMD script in the same folder as the CSV
    Returns the generated output file path
    """

    # Output file will be created in the same folder as the CSV
    output_dir = csv_path.parent

    # Timestamp ensures every run creates a unique file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Example: run_all_20260103_213522.sql
    output_file = output_dir / f"run_all_{timestamp}.sql"

    # List to accumulate all lines of the SQLCMD script
    lines = []

    # -------------------------------
    # SQLCMD header section
    # -------------------------------

    lines.extend([
        "------------------------------------------------------------",
        "-- MULTI-DATABASE SQLCMD SCRIPT",
        "-- Enable: Query > SQLCMD Mode",
        "------------------------------------------------------------",
        "",
        ':setvar USERNAME "username"',         # Placeholder username
        ':setvar PASSWORD "password"',         # Placeholder password
        f':setvar SCRIPT "{sql_script_path}"', # SQL file user selected
        "",
        "------------------------------------------------------------",
        "-- BEGIN EXECUTION",
        "------------------------------------------------------------",
        "",
        ""
    ])

    # -------------------------------
    # Read CSV and generate blocks
    # -------------------------------

    # Open CSV file safely
    with csv_path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)

        # Loop through each row of CSV
        for i, row in enumerate(reader, start=1):

            # Extract and clean values
            server = row["server"].strip()
            database = row["database"].strip()

            # Add one SQLCMD execution block per row
            lines.extend([
                f"PRINT '--- [{i}] {database} on {server} ---'",
                f":CONNECT {server} -U $(USERNAME) -P $(PASSWORD)",
                f"USE [{database}];",
                ":r $(SCRIPT)",
                "GO",
                ""
            ])

    # Write all accumulated lines into the output file
    output_file.write_text("\n".join(lines), encoding="utf-8")

    # Return the path so GUI can show it
    return output_file


# -------------------------------
# GUI helper functions
# -------------------------------

def browse_csv():
    """
    Opens file dialog to select CSV file
    Inserts selected path into the CSV entry box
    """
    path = filedialog.askopenfilename(
        filetypes=[("CSV Files", "*.csv")]
    )

    # Only update entry if user selected a file
    if path:
        csv_entry.delete(0, tk.END)  # Clear existing text
        csv_entry.insert(0, path)    # Insert selected path


def browse_sql():
    """
    Opens file dialog to select SQL script file
    Inserts selected path into the SQL entry box
    """
    path = filedialog.askopenfilename(
        filetypes=[("SQL Files", "*.sql")]
    )

    if path:
        sql_entry.delete(0, tk.END)  # Remove previous value
        sql_entry.insert(0, path)    # Insert new path


def run_tool():
    """
    Triggered when user clicks 'Generate' button
    Validates input and calls generator
    """
    try:
        # Convert text box values to Path objects
        csv_path = Path(csv_entry.get())
        sql_path = Path(sql_entry.get())

        # Basic validation
        if not csv_path.exists():
            raise FileNotFoundError("CSV file not found.")
        if not sql_path.exists():
            raise FileNotFoundError("SQL script file not found.")

        # Generate SQLCMD file
        output = generate_sqlcmd(csv_path, sql_path)

        # Show success message
        messagebox.showinfo(
            "Success",
            f"SQLCMD script generated:\n{output}"
        )

    except Exception as e:
        # Show error message in GUI instead of console
        messagebox.showerror("Error", str(e))


# -------------------------------
# GUI layout
# -------------------------------

# Create the main application window
root = tk.Tk()

# Set window title
root.title(f"{TOOL_NAME} v{TOOL_VERSION}")

# Fixed window size
root.geometry("600x220")
root.resizable(False, False)

# Tool title label
tk.Label(
    root,
    text=TOOL_NAME,
    font=("Segoe UI", 12, "bold")
).pack(pady=5)

# Version label
tk.Label(
    root,
    text=f"Version {TOOL_VERSION}"
).pack()

# Container frame for form fields
frame = tk.Frame(root)
frame.pack(pady=15)

# -------------------------------
# CSV input row
# -------------------------------

tk.Label(frame, text="CSV File:").grid(row=0, column=0, sticky="e")

csv_entry = tk.Entry(frame, width=50)
csv_entry.grid(row=0, column=1, padx=5)

tk.Button(
    frame,
    text="Browse",
    command=browse_csv
).grid(row=0, column=2)

# -------------------------------
# SQL input row
# -------------------------------

tk.Label(frame, text="SQL Script:").grid(row=1, column=0, sticky="e", pady=5)

sql_entry = tk.Entry(frame, width=50)
sql_entry.grid(row=1, column=1, padx=5)

tk.Button(
    frame,
    text="Browse",
    command=browse_sql
).grid(row=1, column=2)

# -------------------------------
# Generate button
# -------------------------------

tk.Button(
    root,
    text="Generate SQLCMD Script",
    command=run_tool,
    width=30
).pack(pady=15)

# -------------------------------
# Start GUI event loop
# -------------------------------

root.mainloop()
