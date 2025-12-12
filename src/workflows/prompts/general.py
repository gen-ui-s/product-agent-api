# -----------------------------------------------------------------------------
# FULL JSON → Design rules doc (from AI Genuis Documentation)
# -----------------------------------------------------------------------------

JSON_RULES_SNIPPET = """

<json_plugin_rules>
# AI Genuis Documentation

# JSON → Design Plugin — Node Types Reference

> Purpose: teach an AI agent to author valid JSON for the JSON-to-Design plugin. This document defines nodes, color & gradients, style, layout, sizing & constraints, absolute positioning, effects (incl. Texture), patterns, validation, and a parameter index. All examples are copy-paste valid.
> 

---

## 1) Conventions & Core Rules

- **Every node** needs: `type` and `size` with `width` & `height` (`number` in px or `"hug"` or `"fill"`).
- **Colors accepted**: `#RRGGBB`, `#RRGGBBAA`, `#RGB`, `#RGBA`, `rgb(...)`, `rgba(...)`, `hsl(...)`, `hsla(...)`. Prefer hex.
- **Gradients** allowed for `style.fill` & `style.stroke`:
    - CSS strings: `linear-gradient(...)`, `radial-gradient(...)`, `conic-gradient(...)` (aka `angular-gradient(...)`), `diamond-gradient(...)`.
    - Object form: `{ "type": "gradient", "gradientType": "linear"|"radial", "angle"?: number, "stops": [{ "color", "position" }] }`.
    - The plugin normalizes hex stops to `#RRGGBBAA` internally for validation.
- **Effects** live under `style.effects`. (Legacy: `style.shadow` = single drop shadow.)
- **Auto‑layout** is default on `frame`. Buttons **must** be `type: "frame"`.
- **Icon color**: Lucide uses **stroke**, Material uses **fill**.
- Mobile devices should have a status bar and a nav bar by default with all icons needed
- Meet **`(WCAG) 2.2` accessibility standards**
- ONLY Use `gemini-2.5-flash-image` for image generation
- Don’t use `texture` with `glass`
- Don’t use percentages with line height
- **Map sizes**: For `map` nodes, `size.width` and `size.height` MUST be fixed numeric pixel values (no "hug" or "fill") to avoid loss of resolution in the rendered map.
- **Absolute positioning sizing**: Any node that uses `position.type` = "absolute" MUST NOT use "fill" for `size.width` or `size.height`; these must be either "hug" or explicit numeric dimensions in pixels.
- **All objects and frames must have width and height values. Either fill, hug or a fixed number of pixels.**
---

# 1.5) Top-Level Structure & Node Types

- All generations MUST start with a **top-level `screens` array**.
- Each item in `screens` represents a single screen and wraps its root `node`.
- For now, every generation MUST begin with this exact structure:

```json
{
  "screens": [
    {
      "screen_id": "discover",
      "screen_name": "Discover",
      "screen_type": "home",
      "node": {
        // Root node for the Discover screen (usually a frame) goes here
      }
    }
  ]
}
```

### Example with two or more screens

```json
{
  "screens": [
    {
      "screen_id": "discover",
      "screen_name": "Discover",
      "screen_type": "home",
      "node": {
        "type": "frame",
         // screen design goes here
          },
          {
        "type": "frame",
            // screen design goes here
          }
          }
  ]
}
```

- Additional screens (if any) MUST be appended as extra objects in the same screens array.
- The node field inside each screen uses the node types defined below (frame, rect, ellipse, text, etc.).
- The root node for a screen is almost always a frame that matches the device size.

```
---

# 2) Node Types

Supported node types: `frame`, `rect|rectangle`, `ellipse|circle`, `text`, `icon`, `line`, `image` (URL or Gemini), `map`.

## 2.1) `frame`

**Purpose:** containers, sections, lists, **buttons** (buttons should be frames)

**Fields**

- `type`: `"frame"`
- `name`: string
- `size`: `{ width: number|"hug"|"fill", height: number|"hug"|"fill", minWidth?: number, maxWidth?: number, minHeight?: number, maxHeight?: number }`
- `style`: `{ fill?: color|gradient, fillOpacity?: number, stroke?: color|gradient, strokeOpacity?: number, strokeWidth?: number, strokeAlign?: "inside"|"center"|"outside", cornerRadius?: number, opacity?: number, effects?: object }`
- `layout`: `{`
    - `direction: "vertical"|"horizontal"|"row",`
    - `wrap?: true|false|"wrap"|"no-wrap",`
    - `gap?: number,`
    - `rowGap?: number,`
    - `columnGap?: number,`
    - `padding?: number|{top,right,bottom,left},`
    - `align?: "top-left"|"top-center"|"top-right"|"left"|"center"|"right"|"bottom-left"|"bottom-center"|"bottom-right"|"top"|"bottom",`
    - `justify?: "space-between"|"space-between-left"|"space-between-center"|"space-between-right" 
    }`
- `children`: `SchemaNode[]`
- `position` (absolute inside auto-layout or root): `{ type: "absolute", x: number, y: number, horizontal?: "MIN"|"CENTER"|"MAX"|"STRETCH", vertical?: "MIN"|"CENTER"|"MAX"|"STRETCH" }`

**Example**

```json
{
  "type": "frame",
  "name": "Card",
  "size": { "width": 344, "height": "hug", "minHeight": 120 },
  "layout": { "direction": "vertical", "gap": 12, "padding": 16, "align": "top-left" },
  "style": { "fill": "#0B1220", "cornerRadius": 16 },
  "children": [
    { "type": "text", "text": "Title", "size": { "width": "hug", "height": "hug" },
      "style": { "fontFamily": "Inter", "fontWeight": 700, "fontSize": 18, "fill": "#FFFFFF" } },
    { "type": "text", "text": "Body text…", "size": { "width": "fill", "height": "hug" },
      "style": { "fontFamily": "Inter", "fontWeight": 400, "fontSize": 14, "fill": "#9CA3AF" } }
  ]
}
```

---

## 2.2) `rect` (alias `rectangle`)

**Purpose:** boxes, dividers, backgrounds

**Fields**

- `type`: `"rect"` or `"rectangle"`
- `name`, `size`, `style`, `position` (same shape as frame)

**Example**

```json
{
  "type": "rect",
  "name": "Divider",
  "size": { "width": "fill", "height": 1 },
  "style": { "fill": "none", "stroke": "#FFFFFF22", "strokeWidth": 1, "strokeAlign": "inside" }
}
```

---

## 2.3) `ellipse` (alias `circle`)

**Purpose:** avatars, status dots, circular shapes

**Fields**

- `type`: `"ellipse"` or `"circle"`
- `name`, `size` (numbers), `style`, `position`

**Example**

```json
{
  "type": "ellipse",
  "name": "Status",
  "size": { "width": 10, "height": 10 },
  "style": { "fill": "#22C55E" }
}
```

---

## 2.4) `text`

**Purpose:** typography

**Fields**

- `type`: `"text"`
- `name`: string
- `text`: string
- `size`: `{ width: number|"hug"|"fill", height: number|"hug" }`
- `style`: `{ fontFamily: string, fontWeight: number(100..900), fontSize: number, fill: color, textAlign?: "left"|"center"|"right"|"justified", textAlignVertical?: "top"|"middle"|"center"|"bottom", lineHeight?: number|string|"auto", letterSpacing?: number }`
- `position` (optional)

**Line height rules**

- `"auto"` → Figma line height set to `AUTO`
- `number` (e.g. `24`) or numeric string (e.g. `"24"`) → treated as **pixels**
- string with `%` (e.g. `"120%"`) → treated as **percentage**

**Vertical alignment**

- `textAlignVertical` maps to Figma `textAlignVertical`:
    - `"top"` → `TOP`
    - `"middle"` / `"center"` → `CENTER`
    - `"bottom"` → `BOTTOM`

**Example**

```json
{
  "type": "text",
  "name": "Headline",
  "text": "Welcome back",
  "size": { "width": "hug", "height": "hug" },
  "style": {
    "fontFamily": "Inter",
    "fontWeight": 700,
    "fontSize": 24,
    "fill": "#FFFFFF",
    "textAlign": "center",
    "textAlignVertical": "middle",
    "lineHeight": "120",
    "letterSpacing": 0
  }
}
```

---

## 2.5) `icon`

**Purpose:** vector icons via CDN or embedded fallback

**Fields**

- `type`: `"icon"`
- `iconSet`: `"lucide"|"material"`
- `icon`: string (e.g., `"star"`, `"shopping_cart"`)
- `size`: number | `{ width, height }`
- `style`: `{ stroke?: color, fill?: color }` *(Lucide uses stroke; Material uses fill)*
- `name`, `position` (optional)

**Examples**

```json
{ "type": "icon", "iconSet": "lucide",   "icon": "star",          "size": 20, "style": { "stroke": "#FFFFFF" } }
```

```json
{ "type": "icon", "iconSet": "material", "icon": "shopping_cart", "size": 24, "style": { "fill": "#111827" } }
```

---

## 2.6) `line`

**Purpose:** rules and separators

**Fields**

- `type`: `"line"`
- `name`: string
- `length` (alias `width`): number
- `rotation`?: number (degrees)
- `style`: `{ stroke: color|gradient, strokeWidth: number }`
- `position` (optional)

**Example**

```json
{
  "type": "line",
  "name": "Rule",
  "length": 280,
  "style": { "stroke": "#FFFFFF22", "strokeWidth": 1 }
}
```

---

## 2.7) `image`

**Purpose:** raster image fills (no Unsplash in this doc)

**Sources (priority)**

1. `url`: string
2. Gemini native generation: `model` + `prompt` (optional `aspectRatio` like `"4:3"`, `"16:9"`; auto-snaps if omitted)

**Fields**

- `type`: `"image"`
- `name`: string
- `model`?: string (`"gemini-2.5-flash-image"`) (*Can not use any other model)
- `prompt`?: string
- `aspectRatio`?: `"1:1"|"2:3"|"3:2"|"3:4"|"4:3"|"4:5"|"5:4"|"9:16"|"16:9"|"21:9"`
- `size`: `{ width: number, height: number }`
- `scaleMode`: `"fill"|"fit"`
- `style`: `{ cornerRadius?: number }`
- `position` (optional)

**Examples**

```json
{
  "type": "image",
  "name": "AI Dish",
  "model": "gemini-2.5-flash-image",
  "prompt": "Plated salmon with microgreens, studio lighting, shallow depth of field",
  "size": { "width": 320, "height": 240 },
  "scaleMode": "fit",
  "style": { "cornerRadius": 12 }
}
```

---

## 2.8) `map`

**Purpose:** Google Static Map rendered as an image fill

**Fields**

- Center (one of): `lat`+`lng` | `address` | `center`(string)
- View: `zoom`(number), `scale`(1|2), `maptype`(`"roadmap"|"satellite"|"hybrid"|"terrain"`)
- `markers`: array of string **or** `{ lat, lng }` **or** `{ address, color?, label? }`
- `path`: `{ color?: string, weight?: number, fillcolor?: string, points: [{ lat, lng }, ...] }`
- `styles`: array of `{ feature?: string, element?: string, rules?: [{ anyKey: anyVal }, ...] }`
- `size`: `{ width: number, height: number }`
- `scaleMode`: `"fill"|"fit"`
- `style`: `{ cornerRadius?: number }`
- `position` (optional)

**Example**

Light Mode

```json
{
  "type": "map",
  "name": "Route A → B (Light)",
  "size": { "width": 640, "height": 360 },
  "scaleMode": "fill",
  "lat": 42.34805,
  "lng": -71.08785,
  "zoom": 13,
  "scale": 2,
  "maptype": "roadmap",

  "markers": [
    { "address": "560 Boylston St, Boston MA", "color": "red", "label": "A" },
    { "address": "4 Jersey St, Boston MA 02215", "color": "blue", "label": "B" }
  ],

  "path": {
    "color": "0x2563EB",
    "weight": 5,
    "points": [
      { "lat": 42.3494, "lng": -71.0785 },
      { "lat": 42.3467, "lng": -71.0972 }
    ]
  },

  "styles": [
    { "feature": "all", "element": "geometry", "rules": [ { "color": "0xF8FAFC" } ] },
    { "feature": "all", "element": "labels.text.fill", "rules": [ { "color": "0x334155" } ] },
    { "feature": "all", "element": "labels.text.stroke", "rules": [ { "color": "0xFFFFFF" } ] },

    { "feature": "road", "element": "geometry", "rules": [ { "color": "0xE5E7EB" } ] },
    { "feature": "road", "element": "labels.text.fill", "rules": [ { "color": "0x475569" } ] },
    { "feature": "road.local", "element": "labels", "rules": [ { "visibility": "simplified" } ] },

    { "feature": "poi", "element": "geometry", "rules": [ { "color": "0xFFFFFF" } ] },
    { "feature": "poi", "element": "labels.text.fill", "rules": [ { "color": "0x64748B" } ] },
    { "feature": "poi.business", "element": "labels", "rules": [ { "visibility": "off" } ] },

    { "feature": "transit", "element": "labels.icon", "rules": [ { "visibility": "off" } ] },

    { "feature": "water", "element": "geometry", "rules": [ { "color": "0xC7E5FF" } ] },
    { "feature": "water", "element": "labels.text.fill", "rules": [ { "color": "0x2563EB" } ] }
  ],

  "style": { "cornerRadius": 12 }
}
```

Dark Mode

```json
{
  "type": "map",
  "name": "Route A → B (Dark)",
  "size": { "width": 640, "height": 360 },
  "scaleMode": "fill",
  "lat": 42.34805,
  "lng": -71.08785,
  "zoom": 13,
  "scale": 2,
  "maptype": "roadmap",

  "markers": [
    { "address": "560 Boylston St, Boston MA", "color": "red", "label": "A" },
    { "address": "4 Jersey St, Boston MA 02215", "color": "blue", "label": "B" }
  ],

  "path": {
    "color": "0x60A5FA",
    "weight": 5,
    "points": [
      { "lat": 42.3494, "lng": -71.0785 },
      { "lat": 42.3467, "lng": -71.0972 }
    ]
  },

  "styles": [
    { "feature": "all", "element": "geometry", "rules": [ { "color": "0x0B0F1C" } ] },
    { "feature": "all", "element": "labels.text.fill", "rules": [ { "color": "0x94A3B8" } ] },
    { "feature": "all", "element": "labels.text.stroke", "rules": [ { "color": "0x0B0F1C" } ] },

    { "feature": "road", "element": "geometry", "rules": [ { "color": "0x111827" } ] },
    { "feature": "road", "element": "labels.text.fill", "rules": [ { "color": "0xCBD5E1" } ] },
    { "feature": "road.local", "element": "labels", "rules": [ { "visibility": "simplified" } ] },

    { "feature": "poi", "element": "geometry", "rules": [ { "color": "0x0F172A" } ] },
    { "feature": "poi", "element": "labels.text.fill", "rules": [ { "color": "0x93C5FD" } ] },
    { "feature": "poi.business", "element": "labels", "rules": [ { "visibility": "off" } ] },

    { "feature": "transit", "element": "labels.icon", "rules": [ { "visibility": "off" } ] },

    { "feature": "water", "element": "geometry", "rules": [ { "color": "0x0A1929" } ] },
    { "feature": "water", "element": "labels.text.fill", "rules": [ { "color": "0x60A5FA" } ] }
  ],

  "style": { "cornerRadius": 12 }
}
```

---

## 3) Colors & Gradients

**Solid**

```json
{ "style": { "fill": "#111827" } }
```

**Linear**

```json
{ "style": { "fill": "linear-gradient(135deg, #667eea, #764ba2)" } }
```

**Radial**

```json
{ "style": { "fill": "radial-gradient(circle, #0555FFFF 0%, #00000000 100%)" } }
```

**Conic/Angular**

```json
{ "style": { "fill": "conic-gradient(from 45deg, #FFFFFF, #000000)" } }
```

**Diamond**

```json
{ "style": { "fill": "diamond-gradient(#FFFFFF 0%, #000000 100%)" } }
```

**Object form**

```json
{
  "style": {
    "fill": {
      "type": "gradient",
      "gradientType": "linear",
      "angle": 90,
      "stops": [ { "color": "#0555FFFF", "position": 0 }, { "color": "#00000000", "position": 1 } ]
    }
  }
}
```

---

## 4) Style (fills, strokes, corners)

```json
{
  "style": {
    "fill": "#0B1220",
    "fillOpacity": 1,
    "stroke": "linear-gradient(180deg, #FFFFFF, #FFFFFF00)",
    "strokeOpacity": 0.6,
    "strokeWidth": 2,
    "strokeAlign": "inside",
    "cornerRadius": 12
  }
}
```

- `strokeAlign`: `"inside" | "center" | "outside"`
- Per-corner: `topLeftRadius`, `topRightRadius`, `bottomRightRadius`, `bottomLeftRadius`

---

## 5) Layout (Auto-layout for `frame`)

```json
"layout": {
  "direction": "vertical",
  "wrap": true,
  "gap": 12,
  "rowGap": 12,
  "columnGap": 12,
  "padding": { "top": 12, "right": 12, "bottom": 12, "left": 12 },
  "align": "top-left",
  "justify": "space-between"
}
```

Child override (`align`): `"top" | "center" | "bottom" | "left" | "right" | "stretch"`

**Wrapping grid**

```json
{
  "type": "frame",
  "size": { "width": 320, "height": "hug" },
  "layout": { "direction": "horizontal", "wrap": true, "columnGap": 12, "rowGap": 12, "padding": 12 },
  "children": [
    { "type": "rect", "size": { "width": 96, "height": 72 }, "style": { "fill": "#1F2937", "cornerRadius": 8 } },
    { "type": "rect", "size": { "width": 96, "height": 72 }, "style": { "fill": "#1F2937", "cornerRadius": 8 } },
    { "type": "rect", "size": { "width": 96, "height": 72 }, "style": { "fill": "#1F2937", "cornerRadius": 8 } }
  ]
}
```

---

## 6) Sizing & Constraints

```json
"size": {
  "width": 320,              // or "hug" or "fill"
  "height": "hug",
  "minWidth": 200,
  "maxWidth": 480,
  "minHeight": 40,
  "maxHeight": 240
}
```

- In auto-layout parents, `"fill"` maps to `layoutGrow`/`layoutAlign` depending on axis.
- Min/max are applied on nodes that support them (frames, etc.).

---

## 7) Positioning (Absolute within auto-layout)

Use when a child needs to float within an auto-layout parent.

```json
"position": {
  "type": "absolute",
  "x": 16, "y": 12,
  "horizontal": "MIN",  // MIN|CENTER|MAX|STRETCH
  "vertical": "MIN",    // MIN|CENTER|MAX|STRETCH
  "left": 16            // pin-style inference also supported (left/right/top/bottom)
}
```

Shorthand:

```json
"absolute": { "x": 16, "y": 12 }
```

**Example — absolute badge**

```json
{
  "type": "frame",
  "size": { "width": 320, "height": 96 },
  "layout": { "direction": "vertical", "padding": 16 },
  "children": [
    {
      "type": "rect",
      "name": "Badge",
      "size": { "width": 40, "height": 24 },
      "style": { "fill": "#111827", "cornerRadius": 6 },
      "position": { "type": "absolute", "x": 16, "y": 12, "horizontal": "MIN", "vertical": "MIN" }
    }
  ]
}
```

---

## 8) Effects (Complete, incl. Texture)

Place under `style.effects`. **Engine order**: Drop Shadow → Inner Shadow → Layer Blur → Background Blur → Glass → Texture → Noise → (legacy shadow).

### 8.1 Drop Shadow

```json
"effects": {
  "dropShadow": {
    "x": 0, "y": 8, "blur": 24, "opacity": 0.18, "color": "#000000",
    "spread": 1, "blendMode": "normal", "showShadowBehindNode": false, "visible": true
  }
}
```

### 8.2 Inner Shadow

```json
"effects": {
  "innerShadow": { "x": 0, "y": 2, "blur": 8, "opacity": 0.25, "color": "#000000", "blendMode": "multiply" }
}
```

### 8.3 Layer Blur

```json
"effects": { "layerBlur": { "radius": 12 } }
```

### 8.4 Background Blur

```json
"effects": { "backgroundBlur": { "radius": 22 } }
```

> If glass is present, the plugin removes backgroundBlur to avoid conflicts.
> 

### 8.5 Glass (frame-like only)

```json
"effects": {
  "glass": { "lightIntensity": 0.85, "lightAngle": 60, "refraction": 0.7, "depth": 12, "dispersion": 0.12, "radius": 12, "visible": true }
}
```

### 8.6 Noise (MONOTONE / DUOTONE)

**Monotone**

```json
"effects": { "noise": { "noiseType": "MONOTONE", "color": "#FFFFFF", "opacity": 0.35, "noiseSize": 3, "density": 0.55 } }
```

**Duotone**

```json
"effects": { "noise": { "noiseType": "DUOTONE", "color1": "#000000", "opacity1": 0.35, "color2": "#FFFFFF", "opacity2": 0.35, "size": 2, "density": 0.5 } }
```

### 8.7 Texture

Non-directional surface texture **distinct from `noise`**. Authored via `style.effects.texture`. The engine outputs a dedicated `{ "type": "TEXTURE", ... }` effect internally.

```json
"effects": {
  "texture": {
    "noiseSize": 2,        // alias: size; >=1 (default 2)
    "radius": 4,           // aliases: edge, edgeRadius; >=0 (default 4)
    "clipToShape": true,   // alias: clip; default true
    "visible": true
  }
}
```

**Fine texture alias example**

```json
"effects": { "texture": { "size": 1, "edge": 2, "clip": true } }
```

**Combined pattern**

```json
{
  "type": "frame",
  "size": { "width": 344, "height": "hug" },
  "layout": { "direction": "vertical", "gap": 12, "padding": 16 },
  "style": {
    "fill": "#FFFFFF0F",
    "cornerRadius": 16,
    "effects": {
      "glass": { "lightIntensity": 0.8, "lightAngle": 48, "refraction": 0.65, "depth": 10, "dispersion": 0.12, "radius": 12 },
      "texture": { "noiseSize": 2, "radius": 3, "clipToShape": true },
      "noise": { "noiseType": "MONOTONE", "color": "#FFFFFF", "opacity": 0.18, "size": 2, "density": 0.5 }
    }
  },
  "children": [
    { "type": "text", "text": "Now Playing", "size": { "width": "hug", "height": "hug" },
      "style": { "fontFamily": "Inter", "fontWeight": 700, "fontSize": 16, "fill": "#FFFFFF" } },
    { "type": "text", "text": "Ambient Dreams — Lofi Set", "size": { "width": "hug", "height": "hug" },
      "style": { "fontFamily": "Inter", "fontWeight": 400, "fontSize": 13, "fill": "#E5E7EB" } }
  ]
}
```

---

## 9) Patterns (Buttons, Cards, Lists)

### Button (buttons **must** be frames)

```json
{
  "type": "frame",
  "name": "Primary Button",
  "size": { "width": "hug", "height": "hug" },
  "layout": { "direction": "horizontal", "gap": 8, "padding": 14, "align": "center" },
  "style": {
    "fill": "#111827",
    "cornerRadius": 12,
    "effects": {
      "dropShadow": { "x": 0, "y": 6, "blur": 18, "spread": 1, "opacity": 0.22, "color": "#000000" },
      "texture": { "noiseSize": 2, "radius": 3, "clipToShape": true }
    }
  },
  "children": [
    { "type": "icon", "iconSet": "material", "icon": "shopping_cart", "size": 20, "style": { "fill": "#FFFFFF" } },
    { "type": "text", "text": "Add to Cart", "size": { "width": "hug", "height": "hug" },
      "style": { "fontFamily": "Inter", "fontWeight": 600, "fontSize": 14, "fill": "#FFFFFF" } }
  ]
}
```

### Card

Use the frame example from §2.1; add list items as children with `wrap` if needed.

### List Item (with icon + text)

```json
{
  "type": "frame",
  "size": { "width": "fill", "height": "hug" },
  "layout": { "direction": "horizontal", "gap": 12, "padding": 12, "align": "center" },
  "children": [
    { "type": "icon", "iconSet": "lucide", "icon": "calendar", "size": 20, "style": { "stroke": "#E5E7EB" } },
    { "type": "text", "text": "Meeting at 2:30 PM", "size": { "width": "hug", "height": "hug" },
      "style": { "fontFamily": "Inter", "fontWeight": 500, "fontSize": 14, "fill": "#FFFFFF" } }
  ]
}
```

---

## 10) Validation & Troubleshooting

**Checklist**

- Each node has `type` **and** `size` (`number` or `"hug"`/`"fill"`).
- Colors are valid hex or supported CSS. For gradients, ensure stops resolve to colors with alpha as needed.
- Effects are under `style.effects` with exact keys; `opacity` is `0..1`.
- Spread on frames needs a visible fill and `clipsContent=true`. Rects/Ellipses support spread natively.
- Avoid pairing `backgroundBlur` with `glass` (engine removes the blur when glass is present).
- Mobile devices should have a status bar and a nav bar by default with all icons needed
- Meet **`(WCAG) 2.2` accessibility standards**
- ONLY Use `gemini-2.5-flash-image` for image generation
- Don’t use `texture` with `glass`

**Common errors & fixes**

- *“Required value missing at [0].gradientStops[0].color.a”*: ensure gradient stop colors normalize to `#RRGGBBAA` or provide `fillOpacity`/`strokeOpacity`. The engine auto-normalizes, but malformed strings can fail; use the object form if needed.
- *Blend mode invalid*: use one of `NORMAL, MULTIPLY, SCREEN, OVERLAY, DARKEN, LIGHTEN, COLOR_DODGE, COLOR_BURN, HARD_LIGHT, SOFT_LIGHT, DIFFERENCE, EXCLUSION, HUE, SATURATION, COLOR, LUMINOSITY`.
- *Shadow spread not visible on frames*: add a tiny visible fill (engine tries this) and set `clipsContent=true` on the frame; or use a rectangle for guaranteed spread support.
- *Icons the wrong color*: Lucide uses `stroke`; Material uses `fill`.
- *Text looks italic with non-400 weight*: the plugin loads the closest available style; provide `fontWeight` and `fontFamily` (e.g., Inter) to reduce fallback surprises.
</json_plugin_rules>
"""


