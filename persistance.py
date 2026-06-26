import json
import os
from typing import Dict, List, Optional

## persistant_add(portfolio name, portfolio weights as a list)
##  persistant_load(portfolio name) -> portfolio weights as a list

# Define the file name globally
DB_FILE = "matrix_storage.json"

def _initialize_db():
    """Ensures the storage file exists and contains a valid empty JSON object."""
    if not os.path.exists(DB_FILE):
        with open(DB_FILE, "w") as f:
            json.dump({}, f)

def persistent_add(name: str, int_list: List[int]):
    """Saves or updates a list of 5 integers associated with a specific name."""
    _initialize_db()
    
    # 1. Read existing data safely
    with open(DB_FILE, "r") as f:
        try:
            database = json.load(f)
        except json.JSONDecodeError:
            database = {}

    # 2. Add or overwrite the record
    database[name] = int_list

    # 3. Write back to disk with clean formatting
    with open(DB_FILE, "w") as f:
        json.dump(database, f, indent=4)

def persistent_load(name: str):
    """Safely retrieves the 5-integer list for a name. Returns None if not found."""
    _initialize_db()
    
    with open(DB_FILE, "r") as f:
        try:
            database = json.load(f)
        except json.JSONDecodeError:
            return None
            
    # Returns the list or None if the name doesn't exist
    return database.get(name)


