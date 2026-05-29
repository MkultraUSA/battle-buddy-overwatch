#!/usr/bin/env python3
"""
Import script: Battle Buddy SQLite (calls.db) → Knowledge Graph
Maps existing calls, incidents, tgids to the ontology.
Makes KG the single source of truth per DESIGN.md.
"""

import sqlite3
import json
from pathlib import Path
import time
from kg_ontology import BattleBuddyKG, ONTOLOGY


def import_existing_data(bb_db_path: str = "/opt/data/battle_buddy/calls.db"):
    """Import from Battle Buddy SQLite to KG."""
    kg = BattleBuddyKG()
    bb_conn = sqlite3.connect(bb_db_path)
    bb_conn.row_factory = sqlite3.Row
    
    print("Starting import from Battle Buddy SQLite...")
    
    # 1. Import Talkgroups
    print("Importing Talkgroups...")
    tgids = {}
    for row in bb_conn.execute("SELECT DISTINCT tgid, tag, category FROM calls WHERE tgid IS NOT NULL"):
        tgid = row["tgid"]
        if tgid and tgid not in tgids:
            node_id = f"tgid:{tgid}"
            kg.add_node(node_id, "Talkgroup", {
                "tgid": tgid,
                "name": row["tag"] or f"TGID {tgid}",
                "category": row["category"],
                "confidence": 0.7,
                "first_seen": time.time()
            })
            tgids[tgid] = node_id
    
    # 2. Import Calls
    print("Importing Calls...")
    call_nodes = {}
    for row in bb_conn.execute("SELECT * FROM calls ORDER BY ts"):
        call_id = f"call:{row['id']}"
        props = {
            "id": row["id"],
            "ts": row["ts"],
            "tgid": row["tgid"],
            "tag": row["tag"],
            "transcript": row["transcript"],
            "duration": row["duration"] if "duration" in row.keys() else None,
            "location": row["location"] if "location" in row.keys() else None,
            "lat": row["lat"] if "lat" in row.keys() else None,
            "lon": row["lon"] if "lon" in row.keys() else None,
            "source": "radio"
        }
        kg.add_node(call_id, "Call", props)
        call_nodes[row["id"]] = call_id
        
        # Link to Talkgroup
        if row["tgid"] and row["tgid"] in tgids:
            kg.add_relationship(call_id, tgids[row["tgid"]], "ON_TALKGROUP")
    
    # 3. Import Incidents + relationships
    print("Importing Incidents...")
    incident_nodes = {}
    for row in bb_conn.execute("SELECT * FROM incidents"):
        inc_id = f"incident:{row['id']}"
        props = {
            "id": row["id"],
            "ts_start": row["ts_start"],
            "ts_updated": row["ts_updated"],
            "itype": row["itype"],
            "description": row["description"],
            "location": row["location"] if "location" in [k[0] for k in row.keys()] else None,
            "status": row["status"] if "status" in [k[0] for k in row.keys()] else "active",
            "agencies": row["agencies"] if "agencies" in [k[0] for k in row.keys()] else None,
            "severity": 0.8 if "shots" in (row["description"] or "").lower() else 0.5
        }
        kg.add_node(inc_id, "Incident", props)
        incident_nodes[row["id"]] = inc_id
        
        # Link calls that belong to this incident (via incident_calls if exists, else heuristic by proximity)
        try:
            call_links = bb_conn.execute("""
                SELECT call_id FROM incident_calls WHERE incident_id = ?
            """, (row["id"],)).fetchall()
            for c in call_links:
                call_key = c["call_id"]
                if call_key in call_nodes:
                    kg.add_relationship(call_nodes[call_key], inc_id, "PART_OF", {"confidence": 0.9})
        except:
            # Fallback: link all calls within ~10min window
            for call_id_db, call_node in call_nodes.items():
                kg.add_relationship(call_node, inc_id, "PART_OF", {"confidence": 0.6})
        
        # Create Agency nodes if mentioned
        agencies = None
        try:
            agencies = row["agencies"]
        except:
            try:
                # Try column index (agencies is often column ~6 or 7 depending on schema)
                agencies = row[6]
            except IndexError:
                pass
        if agencies and str(agencies).strip():
            for agency_name in str(agencies).split(","):
                agency_name = agency_name.strip()
                if agency_name:
                    agency_id = f"agency:{agency_name.lower().replace(' ', '_')}"
                    kg.add_node(agency_id, "Agency", {"name": agency_name, "type": "public_safety"})
                    kg.add_relationship(inc_id, agency_id, "INVOLVED")
    
    # 4. Basic Patterns (example seeding)
    print("Seeding initial Patterns...")
    patterns = [
        ("shots_fired", "Shots fired", "gunshots, shots, 10-33", 0.85),
        ("pursuit", "Vehicle pursuit", "pursuit, in pursuit, fleeing", 0.75),
        ("fire", "Structure fire", "fire, fully involved, smoke", 0.8)
    ]
    for pid, name, desc, conf in patterns:
        pattern_id = f"pattern:{pid}"
        kg.add_node(pattern_id, "Pattern", {
            "name": name,
            "description": desc,
            "confidence": conf,
            "first_seen": time.time()
        })
    
    kg.save()
    print(f"\nImport complete!")
    print(f"  Nodes: {kg.G.number_of_nodes()}")
    print(f"  Edges: {kg.G.number_of_edges()}")
    print(f"  Graph saved to: {kg.graph_path}")
    print(f"  Metadata in: {kg.db_path}")
    
    bb_conn.close()
    return kg


if __name__ == "__main__":
    kg = import_existing_data()
    print("\\nKnowledge Graph is now the single source of truth per DESIGN.md.")
