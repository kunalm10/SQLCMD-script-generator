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
import json
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
pcb_entry = None
source_mode = None          # tk.StringVar
builtin_category = None     # tk.StringVar
builtin_target_vars = {}

# -------------------------------
# Core logic: Generate SQLCMD file
# -------------------------------

def generate_sqlcmd(csv_path: Path, sql_script_path: Path,
                    username: str, password: str, pcb:str, 
                    targets: list[tuple[str, str]],) -> Path:
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
    pcb_suffix = f"_{pcb}" if pcb else ""
    output_filename = f"{sql_script_path.stem}{pcb_suffix}_multiDB_{timestamp}.sql"
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
    ])

    # OPTIONAL PCB HEADER
    if pcb:
        lines.extend([
            f"-- PCB: {pcb}",
            ""
        ])


    lines.extend([
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
    # Generate blocks from targets
    # -------------------------------

    for i, (server, database) in enumerate(targets, start=1):
        lines.extend([
            f"PRINT '--- [{i}] {database} on {server} ---'",
            f":CONNECT {server} -U $(USERNAME) -P $(PASSWORD)",
            f"USE [{database}];",
            "GO",
            ":r $(SCRIPT)",
            "GO",
            "PRINT ''",
            "PRINT '---------------------------------------------------------------------------------------------'",
            "PRINT ''",
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

def get_targets_from_csv(csv_path: Path) -> list[tuple[str, str]]:
    """
    Returns a list of (server, database) pairs from the CSV.
    """
    targets: list[tuple[str, str]] = []

    with open_csv_safely(csv_path) as f:
        reader = csv.DictReader(f)

        # Validate headers ONCE
        if reader.fieldnames != ["server", "database"]:
            raise ValueError(
                "Invalid CSV headers.\n\n"
                "CSV header must contain exactly:\n"
                "server,database"
            )

        for row in reader:
            server = row["server"].strip()
            database = row["database"].strip()
            if server and database:
                targets.append((server, database))

    return targets

def get_targets_from_builtin(category: str) -> list[tuple[str, str]]:
    return BUILTIN_TARGETS.get(category, [])

def load_builtin_targets() -> dict[str, list[tuple[str, str]]]:
    """
    Loads built-in targets from targets.json (same folder as this script).
    Returns: {"Master DBs": [(server, db), ...], ...}
    """
    config_path = Path(__file__).parent / "targets.json"
    if not config_path.exists():
        raise FileNotFoundError(f"targets.json not found at: {config_path}")

    with config_path.open(encoding="utf-8") as f:
        raw = json.load(f)

    targets = {}
    for category, items in raw.items():
        targets[category] = []
        for item in items:
            server = (item.get("server") or "").strip()
            database = (item.get("database") or "").strip()
            if server and database:
                targets[category].append((server, database))

    return targets

BUILTIN_TARGETS = load_builtin_targets()
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
        pcb = pcb_entry.get().strip()

        # Input validation
        if not csv_path.exists():
            raise FileNotFoundError("CSV file not found.")
        if not sql_path.exists():
            raise FileNotFoundError("SQL script file not found.")
        
        # Decide targets source: CSV or Built-in
        if source_mode is not None and source_mode.get() == "builtin":
            targets =  [
                (server, db)
                for (cat, server, db), var in builtin_target_vars.items()
                if var.get()
            ]
        else:
            targets = get_targets_from_csv(csv_path)
        if not targets:
            raise ValueError("No server/database targets selected.")
        
        if not username:
            username = "username"
        if not password:
            password = "password"

        # Generate SQLCMD file
        output = generate_sqlcmd(csv_path, sql_path, username, password, pcb, targets)

        messagebox.showinfo(
            "Success",
            f"SQLCMD script generated:\n{output}"
        )

    except Exception as e:
        messagebox.showerror("Error", str(e))


# -------------------------------
# GUI layout
# -------------------------------

def render_builtin_targets(category, container):
    for w in container.winfo_children():
        w.destroy()

    for server, db in BUILTIN_TARGETS.get(category, []):
        key = (category, server, db)
        if key not in builtin_target_vars:
            builtin_target_vars[key] = tk.BooleanVar(value=True)

        cb = tk.Checkbutton(
            container,
            text=f"{db} @ {server}",
            variable=builtin_target_vars[key]
        )
        cb.pack(anchor="w")

def set_category_selection(category: str, checked: bool):
    for (cat, server, db), var in builtin_target_vars.items():
        if cat == category:
            var.set(checked)

def start_gui():
    global csv_entry, sql_entry, username_entry, password_entry, pcb_entry, source_mode, builtin_category

    root = tk.Tk()
    root.title(f"{TOOL_NAME} v{TOOL_VERSION}")
    root.geometry("900x650")
    root.resizable(True, True)

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

    tk.Label(frame, text="CSV File* :").grid(row=0, column=0, sticky="e")
    csv_entry = tk.Entry(frame, width=50)
    csv_entry.grid(row=0, column=1, padx=5)
    tk.Button(frame, text="Browse", command=browse_csv).grid(row=0, column=2)

    # -------------------------------
    # SQL input row
    # -------------------------------

    tk.Label(frame, text="SQL Script* :").grid(row=1, column=0, sticky="e", pady=5)
    sql_entry = tk.Entry(frame, width=50)
    sql_entry.grid(row=1, column=1, padx=5)
    tk.Button(frame, text="Browse", command=browse_sql).grid(row=1, column=2)

    # -------------------------------
    # Username row
    # -------------------------------

    tk.Label(frame, text="Username :").grid(row=2, column=0, sticky="e", pady=5)
    username_entry = tk.Entry(frame, width=50)
    username_entry.grid(row=2, column=1, padx=5, columnspan=2)

    # -------------------------------
    # Password row
    # -------------------------------

    tk.Label(frame, text="Password :").grid(row=3, column=0, sticky="e", pady=5)
    password_entry = tk.Entry(frame, width=50, show="*")
    password_entry.grid(row=3, column=1, padx=5, columnspan=2)

    # -------------------------------
    # PCB row
    # -------------------------------

    tk.Label(frame, text="PCB :").grid(row=4, column=0, sticky="e", pady=5)
    pcb_entry = tk.Entry(frame, width=50)
    pcb_entry.grid(row=4, column=1, padx=5, columnspan=2)

    source_mode = tk.StringVar(value="csv")
    builtin_category = tk.StringVar(value=list(BUILTIN_TARGETS.keys())[0])

    tk.Label(frame, text="Target Source:").grid(row=7, column=0, sticky="e", pady=5)

    src_frame = tk.Frame(frame)
    src_frame.grid(row=7, column=1, columnspan=2, sticky="w")

    tk.Radiobutton(src_frame, text="CSV", variable=source_mode, value="csv").pack(side="left")
    tk.Radiobutton(src_frame, text="Built-in", variable=source_mode, value="builtin").pack(side="left", padx=10)

    tk.Label(frame, text="Built-in Type:").grid(row=8, column=0, sticky="e", pady=5)
    
    # -------------------------------
    # Built-in Targets (Split View)
    # -------------------------------
    split_frame = tk.Frame(frame)
    split_frame.grid(row=9, column=0, columnspan=3, pady=10, sticky="w")

    # Left: Categories
    left_frame = tk.Frame(split_frame, bd=1, relief="groove")
    left_frame.pack(side="left", padx=5)

    tk.Label(left_frame, text="Categories").pack(anchor="w")

    category_listbox = tk.Listbox(left_frame, height=6, exportselection=False)
    category_listbox.pack()

    for cat in BUILTIN_TARGETS.keys():
        category_listbox.insert(tk.END, cat)

    category_listbox.selection_set(0)

    # Right: Targets
    right_frame = tk.Frame(split_frame, bd=1, relief="groove")
    right_frame.pack(side="left", padx=10)

    tk.Label(right_frame, text="Targets").pack(anchor="w")

    targets_container = tk.Frame(right_frame)
    targets_container.pack(anchor="w")

    # Select / Deselect buttons (current category)
    btn_frame = tk.Frame(right_frame)
    btn_frame.pack(anchor="e", pady=5)

    tk.Button(
        btn_frame,
        text="Select All",
        command=lambda: set_category_selection(category_listbox.get(category_listbox.curselection()[0]), True)
    ).pack(side="left", padx=5)

    tk.Button(
        btn_frame,
        text="Deselect All",
        command=lambda: set_category_selection(category_listbox.get(category_listbox.curselection()[0]), False)
    ).pack(side="left")

    def on_category_change(event):
        sel = category_listbox.curselection()
        if not sel:
            return
        category = category_listbox.get(sel[0])
        render_builtin_targets(category, targets_container)

    category_listbox.bind("<<ListboxSelect>>", on_category_change)

    # Initial render
    first_category = category_listbox.get(0)
    render_builtin_targets(first_category, targets_container)

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