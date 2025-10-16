import copy
import json

def format_schema_for_prompt(schema):
    """Format a JSON schema dict into a readable string for inclusion in LLM prompts."""
    return json.dumps(schema, indent=2)

BASE_GENERATOR_SCHEMA = {
    "type": "object",
    "properties": {
        "screens": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                            "screen_name": {"type": "string", "description": "The name of the UI screen."},
                            "sub_prompt": {"type": "string", "description": "A detailed prompt for generating this screen's content."}
                },
                "required": ["screen_name", "sub_prompt"],
                "additionalProperties": False
            }
        }
    },
    "required": ["screens"],
    "additionalProperties": False
}

BASE_COMPONENT_JSON_SCHEMA = {
      "type": "object",
      "properties": {
        "type": {
          "type": "string",
          "enum": ["frame", "text", "icon", "rect", "ellipse"],
          "description": "The type of UI component"
        },
        "name": {
          "type": "string",
          "description": "The name/identifier of the component"
        },
        "layout": {
          "type": "object",
          "properties": {
            "direction": {
              "type": "string",
              "enum": ["horizontal", "vertical"]
            },
            "align": {
              "type": "string",
              "enum": ["center", "start", "end", "stretch", "top", "left", "right"]
            },
            "justify": {
              "type": "string",
              "enum": ["start", "center", "end", "space-between", "space-between-right"]
            },
            "gap": {
              "type": "number"
            },
            "padding": {
              "type": "object",
              "properties": {
                "top": {"type": "number"},
                "bottom": {"type": "number"},
                "left": {"type": "number"},
                "right": {"type": "number"}
              },
              "required": ["top", "bottom", "left", "right"],
              "additionalProperties": False
            }
          },
          "additionalProperties": False
        },
        "size": {
          "type": "object",
          "properties": {
            "width": {
              "anyOf": [
                {"type": "number"},
                {"type": "string", "enum": ["fill", "hug"]}
              ]
            },
            "height": {
              "anyOf": [
                {"type": "number"},
                {"type": "string", "enum": ["fill", "hug"]}
              ]
            }
          },
          "required": ["width", "height"],
          "additionalProperties": False
        },
        "style": {
          "type": "object",
          "properties": {
            "fill": {"type": "string"},
            "stroke": {"type": "string"},
            "strokeWidth": {"type": "number"},
            "cornerRadius": {"type": "number"},
            "shadow": {
              "type": "object",
              "properties": {
                "x": {"type": "number"},
                "y": {"type": "number"},
                "blur": {"type": "number"},
                "color": {"type": "string"}
              },
              "required": ["x", "y", "blur", "color"],
              "additionalProperties": False
            },
            "fontFamily": {"type": "string"},
            "fontWeight": {"type": "number"},
            "fontSize": {"type": "number"},
            "letterSpacing": {"type": "number"},
            "lineHeight": {"type": "number"},
            "textAlign": {
              "type": "string",
              "enum": ["left", "center", "right"]
            }
          },
          "additionalProperties": False
        },
        "text": {
          "type": "string",
          "description": "Text content for text components"
        },
        "icon": {
          "type": "string",
          "description": "Icon name for icon components"
        },
        "iconSet": {
          "type": "string",
          "enum": ["lucide", "material"],
          "description": "Icon library to use"
        },
        "children": {
          "type": "array",
          "items": {
            "$ref": "#"
          },
          "description": "Child components nested within this component"
        }
      },
      "required": ["type"],
      "additionalProperties": False
    }

OPEN_AI_GENERATOR_SCHEMA ={
    "type": "json_schema",
    "json_schema": {
        "name": "screen_generation_response",
        "strict": True,
        "schema": BASE_GENERATOR_SCHEMA
    }
}

OPEN_AI_COMPONENT_JSON_SCHEMA = {
  "type": "json_schema",
  "json_schema": {
    "name": "ui_component_structure",
    "strict": False,
   "schema": BASE_COMPONENT_JSON_SCHEMA

  }
}


# Gemini schemas - these are modified to remove additionalProperties which Gemini doesn't support
# For the generator schema (screens), we can provide a schema since it's not recursive
def _remove_additional_properties(schema):
    """Recursively remove additionalProperties from schema for Gemini compatibility."""
    if isinstance(schema, dict):
        return {k: _remove_additional_properties(v) for k, v in schema.items() if k != 'additionalProperties'}
    elif isinstance(schema, list):
        return [_remove_additional_properties(item) for item in schema]
    return schema

GEMINI_GENERATOR_SCHEMA = _remove_additional_properties(copy.deepcopy(BASE_GENERATOR_SCHEMA))

# For component generation, we include the schema as text in the prompt instead of using response_schema
# This is because Gemini cannot handle recursive schemas ($ref: "#")
COMPONENT_JSON_SCHEMA_TEXT = format_schema_for_prompt(BASE_COMPONENT_JSON_SCHEMA)