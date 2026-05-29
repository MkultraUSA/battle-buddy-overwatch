#!/usr/bin/env python3
"""Fix incident_engine.py — move kg_integration import to correct position."""

with open('/opt/battlebuddy/modules/incident_engine.py', 'r') as f:
    lines = f.readlines()

# Remove the misplaced import line
new_lines = []
for line in lines:
    if 'from modules.kg_integration import kg_write_incident' in line:
        continue  # skip it
    new_lines.append(line)

# Find the end of the 'from modules.config import (' ... ')' block
# and insert after that closing paren
for i, line in enumerate(new_lines):
    if line.strip().startswith('TALK_BASE') or 'talk_base' in line.lower() and ')' in line:
        # Insert after this line (end of config import)
        new_lines.insert(i + 1, '\nfrom modules.kg_integration import kg_write_incident\n')
        break

with open('/opt/battlebuddy/modules/incident_engine.py', 'w') as f:
    f.writelines(new_lines)

print("Fixed. Verifying syntax...")
import ast
ast.parse(open('/opt/battlebuddy/modules/incident_engine.py').read())
print("Syntax OK")
print("Import present:", "kg_integration" in open('/opt/battlebuddy/modules/incident_engine.py').read())
