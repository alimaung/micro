import os

# === Configuration ===
ini_file = r"Y:\SMA\file-converter-64\TEMPLATES\16mm.TPL"  # change to your actual ini path
section = "TEMPLATE"
key = "LOGFILEPATH"
new_path = r"X:\RRD058-2021_OU_Nacharbeitspläne\.filmlogs"  # test path

def modify_ini_ansi(ini_path, section, key, new_value):
    if not os.path.isfile(ini_path):
        print(f"INI file not found: {ini_path}")
        return

    with open(ini_path, "r", encoding="utf-8", errors="ignore") as f:
        lines = f.readlines()

    in_section = False
    found = False

    for i, line in enumerate(lines):
        stripped = line.strip()

        # Detect section
        if stripped.startswith("[") and stripped.endswith("]"):
            in_section = stripped[1:-1].strip().upper() == section.upper()

        elif in_section and "=" in stripped:
            k, v = map(str.strip, stripped.split("=", 1))
            if k.upper() == key.upper():
                lines[i] = f"{key}={new_value}\n"
                found = True
                break

    if not found:
        print(f"Key '{key}' not found in section '[{section}]'.")
        return

    # Write back in ANSI encoding (Windows-1252)
    with open(ini_path, "w", encoding="cp1252", errors="replace") as f:
        f.writelines(lines)

    print(f"Modified '{key}' in section '[{section}]' to: {new_value}")

# Run the function
modify_ini_ansi(ini_file, section, key, new_path)
