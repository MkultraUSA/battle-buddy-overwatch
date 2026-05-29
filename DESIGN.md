---
version: alpha
name: Battle Buddy Overwatch
description: God-mode situational awareness dashboard for tactical radio intelligence. Dense, real-time fusion of live audio, transcription, incident detection, mapping, and knowledge graph. Inspired by Palantir Gotham but built for first responders and public safety.
colors:
  primary: "#0A1428"          # Deep tactical blue-black
  accent: "#00B4D8"           # Bright cyan for live alerts and active incidents
  warning: "#FF4D4D"          # Red for high-priority incidents
  success: "#00CC88"          # Green for resolved/verified
  neutral: "#B0B8C1"          # Muted grays for background data layers
  text-primary: "#F0F4F8"
  text-secondary: "#8A9BA8"
typography:
  display:
    fontFamily: "Inter"
    fontSize: "2.25rem"
    fontWeight: 700
    lineHeight: 1.1
    letterSpacing: "-0.03em"
  heading:
    fontFamily: "Inter"
    fontSize: "1.25rem"
    fontWeight: 600
    lineHeight: 1.3
  body:
    fontFamily: "Inter"
    fontSize: "0.95rem"
    fontWeight: 400
    lineHeight: 1.5
  mono:
    fontFamily: "JetBrains Mono"
    fontSize: "0.85rem"
rounded:
  sm: "4px"
  md: "8px"
  lg: "12px"
  panel: "16px"
spacing:
  base: "8px"
  panel: "16px"
  section: "24px"
components:
  live-indicator:
    backgroundColor: "{colors.accent}"
    textColor: "{colors.text-primary}"
    rounded: "{rounded.sm}"
    padding: "4px 10px"
  incident-card:
    backgroundColor: "#13213A"
    borderColor: "{colors.accent}"
    rounded: "{rounded.md}"
    elevation: "0 4px 12px rgba(0, 180, 216, 0.15)"
  graph-node-incident:
    fill: "{colors.warning}"
    stroke: "{colors.text-primary}"
  map-overlay:
    opacity: 0.85
    blendMode: "multiply"
---

## Overview

Battle Buddy Overwatch is a single-pane "God Mode" dashboard that gives tactical teams real-time fused intelligence from radio communications, incidents, mapping, external feeds, and historical patterns.

It deliberately rejects clean minimalism in favor of dense, information-rich layouts similar to Palantir Gotham — multiple coordinated views, live layers, ontology-backed search, and configurable rules.

The design prioritizes:
- Immediate situational awareness (what is happening RIGHT NOW)
- Drill-down without losing context
- Knowledge graph as the single source of truth
- Modes for different missions (normal, overwatch, timeline, investigation)

## Colors

Primary palette is dark tactical with high-contrast cyan accents for anything live or critical. Red is used sparingly and only for true high-priority incidents. All text maintains WCAG AA contrast on dark backgrounds.

Accent cyan (#00B4D8) is the "live" color — any pulsing, active, or real-time element uses it.

## Typography

Inter for all UI text (highly legible at small sizes on dense dashboards). JetBrains Mono for any code, talkgroup IDs, timestamps, or logs. Display font is used only for major incident titles.

## Layout

The dashboard uses a coordinated multi-panel layout:
- Top bar: global search, active incidents count, live radio status, mode switcher
- Left sidebar: ontology browser (knowledge graph navigator)
- Center: primary map with overlay layers (incidents, units, talkgroup heat, satellite)
- Right panel: live transcript feed + incident cards (collapsible)
- Bottom: timeline scrubber that controls all views

All panels are resizable and can be toggled. Default is dense "overwatch" mode.

## Components

live-indicator: Small pulsing pill used for "LIVE", active talkgroups, or streaming audio.
incident-card: Compact but information-dense cards showing transcript excerpt, confidence, linked entities from the graph, and quick actions.
graph-node-incident: Visual representation in the ontology explorer.
map-overlay: Semi-transparent layers that can be toggled (radio heat, incident clusters, ADS-B tracks, weather).

## Principles

- Every data point must be traceable to source (radio call, timestamp, talkgroup, confidence score).
- The knowledge graph is first-class — clicking any entity anywhere opens its graph neighborhood.
- Support multiple simultaneous users with presence and shared annotations.
- All rules (what counts as an incident) should be configurable via UI without code changes.

This DESIGN.md serves as the single source of truth for all future Battle Buddy UI and data model work.
