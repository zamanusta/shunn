import os

file_path = 'inputs/test.md'

with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

output = []
in_frontmatter = False
fm_delimiter_count = 0

for i, line in enumerate(lines):
    # Detect frontmatter
    stripped = line.strip()
    
    if i == 0 and stripped == '---':
        in_frontmatter = True
        
    if in_frontmatter:
        output.append(line)
        if stripped == '---':
            fm_delimiter_count += 1
            if fm_delimiter_count == 2:
                in_frontmatter = False
        continue

    # Body content
    output.append(line)
    
    # Logic: If current line is not empty, and next line is not empty, insert a blank line.
    
    if stripped: # Current line has text
        if i + 1 < len(lines):
            next_line = lines[i+1].strip()
            if next_line and next_line != '---': # Next line has text
                # Check if the current line doesn't already end with a newline
                if not line.endswith('\n'):
                     output.append('\n\n')
                else:
                     output.append('\n')

with open(file_path, 'w', encoding='utf-8') as f:
    f.writelines(output)

print("Formatting complete.")
