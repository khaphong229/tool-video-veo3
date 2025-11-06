"""
Template Manager Demo
Interactive demonstration of template management features
"""

import sys
import os

# Suppress console encoding errors
if sys.platform == 'win32':
    os.environ['PYTHONIOENCODING'] = 'utf-8'

from core.managers import TemplateManager, PromptTemplate


def print_header(title):
    """Print section header"""
    print("\n" + "="*70)
    print(title)
    print("="*70)


def print_template(template: PromptTemplate, detailed=False):
    """Print template information"""
    print(f"\nTemplate #{template.id}: {template.name}")
    print(f"  Category: {template.category}")
    print(f"  Usage: {template.usage_count} times")
    print(f"  Favorite: {'Yes' if template.is_favorite else 'No'}")
    print(f"  Tags: {', '.join(template.tags)}")

    if detailed:
        print(f"\n  Base Style: {template.base_style}")
        print(f"  Camera: {template.camera_movement}")
        print(f"  Lighting: {template.lighting}")
        print(f"  Colors: {template.color_palette}")
        print(f"  Audio: {template.audio_description}")


def demo_list_templates(manager: TemplateManager):
    """Demo: List all templates"""
    print_header("LIST ALL TEMPLATES")

    templates = manager.get_all_templates()
    print(f"\nFound {len(templates)} templates:")

    for template in templates:
        print_template(template)


def demo_list_by_category(manager: TemplateManager):
    """Demo: List templates by category"""
    print_header("LIST TEMPLATES BY CATEGORY")

    categories = manager.get_categories()
    print(f"\nAvailable categories: {', '.join(categories)}\n")

    for category in categories:
        templates = manager.get_all_templates(category=category)
        print(f"\n{category} ({len(templates)} templates):")
        for template in templates:
            print(f"  - {template.name}")


def demo_search_templates(manager: TemplateManager):
    """Demo: Search templates"""
    print_header("SEARCH TEMPLATES")

    search_queries = ['anime', 'cinematic', 'realistic', 'game']

    for query in search_queries:
        results = manager.search_templates(query)
        print(f"\nSearch '{query}': Found {len(results)} results")
        for template in results:
            print(f"  - {template.name} ({template.category})")


def demo_apply_template(manager: TemplateManager):
    """Demo: Apply template to custom prompt"""
    print_header("APPLY TEMPLATE TO CUSTOM PROMPT")

    # Get a template
    template = manager.get_template(1)  # Cinematic Epic

    if not template:
        print("Template not found!")
        return

    print(f"\nUsing template: {template.name}")
    print(f"Category: {template.category}\n")

    # Custom prompts to try
    custom_prompts = [
        "A lone warrior stands on a cliff overlooking a vast desert",
        "Children playing in a futuristic playground",
        "A mysterious door opening in an ancient temple"
    ]

    for i, custom_prompt in enumerate(custom_prompts, 1):
        print(f"\n--- Example {i} ---")
        print(f"Custom Prompt: {custom_prompt}")
        print()

        final_prompt = manager.apply_template(template, custom_prompt)

        print(f"Final Prompt ({len(final_prompt)} chars):")
        print(f"{final_prompt[:200]}...")


def demo_create_custom_template(manager: TemplateManager):
    """Demo: Create custom template"""
    print_header("CREATE CUSTOM TEMPLATE")

    new_template = {
        'name': 'Horror Movie Style',
        'category': 'Horror',
        'base_style': 'dark horror film aesthetic, suspenseful atmosphere, unsettling mood',
        'camera_movement': 'slow creeping camera, dutch angles, disorienting movements',
        'lighting': 'low-key lighting, deep shadows, practical lighting sources only',
        'color_palette': 'desaturated colors, cold blue tones, deep blacks',
        'audio_description': 'eerie ambient sounds, discordant strings, sudden sound design',
        'tags': ['horror', 'dark', 'suspense', 'scary', 'film']
    }

    print("\nCreating new template: Horror Movie Style")
    template_id = manager.create_template(new_template)
    print(f"Created with ID: {template_id}")

    # Retrieve and display
    template = manager.get_template(template_id)
    print_template(template, detailed=True)

    # Try using it
    print("\n--- Applying to custom prompt ---")
    custom = "An old house at the end of a dark street"
    final = manager.apply_template(template, custom)
    print(f"\nCustom: {custom}")
    print(f"Final: {final[:150]}...")


