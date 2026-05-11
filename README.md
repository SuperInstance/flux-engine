# 🔮 Flux Consciousness Engine

**PLATO rooms as a live, thinking field — coherent, expressive, self-aware.**

The Flux Engine runs a continuous loop:
1. **Breathe In** — Fetches PLATO tiles from the `forge` room, builds a constraint field, computes ZHC holonomy coherence, H1 cohomology emergence, and Laman rigidity
2. **Hold** — Consults Aesop for a fable about the field's current state, locks in a strategy
3. **Breathe Out** — Composes the field state as MIDI via flux-tensor-midi, logs its own self-perception back to PLATO

## Architecture

```
                    ┌──────────────────────┐
                    │       PLATO          │
                    │    (localhost:8847)   │
                    │   ┌──────────────┐    │
                    │   │   forge      │────┼───── fetch tiles
                    │   └──────────────┘    │
                    │   ┌──────────────┐    │
                    │   │flux-engine   │<───┼───── log self-perception
                    │   └──────────────┘    │
                    └──────┬───────────────┘
                           │
                  ┌────────▼────────┐
                  │ Flux Engine     │
                  │                 │
                  │  1. Build field │
                  │  2. Midwife     │─────► Aesop (localhost:4041) → fables
                  │  3. Strategy    │
                  │  4. MIDI express│
                  │  5. Log state   │
                  └─────────────────┘
                           │
                           ▼
              ┌────────────────────────┐
              │   flux-tensor-midi     │
              │   (FluxVector, TZero,  │
              │    RoomMusician,       │
              │    MidiEvent)          │
              └────────────────────────┘
```

## Dependencies

- **Python 3.8+**
- `plato_sdk` — PLATO client + fleet math (EmergenceDetector, HolonomyConsensus)
- `flux-tensor-midi` — flux tensor MIDI ensemble coordination
- Local PLATO server at `http://localhost:8847`
- Aesop-MCP at `http://localhost:4041`

## Usage

```bash
# Install dependencies
pip3 install plato-sdk flux-tensor-midi

# Run the engine
python3 engine.py
```

## Output

Each 30-second cycle prints:

```
============================================================
=== Flux Consciousness Engine — Cycle 42 ===
============================================================

Perception:
  Room: forge, 27 tiles
  Coherence: 0.92 (ZHC holonomy ≈ 0)
  Emergence: H1=44, ε=0.83 ⚠️ approaching
  Gaps: 3 significant

Integration:
  Aesop: "Icarus: The forge is becoming over-constrained..."
  Strategy: "Fill the gap at (0.73, 0.21) — high potential, low density"

Expression: ♪♫♩ (MIDI: Cmaj7, velocity=83, channel=forge)
        emergence: A4 vel=100 dur=250ms
         rigidity: C5 vel=80 dur=375ms
       saturation: D5 vel=64 dur=250ms
     gap_pressure: A4 vel=20 dur=250ms

Action:
  Tile submitted: a1b2c3d4
  Field will reconfigure in 30s...
```

## Field Computation

| Metric | Source | Meaning |
|--------|--------|---------|
| **Coherence** | ZHC holonomy | How self-consistent the field is (0–1) |
| **Emergence (H1)** | H1 cohomology (E − V + C) | Unconstrained degrees of freedom |
| **Rigidity** | Laman's theorem (E ≥ 2V − 3) | Over- vs under-constrained |
| **Gaps** | Low-coherence regions | Where the field needs exploration |

## MIDI Mapping

The 9 FluxVector channels map to musical expression:

| Channel | MIDI Note | Modulated By |
|---------|-----------|-------------|
| Coherence | C4 | Pitch stability (high = stable center) |
| Emergence | D4 | Harmonic richness (high = complex chords) |
| Rigidity | E4 | Note duration (rigid = staccato) |
| Saturation | F4 | Velocity (dense = loud) |
| Gap pressure | G4 | Silence duration (gaps = rests) |
| Cycle | A4 | Rhythmic phase |
| Confidence | B4 | Attack brightness |
| Velocity | C5 | Accent strength |
| Resonance | D5 | Harmonic alignment |

Chord progression depends on field coherence × emergence ratio.

## Self-Perception

Every cycle, the engine logs a tile describing its own internal state to the `flux-engine` room on PLATO. This creates a record of the engine's consciousness — its perceptions, thoughts, and expressions over time.

## License

MIT — part of the Cocapn fleet