# -----------------------------------------------------------------------------
# Laws of UX snippet (actionable)
# -----------------------------------------------------------------------------

UX_LAWS_SNIPPET = """
<ux_laws>
You must apply the following UX laws, adapted from the Laws of UX collection, when designing layouts, interactions, grouping, and hierarchy. These are design constraints, not suggestions.

For each screen you generate:
- Use these laws to guide choices about structure, number of options, grouping, navigation, visual hierarchy, and feedback.
- When there is a conflict, prioritize:
  1) Clarity of task completion,
  2) Reduced cognitive load,
  3) Aesthetics.

1) Aesthetic–Usability Effect
- People are more forgiving of minor usability issues if the design looks polished.
- Application: Use clean, consistent visual language (spacing, typography, color use). Make the layout feel intentional and cohesive, but never sacrifice clarity or contrast for decoration.

2) Choice Overload
- Too many options at once overwhelm users.
- Application: Limit the number of primary choices per screen. Use filters, tabs, grouping, and “See more” patterns instead of dumping large sets of options all at once.

3) Chunking
- Grouping information into small, meaningful chunks improves understanding and recall.
- Application: Break forms, lists, and settings into clearly labeled sections. Use subheaders and spacing to visually separate logical groups.

4) Cognitive Bias (general)
- Users rely on mental shortcuts, not purely rational analysis.
- Application: Use defaults and recommendations to reduce effort. Highlight safe or recommended options. Avoid manipulative patterns or dark patterns.

5) Cognitive Load
- The more mental effort required, the harder the interface is to use.
- Application: Avoid dense layouts and unnecessary details. Use concise copy. Show only the information needed to complete the current task.

6) Doherty Threshold
- Interactions feel smooth when response time is under ~400ms or clearly acknowledged.
- Application: Represent quick feedback in the UI: loading indicators, skeleton states, button “loading” states, and optimistic UI where appropriate.

7) Fitts’s Law
- Target acquisition time depends on target size and distance.
- Application: Make primary actions large and easy to hit. Avoid tiny tap targets. Place critical actions where thumbs/cursors naturally rest.

8) Flow
- Smooth, focused experiences help users stay engaged.
- Application: Avoid unnecessary модals, interruptions, and context switches. Keep key flows linear and predictable.

9) Goal–Gradient Effect
- Users accelerate their behavior as they feel closer to a goal.
- Application: Show progress indicators (steps, completion bars, checklists). Make each step’s completion feel rewarding and visible.

10) Hick’s Law
- Decision time increases with number and complexity of choices.
- Application: Limit visible choices. Order options by importance. Use defaults and recommended options so users can decide quickly.

11) Jakob’s Law
- Users expect your product to behave like others they know.
- Application: Reuse established patterns (top nav, bottom nav on mobile, standard icons, search placement, profile menu conventions). Avoid reinventing basic patterns.

12) Law of Common Region
- Elements inside the same visual container are perceived as related.
- Application: Use cards, panels, and bordered sections to group related content and controls. Do not mix unrelated items in one visual container.

13) Law of Proximity
- Elements close together are perceived as related.
- Application: Keep labels close to inputs, actions close to the content they affect, and separate unrelated groups with sufficient spacing.

14) Law of Prägnanz
- People prefer simple, stable interpretations of complex arrangements.
- Application: Simplify composition, avoid unnecessary visual complexity, and ensure hierarchy is clear at a glance.

15) Law of Similarity
- Similar-looking elements are perceived as having similar roles.
- Application: Style all primary buttons consistently; all secondary actions consistently; and differentiating destructive actions visually. Never give identical styles to elements with different importance.

16) Law of Uniform Connectedness
- Connected elements are perceived as related more strongly than unconnected ones.
- Application: Use connecting lines, shared backgrounds, or container frames to show relationships (steps in a process, items within a group, filter chips).

17) Mental Model
- Users build internal models of how your system works.
- Application: Use domain language and familiar concepts. Avoid exposing internal implementation details. Align labels and navigation with how users think about the task.

18) Miller’s Law & Working Memory
- People can hold only a few items in working memory at once.
- Application: Don’t expect users to remember information across screens. Keep key values and selections visible (summaries, sticky panels, bread crumbs).

19) Occam’s Razor
- When multiple designs work, the simplest one is best.
- Application: Prefer simpler layouts and flows. Remove decorative or redundant elements that don’t serve comprehension or task completion.

20) Paradox of the Active User
- Users often skip instructions and dive in.
- Application: Make the interface learnable-by-doing: good empty states, inline hints, contextual guidance instead of long upfront tutorials.

21) Pareto Principle (80/20 Rule)
- A minority of features usually generates most of the value.
- Application: Emphasize the top ~20% of features and actions that deliver ~80% of value. De-emphasize rarely used options.

22) Parkinson’s Law
- Work tends to expand to fill available time.
- Application: Keep flows efficient and time-bounded. Use microcopy (“Takes less than 2 minutes”) and progress indicators to set expectations.

23) Peak–End Rule
- People judge an experience by its most intense moment and its ending.
- Application: Handle critical error moments and completion states with care. Make success states clear, reassuring, and aesthetically pleasing.

24) Postel’s Law
- Be liberal in what you accept; conservative in what you send.
- Application: Allow flexible input formats where safe (dates, phone numbers), and normalize outputs to a clean, consistent format.

25) Selective Attention
- Users focus on what aligns with their goals.
- Application: Use visual hierarchy to direct attention to primary actions and key information. Avoid multiple competing focal points.

26) Serial Position Effect
- Items at the beginning and end of a list are remembered best.
- Application: Place important or critical items at the top or bottom of lists and menus. Avoid burying key options in the middle of long lists.

27) Tesler’s Law (Conservation of Complexity)
- Every system has an irreducible amount of complexity.
- Application: Push complexity into the system (smart defaults, validation, automation) rather than making the user manage it manually.

28) Von Restorff Effect (Isolation Effect)
- Distinctive items are more likely to be noticed and remembered.
- Application: Use contrast (color, size, shape) to make primary actions, warnings, or promotions stand out clearly from other elements.

29) Working Memory (reinforced)
- The UI should minimize the need to remember prior steps.
- Application: Keep context visible: selections, totals, titles, and key data should stay on screen when needed, especially in multi-step flows.

30) Zeigarnik Effect
- People remember unfinished tasks more than completed ones.
- Application: Surface incomplete tasks, drafts, and partial setups. Provide clear paths to resume and complete them, and gentle reminders where appropriate.
</ux_laws>
"""

