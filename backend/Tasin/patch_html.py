# patch_html.py - Corrected and more robust version
# This script reads the index.html from the build directory
# and correctly replaces the asset paths with Django's static template tags.

import re
import os

def patch_html_for_django(html_file_path):
    """
    Patches the index.html file from a Vite build to use Django's {% static %} tags.
    This version uses standard string concatenation for reliable path replacement.
    """
    try:
        with open(html_file_path, 'r', encoding='utf-8') as file:
            content = file.read()

        # 1. Insert {% load static %} after <!doctype html>
        content = re.sub(r'(<!doctype html>\s*)', r'\1{% load static %}\n', content, flags=re.IGNORECASE)

        # 2. Function to handle the replacement of asset URLs
        # The regex now captures the attribute name (src|href) and the asset path
        def replace_asset_path(match):
            attribute = match.group(1)
            asset_path = match.group(2)
            # Reconstruct the Django static tag using string concatenation
            # This avoids the f-string's syntax error with {% ... %}
            # It also ensures the correct syntax: src="{% static '...' %}"
            return attribute + '="{% static \'react/assets/' + asset_path + '\' %}"'

        # 3. Replace all /assets/* paths with the correct Django static tag
        content = re.sub(
            r'(src|href)="/assets/([^"]+)"',
            replace_asset_path,
            content
        )

        # 4. Replace the vite.svg path with {% static %}
        def replace_vite_path(match):
            attribute = match.group(1)
            # Reconstruct the Django static tag for vite.svg
            return attribute + '="{% static \'react/vite.svg\' %}"'

        content = re.sub(
            r'(href)="/vite.svg"',
            replace_vite_path,
            content
        )

        with open(html_file_path, 'w', encoding='utf-8') as file:
            file.write(content)

        print(f"Successfully patched {html_file_path} for Django.")

    except FileNotFoundError:
        print(f"Error: {html_file_path} not found.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    # The path to your index.html file after the build script has copied it
    html_path = r"C:\Code projects\Tasin\backend\Tasin\react_accounts\templates\react\index.html"
    patch_html_for_django(html_path)
