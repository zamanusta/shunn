import sys
import os
import re

# Try to import yaml, if not handling it differently or erroring
try:
    import yaml
except ImportError:
    print("Error: PyYAML is not installed. Please run 'pip install PyYAML'.")
    sys.exit(1)

FRONTMATTER_SCHEMA = [
    'address',
    'firstname',
    'lastname',
    'byline',
    'font_family',
    'title',
    'page_size',
    'email'
]

METADATA_FILENAME = 'metadata.yaml'

def parse_frontmatter(filename):
    """
    Parses YAML frontmatter from a markdown file.
    Assumes frontmatter is between the first two '---' lines.
    """
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read()
            
        if content.startswith('---'):
            parts = content.split('---', 2)
            if len(parts) >= 3:
                # parts[0] is empty, parts[1] is yaml, parts[2] is content
                fm = yaml.safe_load(parts[1])
                if isinstance(fm, dict):
                    return fm
    except Exception as e:
        print(f"Error parsing frontmatter: {e}")
    
    return {}

def render_template(template_str, context):
    """
    Simple Mustache-like renderer.
    Replaces {{{ key }}} and {{ key }} with values from context.
    """
    def get_val(match):
        key = match.group(1).strip()
        # Return string representation of the value, or empty string if not found
        return str(context.get(key, ''))

    # Replace {{{ ... }}} first (triple braces)
    # Regex matches {{{ anything }}}
    template_str = re.sub(r'\{\{\{(.*?)\}\}\}', get_val, template_str)
    
    # Replace {{ ... }} second
    template_str = re.sub(r'\{\{(.*?)\}\}', get_val, template_str)
    
    return template_str

def main():
    if len(sys.argv) < 2:
        print("Usage: render.py <filename> [metadata_filename]")
        sys.exit(1)
        
    filename = sys.argv[1]
    metadata_filename = sys.argv[2] if len(sys.argv) > 2 else METADATA_FILENAME
    
    default_context = {
        'page_size': 'A4',
        'font_family': '"Times New Roman", Times, serif'
    }
    
    common_context = {}
    if os.path.exists(metadata_filename):
        try:
            with open(metadata_filename, 'r', encoding='utf-8') as f:
                loaded = yaml.safe_load(f)
                if isinstance(loaded, dict):
                    common_context = loaded
        except Exception as e:
            print(f"Warning: Could not read metadata file: {e}")
            
    front_matter = parse_frontmatter(filename)
    
    # Merge: defaults -> metadata -> frontmatter
    context = default_context.copy()
    context.update(common_context)
    context.update(front_matter)
    
    # Validate keys
    missing_keys = [k for k in FRONTMATTER_SCHEMA if k not in context]
    if missing_keys:
        # The original script raises an error, so we should too to be safe
        print(f"Error: Missing keys in frontmatter: {missing_keys}")
        sys.exit(1)
        
    # Read template
    template_path = os.path.join(os.getcwd(), 'templates', 'manuscript.css.mustache')
    try:
        with open(template_path, 'r', encoding='utf-8') as f:
            template = f.read()
    except FileNotFoundError:
        print(f"Error: Template file not found at {template_path}")
        sys.exit(1)
        
    # Render CSS
    css = render_template(template, context)
    
    # Write output
    out_dir = os.path.join(os.getcwd(), 'rendered')
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)
        
    out_file = os.path.join(out_dir, 'manuscript.css')
    with open(out_file, 'w', encoding='utf-8') as f:
        f.write(css)
    
    print(f"Successfully rendered CSS to {out_file}")

if __name__ == '__main__':
    main()
