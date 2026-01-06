from pathlib import Path

def generate_sqlcmd_script(
    server_db_map,
    script_path,
    output_file,
    username,
    password
):
    lines = []

    # Header
    lines.extend([
        "------------------------------------------------------------",
        "-- MULTI-DATABASE SQLCMD SCRIPT",
        "-- Enable: Query > SQLCMD Mode",
        "------------------------------------------------------------",
        "",
        f':setvar USERNAME "{username}"',
        f':setvar PASSWORD "{password}"',
        f':setvar SCRIPT "{script_path}"',
        "",
        "------------------------------------------------------------",
        "-- BEGIN EXECUTION",
        "------------------------------------------------------------",
        "",
        ""
    ])

    # Body
    for i, (server, database) in enumerate(server_db_map, start=1):
        lines.extend([
            f"PRINT '--- [{i}] {database} on {server} ---'",
            f":CONNECT {server} -U $(USERNAME) -P $(PASSWORD)",
            f"USE [{database}];",
            ":r $(SCRIPT)",
            "GO",
            ""
        ])

    Path(output_file).write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    server_db_map = [
        ("server1", "database1"),
        ("server2", "database2"),
        ("server3", "database3"),
        ("server4", "database4"),
        ("server5", "database5"),
    ]

    generate_sqlcmd_script(
        server_db_map=server_db_map,
        script_path=r"C:\sqlcmd-script-generator\checkConnection.sql",
        output_file=r"C:\sqlcmd-script-generator\run_all.sql",
        username="username",
        password="password"
    )

    print("SQLCMD script generated successfully.")