def demo_favorites_and_usage(manager: TemplateManager):
    """Demo: Favorites and usage tracking"""
    print_header("FAVORITES AND USAGE TRACKING")

    # Mark some templates as favorites
    print("\nMarking templates 1, 3, 6 as favorites...")
    for template_id in [1, 3, 6]:
        manager.toggle_favorite(template_id)

    # Get favorites
    favorites = manager.get_favorite_templates()
    print(f"\nFavorite templates ({len(favorites)}):")
    for template in favorites:
        print(f"  - {template.name}")

    # Increment usage for testing
    print("\nSimulating template usage...")
    for i in range(5):
        manager.increment_usage(1)  # Cinematic Epic
    for i in range(3):
        manager.increment_usage(2)  # Anime Style
    for i in range(7):
        manager.increment_usage(6)  # Studio Ghibli

    # Get most used
    most_used = manager.get_most_used_templates(limit=5)
    print(f"\nMost used templates:")
    for template in most_used:
        print(f"  - {template.name}: {template.usage_count} uses")


def demo_statistics(manager: TemplateManager):
    """Demo: Get statistics"""
    print_header("TEMPLATE STATISTICS")

    stats = manager.get_statistics()

    print(f"\nTotal Templates: {stats['total_templates']}")
    print(f"Total Usage: {stats['total_usage']}")
    print(f"Favorites: {stats['favorite_count']}")
    print(f"Categories: {stats['category_count']}")

    if stats['most_used_template']:
        print(f"\nMost Used Template:")
        print(f"  {stats['most_used_template']['name']}")
        print(f"  {stats['most_used_template']['usage_count']} uses")


def demo_detailed_template_view(manager: TemplateManager):
    """Demo: View template in detail"""
    print_header("DETAILED TEMPLATE VIEW")

    # Show a few templates in detail
    template_ids = [1, 2, 6]

    for template_id in template_ids:
        template = manager.get_template(template_id)
        if template:
            print_template(template, detailed=True)


def main():
    """Main demo function"""
    print("="*70)
    print("TEMPLATE MANAGER DEMO")
    print("="*70)
    print()
    print("This demo showcases the Template Manager functionality:")
    print("  - Pre-defined templates")
    print("  - Template application")
    print("  - Search and filtering")
    print("  - Favorites and usage tracking")
    print("  - Custom template creation")
    print()

    # Initialize manager
    print("Initializing Template Manager...")
    manager = TemplateManager()
    print("Ready!")

    # Run demos
    demos = [
        ("1. List All Templates", demo_list_templates),
        ("2. List by Category", demo_list_by_category),
        ("3. Search Templates", demo_search_templates),
        ("4. Apply Template", demo_apply_template),
        ("5. Create Custom Template", demo_create_custom_template),
        ("6. Favorites & Usage", demo_favorites_and_usage),
        ("7. Statistics", demo_statistics),
        ("8. Detailed View", demo_detailed_template_view)
    ]

    while True:
        print("\n" + "="*70)
        print("SELECT DEMO")
        print("="*70)
        for i, (title, _) in enumerate(demos, 1):
            print(f"  {i}. {title}")
        print(f"  9. Run All Demos")
        print(f"  0. Exit")
        print()

        try:
            choice = input("Enter choice: ").strip()

            if choice == '0':
                print("\nGoodbye!")
                break
            elif choice == '9':
                for title, demo_func in demos:
                    demo_func(manager)
            elif choice.isdigit() and 1 <= int(choice) <= len(demos):
                demos[int(choice) - 1][1](manager)
            else:
                print("Invalid choice!")

            input("\nPress Enter to continue...")

        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            break
        except Exception as e:
            print(f"\nError: {e}")
            import traceback
            traceback.print_exc()


if __name__ == '__main__':
    main()
