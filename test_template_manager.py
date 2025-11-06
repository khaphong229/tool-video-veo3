"""
Automated test for Template Manager
"""

import sys
import os
from pathlib import Path

# Suppress console encoding errors
if sys.platform == 'win32':
    os.environ['PYTHONIOENCODING'] = 'utf-8'


def test_template_manager():
    """Test Template Manager functionality"""
    print("="*70)
    print("TEMPLATE MANAGER AUTOMATED TEST")
    print("="*70)
    print()

    # Use test database
    test_db = "test_templates.db"
    if Path(test_db).exists():
        Path(test_db).unlink()
        print(f"Cleaned up old test database: {test_db}")

    print("1. Importing TemplateManager...")
    try:
        from core.managers import TemplateManager, PromptTemplate
        print("   SUCCESS - TemplateManager imported")
    except Exception as e:
        print(f"   FAILED - {e}")
        import traceback
        traceback.print_exc()
        return False

    print()
    print("2. Creating TemplateManager instance...")
    try:
        manager = TemplateManager(db_path=test_db)
        print("   SUCCESS - TemplateManager created")
    except Exception as e:
        print(f"   FAILED - {e}")
        import traceback
        traceback.print_exc()
        return False

    print()
    print("3. Checking pre-defined templates...")
    try:
        templates = manager.get_all_templates()
        assert len(templates) == 8, f"Expected 8 templates, got {len(templates)}"

        expected_names = [
            'Cinematic Epic',
            'Anime Style',
            'Cyberpunk Game',
            'Nature Documentary',
            'Abstract Art',
            'Studio Ghibli Style',
            'Pixel Art',
            'Realistic Photography'
        ]

        template_names = [t.name for t in templates]
        for name in expected_names:
            assert name in template_names, f"Missing template: {name}"

        print(f"   SUCCESS - Found all 8 pre-defined templates")
    except AssertionError as e:
        print(f"   FAILED - {e}")
        return False

    print()
    print("4. Testing get_template()...")
    try:
        template = manager.get_template(1)
        assert template is not None, "Template 1 not found"
        assert isinstance(template, PromptTemplate)
        assert hasattr(template, 'name')
        assert hasattr(template, 'category')
        assert hasattr(template, 'base_style')
        assert hasattr(template, 'tags')

        print(f"   SUCCESS - Retrieved template: {template.name}")
    except AssertionError as e:
        print(f"   FAILED - {e}")
        return False

    print()
    print("5. Testing get_categories()...")
    try:
        categories = manager.get_categories()
        assert len(categories) > 0, "No categories found"

        expected_categories = ['Anime', 'Art', 'Cinematic', 'Documentary', 'Game', 'Photography']
        for cat in expected_categories:
            assert cat in categories, f"Missing category: {cat}"

        print(f"   SUCCESS - Found {len(categories)} categories: {', '.join(categories)}")
    except AssertionError as e:
        print(f"   FAILED - {e}")
        return False

    print()
    print("6. Testing filter by category...")
    try:
        anime_templates = manager.get_all_templates(category='Anime')
        assert len(anime_templates) == 2, f"Expected 2 anime templates, got {len(anime_templates)}"

        game_templates = manager.get_all_templates(category='Game')
        assert len(game_templates) == 2, f"Expected 2 game templates, got {len(game_templates)}"

        print(f"   SUCCESS - Category filtering works")
    except AssertionError as e:
        print(f"   FAILED - {e}")
        return False

    print()
    print("7. Testing search_templates()...")
    try:
        # Search by name
        results = manager.search_templates('Cinematic')
        assert len(results) > 0, "No results for 'Cinematic'"

        # Search by tag
        results = manager.search_templates('anime')
        assert len(results) >= 2, f"Expected at least 2 results for 'anime', got {len(results)}"

        print(f"   SUCCESS - Search functionality works")
    except AssertionError as e:
        print(f"   FAILED - {e}")
        return False

    print()
    print("8. Testing apply_template()...")
    try:
        template = manager.get_template(1)  # Cinematic Epic
        custom_prompt = "A hero walking through a destroyed city"

        final_prompt = manager.apply_template(template, custom_prompt)

        # Check that all components are included
        assert custom_prompt in final_prompt
        assert template.base_style in final_prompt
        assert template.camera_movement in final_prompt
        assert template.lighting in final_prompt

        print(f"   SUCCESS - Template application works")
        print(f"   Custom prompt: {custom_prompt[:50]}...")
        print(f"   Final prompt length: {len(final_prompt)} characters")
    except AssertionError as e:
        print(f"   FAILED - {e}")
        return False

    print()
    print("9. Testing create_template()...")
    try:
        new_template_data = {
            'name': 'Test Template',
            'category': 'Test',
            'base_style': 'Test style',
            'camera_movement': 'Test camera',
            'lighting': 'Test lighting',
            'color_palette': 'Test colors',
            'audio_description': 'Test audio',
            'tags': ['test', 'demo']
        }

        template_id = manager.create_template(new_template_data)
        assert template_id > 0, "Failed to create template"

        # Verify created
        created_template = manager.get_template(template_id)
        assert created_template is not None
        assert created_template.name == 'Test Template'
        assert len(created_template.tags) == 2

        print(f"   SUCCESS - Created template ID: {template_id}")
    except Exception as e:
        print(f"   FAILED - {e}")
        return False

    print()
    print("10. Testing update_template()...")
    try:
        manager.update_template(template_id, {
            'name': 'Updated Test Template',
            'tags': ['test', 'demo', 'updated']
        })

        updated = manager.get_template(template_id)
        assert updated.name == 'Updated Test Template'
        assert len(updated.tags) == 3

        print(f"   SUCCESS - Template updated")
    except Exception as e:
        print(f"   FAILED - {e}")
        return False

    print()
    print("11. Testing increment_usage()...")
    try:
        initial_template = manager.get_template(1)
        initial_usage = initial_template.usage_count

        manager.increment_usage(1)
        manager.increment_usage(1)

        updated_template = manager.get_template(1)
        assert updated_template.usage_count == initial_usage + 2

        print(f"   SUCCESS - Usage count incremented ({initial_usage} -> {updated_template.usage_count})")
    except AssertionError as e:
        print(f"   FAILED - {e}")
        return False

    print()
    print("12. Testing toggle_favorite()...")
    try:
        template = manager.get_template(1)
        initial_favorite = template.is_favorite

        new_status = manager.toggle_favorite(1)
        assert new_status != initial_favorite

        # Toggle back
        final_status = manager.toggle_favorite(1)
        assert final_status == initial_favorite

        print(f"   SUCCESS - Favorite toggle works")
    except AssertionError as e:
        print(f"   FAILED - {e}")
        return False

    print()
    print("13. Testing get_favorite_templates()...")
    try:
        # Make template 1 favorite
        manager.toggle_favorite(1)
        favorites = manager.get_favorite_templates()
        assert len(favorites) > 0, "No favorite templates found"

        print(f"   SUCCESS - Found {len(favorites)} favorite templates")
    except AssertionError as e:
        print(f"   FAILED - {e}")
        return False

    print()
    print("14. Testing get_most_used_templates()...")
    try:
        most_used = manager.get_most_used_templates(limit=5)
        assert len(most_used) > 0, "No most used templates found"

        # Should be sorted by usage count
        if len(most_used) > 1:
            assert most_used[0].usage_count >= most_used[1].usage_count

        print(f"   SUCCESS - Retrieved {len(most_used)} most used templates")
    except AssertionError as e:
        print(f"   FAILED - {e}")
        return False

    print()
    print("15. Testing get_statistics()...")
    try:
        stats = manager.get_statistics()
        assert 'total_templates' in stats
        assert 'total_usage' in stats
        assert 'favorite_count' in stats
        assert 'category_count' in stats

        assert stats['total_templates'] > 0
        assert stats['category_count'] > 0

        print(f"   SUCCESS - Statistics retrieved")
        print(f"   Total templates: {stats['total_templates']}")
        print(f"   Total usage: {stats['total_usage']}")
        print(f"   Categories: {stats['category_count']}")
    except AssertionError as e:
        print(f"   FAILED - {e}")
        return False

    print()
    print("16. Testing export/import template...")
    try:
        # Export
        export_data = manager.export_template(1)
        assert isinstance(export_data, dict)
        assert 'name' in export_data
        assert 'category' in export_data

        # Import
        new_id = manager.import_template(export_data)
        assert new_id > 0

        imported = manager.get_template(new_id)
        assert imported is not None
        assert imported.name == export_data['name']

        print(f"   SUCCESS - Export/import works (new ID: {new_id})")
    except Exception as e:
        print(f"   FAILED - {e}")
        return False

    print()
    print("17. Testing delete_template()...")
    try:
        # Delete the test template we created
        manager.delete_template(template_id)

        # Verify deleted
        deleted = manager.get_template(template_id)
        assert deleted is None, "Template should be deleted"

        print(f"   SUCCESS - Template deleted")
    except Exception as e:
        print(f"   FAILED - {e}")
        return False

    print()
    print("="*70)
    print("ALL TESTS PASSED")
    print("="*70)
    print()

    # Clean up test database
    if Path(test_db).exists():
        Path(test_db).unlink()
        print(f"Cleaned up test database: {test_db}")

    return True


if __name__ == '__main__':
    success = test_template_manager()
    sys.exit(0 if success else 1)
