import csv
from pathlib import Path
from datetime import datetime
import sys

def get_base_dir():
    # Works for both .py and .exe
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent
    return Path(__file__).resolve().parent


def generate_sqlcmd_from_csv():
    base_dir = get_base_dir()

    csv_file = base_dir / "servers.csv"
    sql_file = base_dir / "checkConnection.sql"

    if not csv_file.exists():
        raise FileNotFoundError(f"Missing file: {csv_file.name}")
    if not sql_file.exists():
        raise FileNotFoundError(f"Missing file: {sql_file.name}")

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = base_dir / f"run_all_{timestamp}.sql"

    lines = [
        "------------------------------------------------------------",
        "-- MULTI-DATABASE SQLCMD SCRIPT",
        "-- Enable: Query > SQLCMD Mode",
        "------------------------------------------------------------",
        "",
        ':setvar USERNAME "username"',
        ':setvar PASSWORD "password"',
        f':setvar SCRIPT "{sql_file}"',
        "",
        "------------------------------------------------------------",
        "-- BEGIN EXECUTION",
        "------------------------------------------------------------",
        "",
        ""
    ]

    with csv_file.open(newline="", encoding="utf-8") as f:
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
    print(f"SUCCESS: {output_file.name}")


if __name__ == "__main__":
    try:
        generate_sqlcmd_from_csv()
    except Exception as e:
        print(f"ERROR: {e}")
        input("Press Enter to exit...")
