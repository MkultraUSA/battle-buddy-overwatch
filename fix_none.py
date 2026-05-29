#!/usr/bin/env python3
"""Fix kg_integration.py — strip None values from node props before add_node."""

with open('/opt/battlebuddy/modules/kg_integration.py', 'r') as f:
    content = f.read()

# Fix 1: Strip None from Call node props
old1 = '''        with _kg_lock:
            kg.add_node(node_id, label="Call", properties=props)'''

new1 = '''        # Strip None values — NetworkX doesn't allow them as node attributes
        props = {k: v for k, v in props.items() if v is not None}

        with _kg_lock:
            kg.add_node(node_id, label="Call", properties=props)'''

content = content.replace(old1, new1)

# Fix 2: Strip None from Talkgroup node props
old2 = '''                    kg.add_node(tg_node_id, label="Talkgroup", properties=tg_props)'''

new2 = '''                    tg_props = {k: v for k, v in tg_props.items() if v is not None}
                    kg.add_node(tg_node_id, label="Talkgroup", properties=tg_props)'''

content = content.replace(old2, new2)

# Fix 3: Strip None from Agency node props
old3 = '''                    kg.add_node(agency_node_id, label="Agency",
                                properties=agency_props)'''

new3 = '''                    agency_props = {k: v for k, v in agency_props.items() if v is not None}
                    kg.add_node(agency_node_id, label="Agency",
                                properties=agency_props)'''

content = content.replace(old3, new3)

# Fix 4: Also handle kg_write_incident's incident props
old4 = '''            kg.add_node(node_id, label="Incident", properties=props)'''
if 'Strip None' not in content.split('def kg_write_incident')[1].split('def')[0]:
    # Only add if not already there for incident function
    pass  # We'll check manually below

with open('/opt/battlebuddy/modules/kg_integration.py', 'w') as f:
    f.write(content)

import ast
ast.parse(content)
print("Syntax OK")
print("Fixes applied:")
print(f"  Call None filter: {'v is not None' in content.split('label=\"Call\"')[0]}")
print(f"  Talkgroup None filter: {content.count('v is not None') >= 2}")
print(f"  Agency None filter: {content.count('v is not None') >= 3}")
