import re

with open('wiki/biblio.md', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# === Step 1: Remove duplicate sections ===
# Duplicate SP section: lines 224-232 (index 223-231)
# Duplicate ODM section: lines 234-241 (index 233-240)
# Duplicate MDS+VSN+MRR+RD+STO section: lines 243-252 (index 242-251)
# We identify them by finding the second occurrence of each duplicated heading
duplicate_ranges = []
headings_seen = set()
for i, line in enumerate(lines):
    stripped = line.strip()
    if stripped.startswith('## '):
        if stripped in headings_seen:
            # Find the end of this duplicate section
            start = i
            end = start + 1
            while end < len(lines):
                if lines[end].strip().startswith('## '):
                    break
                end += 1
            duplicate_ranges.append((start, end))
        else:
            headings_seen.add(stripped)

# Remove duplicates in reverse order to preserve indices
duplicate_ranges.sort(reverse=True)
for start, end in duplicate_ranges:
    del lines[start:end]

# === Step 2: Sort entries within each section ===
# Group lines into sections
sections = []
current_section_start = 0
current_heading_level = 0

# Find all heading boundaries
heading_indices = []
for i, line in enumerate(lines):
    stripped = line.strip()
    if stripped.startswith('### '):
        heading_indices.append((i, 3))
    elif stripped.startswith('## '):
        heading_indices.append((i, 2))

# Process each subsection (###) or section (##)
# We'll work at the ### level first, then ## sections without ###
def get_sort_key(entry_line):
    """Extract sort key from entry line (strip - , [[wikilink|display]] etc.)"""
    text = entry_line.strip()
    # Remove leading - 
    if text.startswith('- '):
        text = text[2:]
    # Extract display text from wikilink [[target|display]] or [[display]]
    wikilink_match = re.match(r'\[\[(?:[^|]+\|)?(.+?)\]\]', text)
    if wikilink_match:
        text = wikilink_match.group(1)
    # Remove «» quotes for sorting
    text = text.replace('\u00ab', '').replace('\u00bb', '')
    return text.lower()

new_lines = []
i = 0
while i < len(lines):
    line = lines[i]
    stripped = line.strip()
    
    if stripped.startswith('### '):
        # Start of a subsection: collect all entries until next heading of same or higher level
        section_lines = [line]
        i += 1
        while i < len(lines):
            next_stripped = lines[i].strip()
            if next_stripped.startswith('### ') or next_stripped.startswith('## '):
                break
            if next_stripped == '---':
                section_lines.append(lines[i])
                i += 1
                continue
            if next_stripped == '':
                section_lines.append(lines[i])
                i += 1
                continue
            # It's an entry or other content
            section_lines.append(lines[i])
            i += 1
        
        # Sort only the entry lines (starting with -), preserve blank lines and separators
        entry_indices = []
        non_entry_lines = []
        for j, sl in enumerate(section_lines):
            if sl.strip().startswith('- '):
                entry_indices.append(j)
            else:
                non_entry_lines.append((j, sl))
        
        entry_lines = [(j, section_lines[j]) for j in entry_indices]
        entry_lines.sort(key=lambda x: get_sort_key(x[1]))
        
        # Reconstruct section
        entry_map = {orig_idx: new_entry for (orig_idx, new_entry), new_idx in 
                     zip(entry_lines, range(len(entry_lines)))}
        
        sorted_section = []
        entry_counter = 0
        for j in range(len(section_lines)):
            if j in [e[0] for e in entry_lines]:
                sorted_section.append(entry_lines[entry_counter][1])
                entry_counter += 1
            else:
                sorted_section.append(section_lines[j])
        
        new_lines.extend(sorted_section)
    
    elif stripped.startswith('## '):
        # Section without sub-sections: collect and sort
        section_lines = [line]
        i += 1
        while i < len(lines):
            next_stripped = lines[i].strip()
            if next_stripped.startswith('## '):
                break
            if next_stripped.startswith('### '):
                break
            section_lines.append(lines[i])
            i += 1
        
        # Sort entry lines
        entry_indices = []
        non_entry_lines = []
        for j, sl in enumerate(section_lines):
            if sl.strip().startswith('- '):
                entry_indices.append(j)
            else:
                non_entry_lines.append((j, sl))
        
        entry_lines = [(j, section_lines[j]) for j in entry_indices]
        entry_lines.sort(key=lambda x: get_sort_key(x[1]))
        
        sorted_section = []
        entry_counter = 0
        for j in range(len(section_lines)):
            if j in [e[0] for e in entry_lines]:
                sorted_section.append(entry_lines[entry_counter][1])
                entry_counter += 1
            else:
                sorted_section.append(section_lines[j])
        
        new_lines.extend(sorted_section)
    
    else:
        # Non-section content (header, etc.)
        new_lines.append(line)
        i += 1

with open('wiki/biblio.md', 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print(f'Done. Removed {len(duplicate_ranges)} duplicate sections, sorted entries.')
