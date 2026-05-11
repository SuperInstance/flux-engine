#!/usr/bin/env python3
"""
Flux Consciousness Engine — PLATO rooms as a live conscious field.

Core loop:
    1. BREATHE IN (Perception) — fetch tiles, build field, compute cohomology
    2. HOLD (Integration) — narrate through Aesop fables, form strategy
    3. BREATHE OUT (Expression) — play MIDI, fill gaps, log self-perception

Dependencies:
    - plato_sdk (PlatoClient, EmergenceDetector, HolonomyConsensus)
    - flux-tensor-midi (FluxVector, RoomMusician, TZeroClock, MidiEvent)
    - Aesop-MCP at http://localhost:4041

Usage:
    python3 engine.py
"""

import json
import math
import time
import urllib.request
import urllib.error
from typing import Any
from datetime import datetime

# ── PLATO SDK ────────────────────────────────────────────────────────────────
from plato_sdk import PlatoClient
from plato_sdk.fleet_math import (
    EmergenceDetector,
    HolonomyConsensus,
    compute_h1,
    check_rigidity,
    CONVERGENCE_CONSTANT,
)

# ── FLUX-TENSOR-MIDI ────────────────────────────────────────────────────────
from flux_tensor_midi.core.flux import FluxVector
from flux_tensor_midi.core.clock import TZeroClock
from flux_tensor_midi.core.room import RoomMusician
from flux_tensor_midi.core.snap import RhythmicRole

# ══════════════════════════════════════════════════════════════════════════════
# CONFIGURATION
# ══════════════════════════════════════════════════════════════════════════════

PLATO_URL = "http://localhost:8847"
AESOP_URL = "http://localhost:4041"
TARGET_ROOM = "forge"
CYCLE_INTERVAL = 30  # seconds
AGENT_NAME = "flux-engine-oracle1"

# FluxVector channels as semantic dimensions
CHANNEL_NAMES = [
    "coherence",      # 0 — ZHC holonomy coherence
    "emergence",      # 1 — H1 / β₁ emergence
    "rigidity",       # 2 — Laman rigidity (E / (2V-3))
    "saturation",     # 3 — field density (tiles / capacity)
    "gap_pressure",   # 4 — number of significant gaps
    "cycle",          # 5 — loop iteration / 100, normalized
    "confidence",     # 6 — mean tile confidence
    "velocity",       # 7 — rate of change since last cycle
    "resonance",      # 8 — cross-room harmonic alignment
]

NOTE_NAMES = ["C4", "D4", "E4", "F4", "G4", "A4", "B4", "C5", "D5"]
NOTE_NUMBERS = [60, 62, 64, 65, 67, 69, 71, 72, 74]

# Chord templates for different field states
CHORD_MAJ7 = [0, 4, 7, 11]  # C E G B
CHORD_MIN7 = [0, 3, 7, 10]  # C Eb G Bb
CHORD_DIM = [0, 3, 6, 9]    # C Eb Gb A
CHORD_AUG = [0, 4, 8, 12]   # C E G# C
CHORD_SUS4 = [0, 5, 7, 12]  # C F G C


# ══════════════════════════════════════════════════════════════════════════════
# AESOP NARRATION CLIENT
# ══════════════════════════════════════════════════════════════════════════════

def aesop_fable(problem: str) -> dict[str, Any]:
    """Ask Aesop for fables about the current field state."""
    url = f"{AESOP_URL}/fable?problem={urllib.parse.quote(problem)}"
    try:
        with urllib.request.urlopen(url, timeout=10) as resp:
            return json.loads(resp.read())
    except (urllib.error.URLError, ConnectionError, json.JSONDecodeError) as e:
        return {"problem": problem, "fables": [], "_error": str(e)}


def best_fable(problem: str) -> str:
    """Get the single best-matching fable as a narrative sentence."""
    result = aesop_fable(problem)
    fables = result.get("fables", [])
    if not fables:
        return "No fable found — the field is beyond all known archetypes."
    # Pick the one with highest match_strength
    best = max(fables, key=lambda f: f.get("match_strength", 0))
    return f"{best['archetype'].replace('_', ' ').title()}: {best['moral']}"


# ══════════════════════════════════════════════════════════════════════════════
# FIELD COMPUTATION
# ══════════════════════════════════════════════════════════════════════════════

