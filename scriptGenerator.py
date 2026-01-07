# ============================================================
# SQLCMD Multi-Server Script Generator (GUI)
# Version: 1.0.1
# ============================================================

# -------------------------------
# Standard library imports
# -------------------------------
import os
import sys
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
TOOL_VERSION = "1.0.1"

# -------------------------------
# Global variables
# -------------------------------

csv_entry = None
sql_entry = None
username_entry = None
password_entry = None

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
    output_dir = csv_path.parent / "multiDB_script"
    output_dir.mkdir(exist_ok=True)

    # Create a timestamp so each run produces a unique file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Example: run_all_20260103_220915.sql
    output_filename = f"{sql_script_path.stem}_multiDB_{timestamp}.sql"
    output_file = output_dir / output_filename

    # Accumulate all lines of the SQLCMD script
    lines = []

    # -------------------------------
    # SQLCMD header
    # -------------------------------

    SQLCMD_BANNER = """/*****************************************************************************************
    ******************************************************************************************
    **                                                                                      **
    **                                                                                      **
    **                                                                                      **
    **                                                                                      **
    **   SQLCMD MODE REQUIRED                                                               **
    **                                                                                      **
    **   IMPORTANT: This script uses SQLCMD directives and will FAIL if                     **
    **   SQLCMD Mode is not enabled.                                                        **
    **                                                                                      **
    **   REQUIRED STEPS IN SSMS:                                                            **
    **                                                                                      **
    **                Query -> SQLCMD Mode                                                  **
    **                                                                                      **
    **                                                                                      **
    **                                                                                      **
    **                                                                                      **
    ******************************************************************************************
    ******************************************************************************************/
    """


    lines.extend([
        SQLCMD_BANNER,
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

    with open_csv_safely(csv_path) as f:
        reader = csv.DictReader(f)

        # Validate headers ONCE
        if reader.fieldnames != ["server", "database"]:
            raise ValueError(
                "Invalid CSV headers.\n\n"
                "CSV header must contain exactly:\n"
                "server,database"
            )

        for i, row in enumerate(reader, start=1):
            server = row["server"].strip()
            database = row["database"].strip()

            lines.extend([
                f"PRINT '--- [{i}] {database} on {server} ---'",
                f":CONNECT {server} -U $(USERNAME) -P $(PASSWORD)",
                f"USE [{database}];",
                ":r $(SCRIPT)",
                "GO",
                "PRINT '---------------------------------------------------------------------------------------------'"
                "PRINT ''"
                ""
            ])

    # Write final SQLCMD file to disk
    output_file.write_text("\n".join(lines), encoding="utf-8")
    # Open output folder automatically on Windows
    if sys.platform.startswith("win"):
        os.startfile(output_dir)

    return output_file

def open_csv_safely(csv_path: Path):
    """
    Attempts to open CSV using common encodings used on Windows.
    Fails gracefully with a clear error if none work.
    """
    encodings_to_try = ["utf-8-sig", "cp1252"]

    last_error = None

    for encoding in encodings_to_try:
        try:
            return csv_path.open(newline="", encoding=encoding)
        except UnicodeDecodeError as e:
            last_error = e

    raise ValueError(
        "Unable to read CSV file.\n"
        "Please save the file as 'CSV UTF-8' and try again."
    )

# -------------------------------
# GUI helper functions
# -------------------------------

def browse_csv():
    """Select CSV file and populate textbox"""
    path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
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

def start_gui():
    global csv_entry, sql_entry, username_entry, password_entry

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

if __name__ == "__main__":
    start_gui()