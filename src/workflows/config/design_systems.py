"""
Design system style guides for UI generation.
Simple string-based approach for MVP. Each string provides context to LLMs
about the visual language and conventions of the design system.
"""

DESIGN_SYSTEM_GUIDES = {
    "shadcn": (
        "Modern, clean aesthetic with subtle shadows and elegant spacing. "
        "Use rounded corners (8-12px), neutral color palette with slate/zinc grays (#18181B, #71717A). "
        "Prefer lucide icons. Components should feel refined and minimalist."
    ),

    "material": (
        "Material Design 3 principles with bold, elevated components. "
        "Strong shadows for depth, 4px corner radius, vibrant colors with #1976D2 blue as primary. "
        "Use material icons. Emphasize clear hierarchy and tactile surfaces."
    ),

    "ios": (
        "iOS Human Interface Guidelines with minimalist, light design. "
        "Thin borders (1px), large corner radius (16-20px), SF Pro or system-ui font. "
        "iOS blue #007AFF for interactive elements. Clean, spacious layouts."
    ),

    "fluent": (
        "Microsoft Fluent Design with modern, responsive feel. "
        "Acrylic backgrounds, 4-8px corner radius, #0078D4 blue accent. "
        "Subtle depth and lighting effects. Professional and accessible."
    ),

    "ant": (
        "Ant Design system with enterprise focus. "
        "8px corner radius, #1890FF primary blue, structured layouts. "
        "Clear information architecture, professional aesthetics."
    ),
}

def get_style_guide(design_system: str = "shadcn") -> str:
    """
    Get the style guide description for a design system.

    Args:
        design_system: Name of the design system (lowercase)

    Returns:
        Style guide string for use in prompts
    """
    return DESIGN_SYSTEM_GUIDES.get(design_system.lower(), DESIGN_SYSTEM_GUIDES["shadcn"])