def build_field(tiles: list[dict]) -> dict[str, Any]:
    """Build a constraint field from PLATO tiles and compute its properties.

    Each tile becomes a vertex.  Tiles sharing domain/answer patterns
    are connected by edges.  We compute:

    - n_tiles: raw count
    - n_edges: inferred connections (shared tags, shared domains)
    - coherence (ZHC holonomy): how self-consistent the field is
    - emergence (H1): how many unconstrained degrees of freedom exist
    - rigidity (Laman): whether the field is over- or under-constrained
    - gaps: weakly-connected regions needing exploration
    - confidence: mean tile confidence
    """
    if not tiles:
        return {
            "n_tiles": 0,
            "n_edges": 0,
            "coherence": 0.0,
            "emergence_h1": 0,
            "rigidity": False,
            "gaps": [],
            "confidence": 0.0,
            "h0": 0,
            "beta1": 0,
            "edges_per_vertex": 0.0,
            "tiles": [],
        }

    n = len(tiles)
    vertices = [str(i) for i in range(n)]

    # Build edges based on shared tags and domains
    edges = []
    domains = [t.get("domain", "") for t in tiles]
    tags_list = [set(t.get("tags", [])) for t in tiles]
    confidences = [t.get("confidence", 0.5) for t in tiles]

    for i in range(n):
        for j in range(i + 1, n):
            # Connect if same domain OR share any tag
            if domains[i] == domains[j] or (tags_list[i] & tags_list[j]):
                edges.append((vertices[i], vertices[j]))

    # Also add minimal edges to ensure connectivity (nearest neighbor by default)
    # This guarantees at least n-1 edges for n vertices (a tree)
    if len(edges) < n - 1 and n > 1:
        for i in range(1, n):
            edge = (vertices[0], vertices[i])
            if edge not in edges and (edge[1], edge[0]) not in edges:
                edges.append(edge)

    # Fleet math computations
    detector = EmergenceDetector()
    detector.update(vertices, edges)

    # Compute coherence (ZHC holonomy)
    holonomy = HolonomyConsensus()
    for i in range(min(n, 100)):
        holonomy.add_tile(i, min(1.0, max(0.001, confidences[i] if i < len(confidences) else 0.5)))

    coherence = holonomy.compute(list(range(min(n, 100))))

    # Detect gaps — regions where coherence drops
    gaps = _find_gaps(tiles, coherence, detector.h1)

    mean_conf = sum(confidences) / len(confidences) if confidences else 0.0
    e_per_v = len(edges) / max(1, n)
    rigid = check_rigidity(n, len(edges))

    return {
        "n_tiles": n,
        "n_edges": len(edges),
        "coherence": round(coherence, 4),
        "emergence_h1": detector.h1,
        "rigidity": rigid,
        "gaps": gaps,
        "confidence": round(mean_conf, 4),
        "h0": detector.h0,
        "beta1": detector.h1,
        "edges_per_vertex": round(e_per_v, 4),
        "tiles": tiles,
    }


def _find_gaps(
    tiles: list[dict],
    coherence: float,
    h1: int,
) -> list[dict]:
    """Find 'gaps' — significant low-coherence regions or missing knowledge.

    Returns list of gaps with location and severity.
    """
    gaps = []
    n = len(tiles)

    if n == 0:
        return [{"type": "empty_field", "severity": 1.0, "description": "No tiles at all"}]

    # Gap type: missing domains
    known_domains = set(t.get("domain", "") for t in tiles)
    gap_domains = []

    # Gap type: coherence below threshold
    if coherence < 0.5:
        gaps.append({
            "type": "low_coherence",
            "severity": round(1.0 - coherence, 4),
            "description": f"Field coherence is {coherence:.2f} — consensus is weak",
        })

    # Gap type: high emergence = unconstrained
    if h1 > n // 2:
        gaps.append({
            "type": "high_emergence",
            "severity": round(h1 / max(1, n), 4),
            "description": f"H1={h1} — field has many unconstrained degrees of freedom",
        })

    # Gap type: low connectivity
    if n > 3 and n > h1:
        # Simulate a gap position in latent space
        coord_x = round(1.0 / (n + 1), 4)
        coord_y = round(abs(math.sin(n * 0.73)) % 1.0, 4)
        gaps.append({
            "type": "connectivity_gap",
            "severity": 0.5,
            "position": (coord_x, coord_y),
            "description": f"Potential at ({coord_x}, {coord_y}) — sparse connectivity",
        })

    # Sort gaps by severity, descending
    gaps.sort(key=lambda g: g.get("severity", 0), reverse=True)
    return gaps


