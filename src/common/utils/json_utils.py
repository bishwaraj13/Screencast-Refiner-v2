"""
Utility functions for JSON operations.
"""

import json
import re
from typing import Dict, Any

def load_json_from_string(json_string: str) -> Dict[str, Any]:
    """
    Parse and load JSON data from a string with support for code block markers.
    
    Args:
        json_string (str): JSON string to parse
        
    Returns:
        Dict[str, Any]: Parsed JSON data
        
    Raises:
        json.JSONDecodeError: If JSON parsing fails
    """
    json_string = json_string.strip().lstrip("```json").rstrip("```")
    pattern = r'\s"([^"]+)"\s'
    json_string = re.sub(pattern, r" \1 ", json_string)
    return json.loads(json_string)
