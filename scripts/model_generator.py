import subprocess
import urllib.request
from pathlib import Path

def main():
    schemas = [
        "https://raw.githubusercontent.com/prusa3d/OpenPrintTag/main/utils/schema/opt_json.schema.json",
        "https://raw.githubusercontent.com/prusa3d/OpenPrintTag/main/utils/schema/fields.schema.json",
        "https://raw.githubusercontent.com/prusa3d/OpenPrintTag/main/utils/schema/field_types.schema.json",
    ]
    
    # Download schemas
    schema_dir = Path("temp_schemas")
    schema_dir.mkdir(exist_ok=True)
    
    for url in schemas:
        filename = url.split("/")[-1]
        urllib.request.urlretrieve(url, schema_dir / filename)
    
    # Generate models
    models_dir = Path("src/models")
    models_dir.mkdir(parents=True, exist_ok=True)
    
    subprocess.run([
        "datamodel-codegen",
        "--input", str(schema_dir / "opt_json.schema.json"),
        "--output", str(models_dir),
        "--output-model-type", "pydantic_v2.BaseModel"
    ])

if __name__ == "__main__":
    main()