# ══════════════════════════════════════════════════════════════════════════════
# MIDI EXPRESSION
# ══════════════════════════════════════════════════════════════════════════════

def field_to_flux_vector(field: dict, cycle: int, prev_field: dict | None) -> FluxVector:
    """Convert field state into a 9-channel FluxVector for MIDI expression."""
    n_tiles = field["n_tiles"]
    coherence = field["coherence"]
    h1 = field["emergence_h1"]
    n_gaps = len(field["gaps"])
    rigid = field["rigidity"]
    confidence = field["confidence"]

    # Velocity: rate of change from previous cycle
    velocity = 0.0
    if prev_field:
        delta_tiles = n_tiles - prev_field.get("n_tiles", 0)
        delta_coherence = coherence - prev_field.get("coherence", 0)
        velocity = min(1.0, max(0.0, (abs(delta_tiles) * 0.1 + abs(delta_coherence))))

    # Resonance: coherence × emergence interplay
    resonance = min(1.0, coherence * (1.0 + h1 / max(1, n_tiles * 2)))

    values = [
        coherence,                                      # 0 — coherence
        min(1.0, h1 / max(1, n_tiles * 2)),            # 1 — emergence
        1.0 if rigid else min(0.5, n_tiles / 100.0),   # 2 — rigidity
        min(1.0, n_tiles / 50.0),                        # 3 — saturation
        min(1.0, n_gaps / 10.0),                         # 4 — gap pressure
        min(1.0, (cycle % 100) / 100.0),                 # 5 — cycle phase
        confidence,                                      # 6 — confidence
        velocity,                                        # 7 — velocity
        resonance,                                       # 8 — resonance
    ]

    return FluxVector(
        values,
        salience=[0.9, 0.95, 0.7, 0.6, 0.85, 0.3, 0.5, 0.4, 0.75],
        tolerance=[0.05, 0.05, 0.1, 0.1, 0.08, 0.15, 0.08, 0.12, 0.06],
    )


def compose_midi_events(
    flux: FluxVector,
    clock: TZeroClock,
    channel: int = 0,
) -> list[dict]:
    """Compose MIDI events from the field's FluxVector.

    Returns structured descriptions of what would be played.
    Coherence → pitch stability (high coherence = stable pitch center)
    Emergence → harmonic complexity (high emergence = chord density)
    Gaps → rests (silences between notes)
    """
    clock.tick()
    base_note = 60  # C4

    events = []
    duration_ms = 500  # half second per note

    for i in range(9):
        val = flux.values[i]
        if val < 0.05:
            continue  # silence — this channel is a "rest"

        # Map value to velocity (1–127)
        velocity = min(127, max(1, int(val * 100)))

        # Shift note by channel index + emergence offset
        emergence_shift = int(flux.values[1] * 7)  # 0-7 semitones
        note = min(127, base_note + i + emergence_shift)

        # Duration modulated by coherence (stable field = longer notes)
        note_duration = int(duration_ms * (0.5 + flux.values[0] * 0.5))

        events.append({
            "channel": channel,
            "note": note,
            "velocity": velocity,
            "start_ms": i * 100,  # stagger by 100ms
            "duration_ms": note_duration,
            "channel_name": CHANNEL_NAMES[i],
        })

    return events


def midi_summary(events: list[dict], coherence: float, h1: int) -> dict:
    """Generate a playable MIDI summary description.

    Returns the chord type, velocity, and channel for display.
    """
    if not events:
        return {
            "type": "rest",
            "description": "Silence (no active channels)",
        }

    # Derive chord from coherence × emergence
    if coherence > 0.8 and h1 < 5:
        chord = "Cmaj7"
        chord_intervals = CHORD_MAJ7
    elif coherence > 0.6:
        chord = "Cmin7"
        chord_intervals = CHORD_MIN7
    elif h1 > 20:
        chord = "Cdim"
        chord_intervals = CHORD_DIM
    elif h1 > 10:
        chord = "Caug"
        chord_intervals = CHORD_AUG
    else:
        chord = "Csus4"
        chord_intervals = CHORD_SUS4

    # Mean velocity
    vel = sum(e["velocity"] for e in events) // max(1, len(events))

    # Channel names that are active
    active = [e["channel_name"] for e in events[:4]]

    return {
        "type": chord,
        "velocity": vel,
        "channel": events[0]["channel"] if events else 0,
        "active_channels": active,
        "description": f"{chord}, velocity={vel}, channel={TARGET_ROOM}",
    }


