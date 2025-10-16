# UI Component JSON Schema Documentation

## Overview

This JSON schema defines a comprehensive structure for representing UI components in a hierarchical, declarative format. It's designed to work with OpenAI's structured output API and captures all attributes necessary for building complete user interfaces.

## Schema Structure

### Core Component Properties

Every UI component must have a `type` and can include various optional properties:

```json
{
  "type": "frame",
  "name": "Component_Name",
  "layout": {...},
  "size": {...},
  "style": {...},
  "children": [...]
}
```

## Component Types

The schema supports five fundamental component types:

### 1. `frame`
A container component that can hold child components. Used for layout and grouping.

**Example:**
```json
{
  "type": "frame",
  "name": "Header_Container",
  "layout": {
    "direction": "horizontal",
    "align": "center",
    "justify": "space-between"
  },
  "children": [...]
}
```

### 2. `text`
Displays text content with typography styling.

**Example:**
```json
{
  "type": "text",
  "text": "Hello World",
  "style": {
    "fontFamily": "Inter",
    "fontWeight": 600,
    "fontSize": 16,
    "fill": "#0F172A"
  }
}
```

### 3. `icon`
Renders an icon from a specified icon set.

**Example:**
```json
{
  "type": "icon",
  "icon": "search",
  "iconSet": "lucide",
  "size": 20,
  "style": {
    "stroke": "#64748B"
  }
}
```

### 4. `rect`
A rectangular shape, often used for backgrounds or placeholders.

**Example:**
```json
{
  "type": "rect",
  "name": "Background",
  "size": {"width": "fill", "height": 200},
  "style": {
    "fill": "#F8FAFC",
    "cornerRadius": 12
  }
}
```

### 5. `ellipse`
A circular or elliptical shape.

**Example:**
```json
{
  "type": "ellipse",
  "size": {"width": 24, "height": 24},
  "style": {"fill": "#F97316"}
}
```

## Property Specifications

### Layout Object

Controls how child components are arranged within a frame.

| Property | Type | Values | Description |
|----------|------|--------|-------------|
| `direction` | string | `"horizontal"`, `"vertical"` | Layout direction |
| `align` | string | `"center"`, `"start"`, `"end"`, `"stretch"`, `"top"`, `"left"`, `"right"` | Cross-axis alignment |
| `justify` | string | `"start"`, `"center"`, `"end"`, `"space-between"`, `"space-between-right"` | Main-axis alignment |
| `gap` | number | Any number | Spacing between children |
| `padding` | object | `{top, bottom, left, right}` | Internal spacing |

**Example:**
```json
{
  "layout": {
    "direction": "vertical",
    "align": "stretch",
    "justify": "start",
    "gap": 12,
    "padding": {
      "top": 16,
      "bottom": 16,
      "left": 20,
      "right": 20
    }
  }
}
```

### Size Object

Defines component dimensions.

| Property | Type | Values | Description |
|----------|------|--------|-------------|
| `width` | number or string | Number or `"fill"`, `"hug"` | Component width |
| `height` | number or string | Number or `"fill"`, `"hug"` | Component height |

**Special Values:**
- `"fill"` - Expand to fill available space
- `"hug"` - Shrink to fit content
- Number - Fixed pixel value

**Example:**
```json
{
  "size": {
    "width": "fill",
    "height": 64
  }
}
```

### Style Object

Defines visual appearance properties.

#### Color & Fill Properties

| Property | Type | Description |
|----------|------|-------------|
| `fill` | string | Background color (hex, gradient, or empty string) |
| `stroke` | string | Border/outline color (hex) |
| `strokeWidth` | number | Border thickness in pixels |

#### Shape Properties

| Property | Type | Description |
|----------|------|-------------|
| `cornerRadius` | number | Corner rounding radius in pixels |

#### Shadow Properties

| Property | Type | Description |
|----------|------|-------------|
| `shadow` | object | Drop shadow configuration |
| `shadow.x` | number | Horizontal offset |
| `shadow.y` | number | Vertical offset |
| `shadow.blur` | number | Blur radius |
| `shadow.color` | string | Shadow color (hex with alpha) |

#### Typography Properties

| Property | Type | Description |
|----------|------|-------------|
| `fontFamily` | string | Font family name |
| `fontWeight` | number | Font weight (100-900) |
| `fontSize` | number | Font size in pixels |
| `letterSpacing` | number | Letter spacing |
| `lineHeight` | number | Line height multiplier or percentage |
| `textAlign` | string | Text alignment: `"left"`, `"center"`, `"right"` |

**Example:**
```json
{
  "style": {
    "fill": "#FFFFFF",
    "stroke": "#E5E7EB",
    "strokeWidth": 1,
    "cornerRadius": 12,
    "shadow": {
      "x": 0,
      "y": 4,
      "blur": 12,
      "color": "#00000010"
    },
    "fontFamily": "Inter",
    "fontWeight": 600,
    "fontSize": 16,
    "fill": "#0F172A"
  }
}
```

