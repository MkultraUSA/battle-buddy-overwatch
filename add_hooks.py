#!/usr/bin/env python3
"""Add kg_write_call() and kg_write_incident() hook calls to production files."""

def insert_after_line(filepath, marker_text, new_lines, desc):
    with open(filepath, 'r') as f:
        content = f.read()
    
    if 'kg_write_call' in content and 'kg_write_incident' in content:
        # Check if actual calls exist (not just imports)
        if 'kg_write_call(call)' in content or 'kg_write_incident(' in content:
            print(f"  SKIP: {desc} already has call")
            return
    
    idx = content.find(marker_text)
    if idx == -1:
        print(f"  WARN: Marker not found for {desc}")
        return
    
    # Find end of the marker line
    line_end = content.index('\n', idx)
    insertion_point = line_end + 1
    
    indent = '            '  # match indent of process() body
    new_block = '\n'.join(indent + l for l in new_lines) + '\n'
    
    content = content[:insertion_point] + new_block + content[insertion_point:]
    
    with open(filepath, 'w') as f:
        f.write(content)
    print(f"  OK: Added {desc}")


# --- audio_receiver.py: kg_write_call after LLM analyze ---
print("[1/2] Adding kg_write_call() hook in audio_receiver.py...")
insert_after_line(
    '/opt/battlebuddy/audio_receiver.py',
    'call["llm"] = llm_analyze(call, recent)',
    [
        'try:',
        '    kg_write_call(call)',
        'except Exception as _kg_err:',
        '    print(f"[recv] KG write warning: {_kg_err}", flush=True)',
    ],
    'audio_receiver kg_write_call'
)

# --- incident_engine.py: kg_write_incident after _active_incidents dict populated ---
print("[2/2] Adding kg_write_incident() hook in incident_engine.py...")

with open('/opt/battlebuddy/modules/incident_engine.py', 'r') as f:
    content = f.read()

# Find _active_incidents[inc_id] = { and find its closing }
import re
match = re.search(r'_active_incidents\[inc_id\]\s*=\s*\{', content)
if match:
    start = match.start()
    # Find matching closing brace (count braces)
    brace_start = content.index('{', match.start())
    depth = 0
    i = brace_start
    while i < len(content):
        if content[i] == '{':
            depth += 1
        elif content[i] == '}':
            depth -= 1
            if depth == 0:
                # Found closing brace — insert after this line
                line_end = content.index('\n', i)
                new_code = '''\
        try:
            kg_write_incident({
                "id": inc_id,
                "itype": itype,
                "description": desc,
                "lat": call.get("lat"),
                "lon": call.get("lon"),
                "location": call.get("location"),
                "tgid": tgid,
                "category": cat,
            })
        except Exception as _kg_err:
            print(f"[incident] KG write warning: {_kg_err}", flush=True)
'''
                content = content[:line_end+1] + '\n' + new_code + content[line_end+1:]
                break
        i += 1
    
    with open('/opt/battlebuddy/modules/incident_engine.py', 'w') as f:
        f.write(content)
    print("  OK: Added incident_engine kg_write_incident")

# Verify syntax
print("\nVerifying syntax...")
import ast
ast.parse(open('/opt/battlebuddy/audio_receiver.py').read())
print("  audio_receiver.py: OK")
ast.parse(open('/opt/battlebuddy/modules/incident_engine.py').read())
print("  incident_engine.py: OK")

# Confirm calls present
ar = open('/opt/battlebuddy/audio_receiver.py').read()
ie = open('/opt/battlebuddy/modules/incident_engine.py').read()
print(f"\n  audio_receiver.py has kg_write_call: {'kg_write_call(call)' in ar}")
print(f"  incident_engine.py has kg_write_incident: {'kg_write_incident(' in ie}")

print("\nDone!")