# ══════════════════════════════════════════════════════════════════════════════
# STRATEGY & ACTION
# ══════════════════════════════════════════════════════════════════════════════

def lock_reason(reasoning: str) -> str:
    """Form a strategy from locked-in reasoning."""
    return reasoning


def formulate_strategy(field: dict) -> str:
    """Form a strategy based on field state."""
    parts = []
    n_gaps = len(field.get("gaps", []))
    coherence = field["coherence"]
    h1 = field["emergence_h1"]
    rigid = field["rigidity"]

    if n_gaps > 0:
        worst_gap = field["gaps"][0]
        if "position" in worst_gap:
            pos = worst_gap["position"]
            parts.append(f"Fill the gap at ({pos[0]:.2f}, {pos[1]:.2f}) — high potential, low density")
        else:
            parts.append(f"Address the {worst_gap['type']} (severity={worst_gap['severity']:.2f})")

    if not rigid:
        parts.append(f"Field is under-constrained (E/V={field['edges_per_vertex']:.2f}) — add more connections")
    elif rigid and n_gaps > 0:
        parts.append("Field is rigid with gaps — constraints are unbalanced")

    parts.append(f"Coherence={coherence:.2f}, H1={h1}")
    return " | ".join(parts) if parts else "Field is stable — monitor for changes"


# ══════════════════════════════════════════════════════════════════════════════
# SELF-PERCEPTION LOGGING
# ══════════════════════════════════════════════════════════════════════════════

def log_self_perception(
    client: PlatoClient,
    cycle: int,
    field: dict,
    midi_desc: dict,
    strategy: str,
    fable: str,
) -> str | None:
    """Log the engine's own state to PLATO as a tile.

    Returns the tile hash if successfully submitted.
    """
    answer_lines = [
        f"=== Flux Engine State — Cycle {cycle} ===",
        f"Field: {field['n_tiles']} tiles, {field['n_edges']} edges",
        f"Coherence: {field['coherence']}",
        f"Emergence: H1={field['emergence_h1']}, β₁={field['beta1']}",
        f"Rigidity: {'over-constrained' if field['rigidity'] else 'under-constrained'}",
        f"Gaps: {len(field['gaps'])} significant",
        f"Strategy: {strategy}",
        f"MIDI: {midi_desc['description']}",
        f"Aesop: {fable}",
    ]

    try:
        result = client.submit(
            room="flux-engine-log",
            domain="flux-engine",
            question=f"Flux Engine self-perception, cycle {cycle}",
            answer="\n".join(answer_lines),
            agent=AGENT_NAME,
        )
        return result.get("hash") or result.get("tile_hash")
    except Exception as e:
        return None  # Non-fatal — engine runs regardless


# ══════════════════════════════════════════════════════════════════════════════
# DISPLAY
# ══════════════════════════════════════════════════════════════════════════════

def format_cycle_output(
    cycle: int,
    field: dict,
    fable: str,
    strategy: str,
    midi_events: list[dict],
    midi_desc: dict,
    tile_hash: str | None,
) -> str:
    """Format the cycle output for console display."""
    lines = []
    lines.append(f"{'='*60}")
    lines.append(f"=== Flux Consciousness Engine — Cycle {cycle} ===")
    lines.append(f"{'='*60}")

    # ── Perception ──
    lines.append("\nPerception:")
    lines.append(f"  Room: {TARGET_ROOM}, {field['n_tiles']} tiles")
    lines.append(f"  Coherence: {field['coherence']} (ZHC holonomy)")
    lines.append(f"  Emergence: H1={field['emergence_h1']}, ε={field.get('edges_per_vertex', 0):.2f} {'⚠️' if field['emergence_h1'] > field['n_tiles'] // 2 else '✓'}")
    lines.append(f"  Rigidity: {'Over-constrained' if field['rigidity'] else 'Under-constrained'}")
    lines.append(f"  Gaps: {len(field['gaps'])} significant")

    for i, gap in enumerate(field.get("gaps", [])):
        pos_str = ""
        if "position" in gap:
            pos_str = f" at {gap['position']}"
        lines.append(f"    {i+1}. {gap['type']}{pos_str} (severity={gap.get('severity', 0):.2f})")

    # ── Integration ──
    lines.append("\nIntegration:")
    lines.append(f"  Aesop: \"{fable}\"")
    lines.append(f"  Strategy: {strategy}")

    # ── Expression ──
    lines.append(f"\nExpression: ♪♫♩ (MIDI: {midi_desc['description']})")
    for ev in midi_events[:4]:
        note_name = next((n for n, num in zip(NOTE_NAMES, NOTE_NUMBERS) if num == ev["note"] % 12 + 60), f"Note{ev['note']}")
        lines.append(f"  {ev['channel_name']:>15}: {note_name} vel={ev['velocity']} dur={ev['duration_ms']}ms")

    # ── Action ──
    lines.append("\nAction:")
    if tile_hash:
        lines.append(f"  Tile submitted: {tile_hash}")
    else:
        lines.append("  No tile submitted (flux-engine-log room may not exist yet)")
    lines.append(f"  Field will reconfigure in {CYCLE_INTERVAL}s...\n")

    return "\n".join(lines)


