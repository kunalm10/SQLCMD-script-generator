# SQLCMD Multi-Server Script Generator

## Overview

This tool generates a **multi-server SQLCMD script** from a CSV file containing server and database names.

It provides a **Windows GUI** that allows users to:
- Select a CSV file with server/database mappings
- Select a SQL script to execute
- Enter SQL username and password

The generated SQLCMD script can be executed in **SQL Server Management Studio (SSMS)** with **SQLCMD Mode enabled**.

---

## What the Tool Produces

A **timestamped SQLCMD `.sql` file** is generated for each run:

```
run_all_YYYYMMDD_HHMMSS.sql
```

This ensures outputs are not overwritten between runs.

---

## What the Tool Does

For each row in the CSV file, the tool generates a SQLCMD execution block similar to:

```sql
PRINT '--- [1] DatabaseName on ServerName ---'
:CONNECT ServerName -U $(USERNAME) -P $(PASSWORD)
USE [DatabaseName];
:r $(SCRIPT)
GO
```

All blocks are combined into a single SQLCMD script.

---

## Inputs

### 1. CSV File

The CSV file **must contain the following headers**:

```csv
server,database
```

#### Example CSV

```csv
server,database
Server_name1,Database1
Server_name2,Database2
```

- Each row represents one server/database execution
- Rows are processed in the same order as the CSV

---

### 2. SQL Script File

This is the `.sql` file that will be executed on **each server/database** using SQLCMD:

```sql
:r $(SCRIPT)
```

- The file name is user-defined
- The file can be located anywhere on disk

---

### 3. Username and Password

The GUI prompts the user to enter:
- SQL username
- SQL password

These values are written directly into the generated SQLCMD file:

```sql
:setvar USERNAME "your_username"
:setvar PASSWORD "your_password"
```

⚠️ **Security Note**  
The generated SQLCMD file contains credentials in plain text.  
Handle the output file securely and avoid committing it to source control.

---

## Output

- The output SQLCMD file is created in the **same folder as the CSV file**
- File naming format:

```
run_all_YYYYMMDD_HHMMSS.sql
```

---

## How to Use

1. Launch the application (`sqlcmd-script-generator.exe`)
2. Click **Browse** and select the CSV file
3. Click **Browse** and select the SQL script file
4. Enter **Username** and **Password**
5. Click **Generate SQLCMD Script**
6. A confirmation dialog will display the output file location

---

## Running the Generated Script

1. Open the generated `.sql` file in **SQL Server Management Studio (SSMS)**
2. Enable SQLCMD Mode:
   ```
   Query → SQLCMD Mode
   ```
3. Execute the script

---

## Version

**v1.0.0**
