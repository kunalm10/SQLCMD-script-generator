import csv
from pathlib import Path
from datetime import datetime
import tkinter as tk
from tkinter import filedialog, messagebox

TOOL_NAME = "SQLCMD Multi-Server Script Generator"
TOOL_VERSION = "1.0.0"


def generate_sqlcmd(csv_path: Path, sql_script_path: Path):
    output_dir = csv_path.parent
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = output_dir / f"run_all_{timestamp}.sql"

    lines = [
        "------------------------------------------------------------",
        "-- MULTI-DATABASE SQLCMD SCRIPT",
        "-- Enable: Query > SQLCMD Mode",
        "------------------------------------------------------------",
        "",
        ':setvar USERNAME "username"',
        ':setvar PASSWORD "password"',
        f':setvar SCRIPT "{sql_script_path}"',
        "",
        "------------------------------------------------------------",
        "-- BEGIN EXECUTION",
        "------------------------------------------------------------",
        "",
        ""
    ]

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

    output_file.write_text("\n".join(lines), encoding="utf-8")
    return output_file


def browse_csv():
    path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
    if path:
        csv_entry.delete(0, tk.END)
        csv_entry.insert(0, path)


def browse_sql():
    path = filedialog.askopenfilename(filetypes=[("SQL Files", "*.sql")])
    if path:
        sql_entry.delete(0, tk.END)
        sql_entry.insert(0, path)


def run_tool():
    try:
        csv_path = Path(csv_entry.get())
        sql_path = Path(sql_entry.get())

        if not csv_path.exists() or not sql_path.exists():
            raise FileNotFoundError("CSV or SQL file not found.")

        output = generate_sqlcmd(csv_path, sql_path)
        messagebox.showinfo("Success", f"Generated:\n{output}")

    except Exception as e:
        messagebox.showerror("Error", str(e))


# GUI
root = tk.Tk()
root.title(f"{TOOL_NAME} v{TOOL_VERSION}")
root.geometry("600x220")
root.resizable(False, False)

tk.Label(root, text=TOOL_NAME, font=("Segoe UI", 12, "bold")).pack(pady=5)
tk.Label(root, text=f"Version {TOOL_VERSION}").pack()

frame = tk.Frame(root)
frame.pack(pady=15)

tk.Label(frame, text="CSV File:").grid(row=0, column=0, sticky="e")
csv_entry = tk.Entry(frame, width=50)
csv_entry.grid(row=0, column=1, padx=5)
tk.Button(frame, text="Browse", command=browse_csv).grid(row=0, column=2)

tk.Label(frame, text="SQL Script:").grid(row=1, column=0, sticky="e", pady=5)
sql_entry = tk.Entry(frame, width=50)
sql_entry.grid(row=1, column=1, padx=5)
tk.Button(frame, text="Browse", command=browse_sql).grid(row=1, column=2)

tk.Button(root, text="Generate SQLCMD Script", command=run_tool, width=30)\
    .pack(pady=15)

root.mainloop()
