#!/usr/bin/env python3
"""
Deployment script — wires kg_integration.py into Battle Buddy production.
Adds imports + function calls at documented hook points.
"""

import re

def add_import(filepath, import_line):
    """Add an import statement after existing imports in a file."""
    with open(filepath, 'r') as f:
        content = f.read()
    
    if 'kg_integration' in content:
        print(f"  SKIP: {filepath} already has kg_integration import")
        return False
    
    # Find a good spot — after last 'import' / 'from' line at top of file
    # Insert after the last import-style line before any non-import code
    lines = content.split('\n')
    insert_idx = 0
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith('import ') or stripped.startswith('from ') or \
           stripped == '' or stripped.startswith('#'):
            insert_idx = i + 1
        elif insert_idx > 0 and not stripped.startswith(('import ', 'from ')):
            break
    
    lines.insert(insert_idx, import_line)
    with open(filepath, 'w') as f:
        f.write('\n'.join(lines))
    print(f"  OK: Added import at line {insert_idx + 1} in {filepath}")
    return True


def insert_after_line(filepath, marker_pattern, new_lines, description):
    """Insert lines after the first line matching marker_pattern."""
    with open(filepath, 'r') as f:
        content = f.read()
    
    if 'kg_write' in content:
        print(f"  SKIP: {filepath} already has kg_write calls")
        return False
    
    lines = content.split('\n')
    for i, line in enumerate(lines):
        if re.search(marker_pattern, line):
            # Insert after this line
            for j, new_line in enumerate(new_lines):
                lines.insert(i + 1 + j, new_line)
            with open(filepath, 'w') as f:
                f.write('\n'.join(lines))
            print(f"  OK: Inserted '{description}' after line {i + 1}")
            return True
    
    print(f"  WARN: Marker pattern not found for '{description}'")
    return True


# ---------------------------------------------------------------------------
# 1. audio_receiver.py
# ---------------------------------------------------------------------------
print("[1/4] Adding import to audio_receiver.py...")
add_import(
    '/opt/battlebuddy/audio_receiver.py',
    'from modules.kg_integration import kg_write_call, kg_link_call_to_incident'
)

print("[2/4] Adding kg_write_call hook in process()...")
insert_after_line(
    '/opt/battlebuddy/audio_receiver.py',
    r'call\[\"llm\"\]\s*=\s*llm_analyze\(call,\s*recent\)',
    [
        '            try:',
        '                kg_write_call(call)',
        '            except Exception as _kg_err:',
        '                print(f"[recv] KG write warning: {_kg_err}", flush=True)',
    ],
    'kg_write_call(call) after LLM analyze'
)

print("[3/4] Adding import to incident_engine.py...")
add_import(
    '/opt/battlebuddy/modules/incident_engine.py',
    'from modules.kg_integration import kg_write_incident'
)

print("[4/4] Adding kg_write_incident hook in _create_incident()...")
insert_after_line(
    '/opt/battlebuddy/modules/incident_engine.py',
    r'_active_incidents\[inc_id\]\s*=\s*\{',
    [
        "        try:",
        "            kg_write_incident({",
        "                'id': inc_id,",
        "                'itype': itype,",
        "                'description': desc,",
        "                'lat': call.get('lat'),",
        "                'lon': call.get('lon'),",
        "                'location': call.get('location'),",
        "                'tgid': tgid,",
        "                'category': cat,",
        "            })",
        "        except Exception as _kg_err:",
        "            print(f'[incident] KG write warning: {_kg_err}', flush=True)",
    ],
    'kg_write_incident() after _create_incident populates dict'
)

print("\nDone! Verifying imports work...")
try:
    from modules.kg_integration import kg_write_call, kg_write_incident
    print("  OK: kg_integration imports successfully")
except Exception as e:
    print(f"  ERROR importing kg_integration: {e}")

try:
    from modules.kg_ontology import BattleBuddyKG
    print("  OK: kg_ontology imports successfully")
except Exception as e:
    print(f"  ERROR importing kg_ontology: {e}")

print("\nAll done.")
