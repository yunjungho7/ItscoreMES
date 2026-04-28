import os
import sys
import json

# Add project root to sys.path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, project_root)

# Now we can import backend.main
try:
    from backend.main import app
except ImportError:
    # Fallback if backend is not treated as a package
    sys.path.insert(0, os.path.join(project_root, 'backend'))
    from main import app

# Define output path
output_path = os.path.join(project_root, 'frontend', 'openapi.json')

with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(app.openapi(), f, indent=2, ensure_ascii=False)

print(f"OpenAPI schema extracted to {output_path}")
