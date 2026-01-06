# ============================================================
# SQLCMD Multi-Server Script Generator (GUI)
# Version: 1.0.0
# ============================================================

# -------------------------------
# Standard library imports
# -------------------------------

import csv                       # For reading server/database CSV
from pathlib import Path         # For safe Windows path handling
from datetime import datetime    # For timestamped output filenames

# -------------------------------
# GUI imports (Tkinter)
# -------------------------------

import tkinter as tk
from tkinter import filedialog, messagebox


# -------------------------------
# Tool metadata
# -------------------------------

TOOL_NAME = "SQLCMD Multi-Server Script Generator"
TOOL_VERSION = "1.0.0"


# -------------------------------
# Core logic: Generate SQLCMD file
# -------------------------------

def generate_sqlcmd(csv_path: Path, sql_script_path: Path,
                    username: str, password: str) -> Path:
    """
    Reads server/database pairs from CSV
    Embeds username/password into SQLCMD variables
    Writes output SQLCMD file next to the CSV
    """

    # Output file location = same folder as CSV
    output_dir = csv_path.parent

    # Create a timestamp so each run produces a unique file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Example: run_all_20260103_220915.sql
    output_file = output_dir / f"run_all_{timestamp}.sql"

    # Accumulate all lines of the SQLCMD script
    lines = []

    # -------------------------------
    # SQLCMD header
    # -------------------------------

    lines.extend([
        "------------------------------------------------------------",
        "-- MULTI-DATABASE SQLCMD SCRIPT",
        "-- Enable: Query > SQLCMD Mode",
        "------------------------------------------------------------",
        "",
        f':setvar USERNAME "{username}"',
        f':setvar PASSWORD "{password}"',
        f':setvar SCRIPT "{sql_script_path}"',
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

    with csv_path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)

        for i, row in enumerate(reader, start=1):
            server = row["server"].strip()
            database = row["database"].strip()

            lines.extend([
                f"PRINT '--- [{i}] {database} on {server} ---'",
                f":CONNECT {server} -U $(USERNAME) -P $(PASSWORD)",
                f"USE [{database}];",
                ":r $(SCRIPT)",
                "GO",
                ""
            ])

    # Write final SQLCMD file to disk
    output_file.write_text("\n".join(lines), encoding="utf-8")

    return output_file


# -------------------------------
# GUI helper functions
# -------------------------------

def browse_csv():
    """Select CSV file and populate textbox"""
    path = filedialog.askopenfilename(
        filetypes=[("CSV Files", "*.csv")]
    )
    if path:
        csv_entry.delete(0, tk.END)
        csv_entry.insert(0, path)


def browse_sql():
    """Select SQL script file and populate textbox"""
    path = filedialog.askopenfilename(
        filetypes=[("SQL Files", "*.sql")]
    )
    if path:
        sql_entry.delete(0, tk.END)
        sql_entry.insert(0, path)


def run_tool():
    """
    Triggered when user clicks Generate
    Validates inputs and runs SQLCMD generator
    """
    try:
        csv_path = Path(csv_entry.get())
        sql_path = Path(sql_entry.get())
        username = username_entry.get().strip()
        password = password_entry.get().strip()

        # Input validation
        if not csv_path.exists():
            raise FileNotFoundError("CSV file not found.")
        if not sql_path.exists():
            raise FileNotFoundError("SQL script file not found.")
        if not username:
            raise ValueError("Username is required.")
        if not password:
            raise ValueError("Password is required.")

        # Generate SQLCMD file
        output = generate_sqlcmd(csv_path, sql_path, username, password)

        messagebox.showinfo(
            "Success",
            f"SQLCMD script generated:\n{output}"
        )

    except Exception as e:
        messagebox.showerror("Error", str(e))


# -------------------------------
# GUI layout
# -------------------------------

root = tk.Tk()
root.title(f"{TOOL_NAME} v{TOOL_VERSION}")
root.geometry("650x300")
root.resizable(False, False)

# Tool title
tk.Label(
    root,
    text=TOOL_NAME,
    font=("Segoe UI", 12, "bold")
).pack(pady=5)

# Version
tk.Label(
    root,
    text=f"Version {TOOL_VERSION}"
).pack()

# Main form container
frame = tk.Frame(root)
frame.pack(pady=15)

# -------------------------------
# CSV input row
# -------------------------------

tk.Label(frame, text="CSV File:").grid(row=0, column=0, sticky="e")
csv_entry = tk.Entry(frame, width=50)
csv_entry.grid(row=0, column=1, padx=5)
tk.Button(frame, text="Browse", command=browse_csv).grid(row=0, column=2)

# -------------------------------
# SQL input row
# -------------------------------

tk.Label(frame, text="SQL Script:").grid(row=1, column=0, sticky="e", pady=5)
sql_entry = tk.Entry(frame, width=50)
sql_entry.grid(row=1, column=1, padx=5)
tk.Button(frame, text="Browse", command=browse_sql).grid(row=1, column=2)

# -------------------------------
# Username row
# -------------------------------

tk.Label(frame, text="Username:").grid(row=2, column=0, sticky="e", pady=5)
username_entry = tk.Entry(frame, width=50)
username_entry.grid(row=2, column=1, padx=5, columnspan=2)

# -------------------------------
# Password row
# -------------------------------

tk.Label(frame, text="Password:").grid(row=3, column=0, sticky="e", pady=5)
password_entry = tk.Entry(frame, width=50, show="*")
password_entry.grid(row=3, column=1, padx=5, columnspan=2)

# -------------------------------
# Generate button
# -------------------------------

tk.Button(
    root,
    text="Generate SQLCMD Script",
    command=run_tool,
    width=35
).pack(pady=20)

# -------------------------------
# Start GUI event loop
# -------------------------------

root.mainloop()