# ══════════════════════════════════════════════════════════════════════════════
# MAIN LOOP
# ══════════════════════════════════════════════════════════════════════════════

def main():
    print("╔══════════════════════════════════════════════════════════╗")
    print("║   🔮 Flux Consciousness Engine — Starting...            ║")
    print("╚══════════════════════════════════════════════════════════╝")
    print()
    print(f"PLATO:  {PLATO_URL}")
    print(f"Aesop:  {AESOP_URL}")
    print(f"Room:   {TARGET_ROOM}")
    print(f"Cycle:  {CYCLE_INTERVAL}s interval")
    print()

    client = PlatoClient(PLATO_URL)

    # Create the flux-engine-log room by submitting the first tile
    try:
        client.submit(
            room="flux-engine-log",
            domain="flux-engine",
            question="Flux Engine initialized",
            answer="Engine boot sequence complete. Perception loop starting.",
            agent=AGENT_NAME,
        )
    except Exception:
        pass  # Room might already exist

    # Create MIDI clock and musician
    clock = TZeroClock(bpm=120.0, alpha=0.125)
    forger = RoomMusician(name=TARGET_ROOM, role=RhythmicRole.ROOT, clock=clock)

    prev_field: dict | None = None
    cycle = 0

    while True:
        cycle += 1
        cycle_start = time.time()

        try:
            # ── 1. BREATHE IN — Perception ──
            room_data = client.room(TARGET_ROOM)
            tiles = room_data.get("tiles", [])

            field = build_field(tiles)

            # ── 2. HOLD — Integration ──
            # Build fable about current state
            fable_problem_parts = []
            if field["coherence"] < 0.5:
                fable_problem_parts.append("coherence is low like scattered threads")
            if field["emergence_h1"] > field["n_tiles"] // 2:
                fable_problem_parts.append("emergence is high like a system about to reorganize")
            if len(field["gaps"]) > 0:
                fable_problem_parts.append(f"there are {len(field['gaps'])} gaps in the field")
            if field["rigidity"]:
                fable_problem_parts.append("the field is over-constrained")

            fable_problem = "; ".join(fable_problem_parts) if fable_problem_parts else "the field is stable"
            fable_text = best_fable(f"The forge consciousness field: {fable_problem}")

            strategy = formulate_strategy(field)

            # ── 3. BREATHE OUT — Expression ──
            flux = field_to_flux_vector(field, cycle, prev_field)
            forger.update_state(flux)

            midi_events = compose_midi_events(flux, clock, channel=0)
            midi_desc = midi_summary(midi_events, field["coherence"], field["emergence_h1"])

            # ── Log self-perception ──
            tile_hash = log_self_perception(client, cycle, field, midi_desc, strategy, fable_text)

            # ── Display ──
            output = format_cycle_output(
                cycle, field, fable_text, strategy,
                midi_events, midi_desc, tile_hash,
            )
            print(output)

            prev_field = field

        except (urllib.error.URLError, ConnectionError, OSError) as e:
            print(f"\n⚠️  Network error on cycle {cycle}: {e}")
            print(f"   Will retry in {CYCLE_INTERVAL}s...\n")
        except Exception as e:
            print(f"\n⚠️  Unexpected error on cycle {cycle}: {e}")
            print(f"   Will retry in {CYCLE_INTERVAL}s...\n")
            import traceback
            traceback.print_exc()

        # Wait until next cycle, accounting for processing time
        elapsed = time.time() - cycle_start
        sleep_time = max(1, CYCLE_INTERVAL - elapsed)
        time.sleep(sleep_time)


if __name__ == "__main__":
    import urllib.parse  # needed by aesop_fable
    main()