## Hierarchy & Nesting

Components can be nested using the `children` array. This creates a tree structure where parent frames contain child components.

**Example:**
```json
{
  "type": "frame",
  "name": "Card",
  "children": [
    {
      "type": "text",
      "text": "Title"
    },
    {
      "type": "frame",
      "name": "Content",
      "children": [
        {
          "type": "text",
          "text": "Description"
        }
      ]
    }
  ]
}
```

## Usage with OpenAI API

### Integration Example

```python
import openai

response_schema = {
    "type": "json_schema",
    "json_schema": {
        "name": "ui_component_structure",
        "strict": True,
        "schema": {
            # Insert the schema from the artifact here
        }
    }
}

response = openai.chat.completions.create(
    model="gpt-4o",
    messages=[
        {
            "role": "system",
            "content": "You are a UI designer that generates component structures."
        },
        {
            "role": "user",
            "content": "Create a login screen with email, password inputs and a submit button."
        }
    ],
    response_format=response_schema
)

ui_structure = response.choices[0].message.content
```

## Common Patterns

### Card Component
```json
{
  "type": "frame",
  "name": "Card",
  "style": {
    "fill": "#FFFFFF",
    "cornerRadius": 12,
    "stroke": "#E5E7EB",
    "strokeWidth": 1,
    "shadow": {
      "x": 0,
      "y": 2,
      "blur": 8,
      "color": "#00000010"
    }
  },
  "layout": {
    "direction": "vertical",
    "gap": 12,
    "padding": {"top": 16, "bottom": 16, "left": 16, "right": 16}
  }
}
```

### Button Component
```json
{
  "type": "frame",
  "name": "Button",
  "layout": {
    "direction": "horizontal",
    "align": "center",
    "justify": "center",
    "gap": 8,
    "padding": {"top": 10, "bottom": 10, "left": 16, "right": 16}
  },
  "style": {
    "fill": "#F97316",
    "cornerRadius": 10,
    "shadow": {
      "x": 0,
      "y": 2,
      "blur": 4,
      "color": "#00000012"
    }
  },
  "children": [
    {
      "type": "icon",
      "icon": "check",
      "iconSet": "lucide",
      "size": 16,
      "style": {"stroke": "#FFFFFF"}
    },
    {
      "type": "text",
      "text": "Submit",
      "style": {
        "fontFamily": "Inter",
        "fontWeight": 700,
        "fontSize": 14,
        "fill": "#FFFFFF"
      }
    }
  ]
}
```

### Navigation Bar
```json
{
  "type": "frame",
  "name": "Navigation",
  "layout": {
    "direction": "horizontal",
    "align": "center",
    "justify": "space-between",
    "padding": {"top": 12, "bottom": 12, "left": 20, "right": 20}
  },
  "size": {"width": "fill", "height": "hug"},
  "style": {
    "fill": "#FFFFFF",
    "stroke": "#E5E7EB",
    "strokeWidth": 1
  }
}
```

## Color System

The schema uses hex color codes with optional alpha channel:

- **Solid colors**: `"#0F172A"` (RGB)
- **Transparent colors**: `"#00000010"` (RGBA - last 2 digits are alpha)
- **Empty fill**: `""` (no fill)
- **Gradients**: `"linear-gradient(135deg, #A8EDEA, #7379F3)"`

## Icon Sets

Currently supported icon sets:
- `"lucide"` - Lucide Icons
- `"material"` - Material Icons

Specify both the `icon` name and `iconSet` when using icons.

## Best Practices

1. **Use meaningful names**: Always provide descriptive `name` properties for frames
2. **Consistent spacing**: Use multiples of 4 or 8 for padding and gaps
3. **Color consistency**: Use a defined color palette across your design
4. **Hierarchy**: Keep nesting shallow (3-4 levels max) for maintainability
5. **Size strategy**: Use `"fill"` and `"hug"` for responsive layouts
6. **Typography scale**: Use a consistent font size scale (12, 14, 16, 18, 20, etc.)

## Limitations

- **Strict mode**: All properties must match the schema exactly
- **No additional properties**: Cannot add custom properties beyond the schema
- **Recursive children**: Child components must follow the same schema structure
- **Icon sets**: Limited to predefined icon sets (lucide, material)

## Troubleshooting

### Common Issues

**Issue**: "Additional properties not allowed"
- **Solution**: Ensure all properties match the schema exactly. Remove any custom properties.

**Issue**: Size values not working
- **Solution**: Use only numbers or the strings `"fill"` and `"hug"` for width/height.

**Issue**: Icons not rendering
- **Solution**: Verify both `icon` and `iconSet` are specified and the icon name exists in the chosen set.

## Version Information

- **Schema Version**: 1.0
- **OpenAI API Compatibility**: Structured Outputs (GPT-4 and later)
- **Last Updated**: 2025

## Support

For issues or questions about this schema, refer to:
- OpenAI Structured Outputs documentation
- Your UI component library documentation
- Icon set documentation (Lucide, Material Icons)