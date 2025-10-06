import pandas as pd
import re
import html
from pathlib import Path

# Load CSV
csv_file = "/workspaces/parse_csv/Copy of AS new translation - Mobile Customer App.csv"
df = pd.read_csv(csv_file)

# Clean function for key names
def clean_key(expression: str) -> str:
    key = expression.strip().lower()
    key = re.sub(r"\s+", "_", key)       # spaces → underscores
    key = re.sub(r"[^a-z0-9_]", "", key) # remove invalid chars
    return key

# Languages and their Android res folder names
langs = {
    "English": "values",      # default
    "Arabic": "values-ar",
    "Kurdish": "values-ku"
}

# Output base folder
output_dir = Path("output_strings")
output_dir.mkdir(exist_ok=True)

for lang, folder in langs.items():
    folder_path = output_dir / folder
    folder_path.mkdir(parents=True, exist_ok=True)

    xml_lines = ['<?xml version="1.0" encoding="utf-8"?>', "<resources>"]

    current_feature = None
    seen_keys = set()  # ✅ track duplicate keys

    for _, row in df.iterrows():
        expr = row["Word-Expression"]

        if pd.isna(expr) or not isinstance(expr, str) or expr.strip() == "":
            continue

        # Detect feature headers (rows with no translation values)
        if (pd.isna(row.get("English")) and 
            pd.isna(row.get("Arabic")) and 
            pd.isna(row.get("Kurdish"))):
            current_feature = expr.strip()
            xml_lines.append(f"\n    <!-- {current_feature} -->")
            continue

        # Otherwise: normal string row
        key = clean_key(expr)

        # ✅ Skip duplicate keys
        if key in seen_keys:
            continue
        seen_keys.add(key)

        value = row.get(lang, "")
        if pd.isna(value) or str(value).strip() == "":
            continue  # skip missing translations

        safe_value = html.escape(str(value), quote=True)
        xml_lines.append(f'    <string name="{key}">{safe_value}</string>')

    xml_lines.append("</resources>")

    # Write to file
    with open(folder_path / "strings.xml", "w", encoding="utf-8") as f:
        f.write("\n".join(xml_lines))

print("✅ XML files generated with feature comments and duplicate keys removed in", output_dir.resolve())
