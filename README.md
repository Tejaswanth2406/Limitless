# Limitless
### *Temporal Reality Operating System*

> **Reality is not something that exists. Reality is the endless act through which existence, time, possibility, and awareness continuously generate one another.**

---

## What is Limitless?

Limitless is a Python framework built on a radical premise:

```
Standard AI:       Tokens → Embeddings → Attention → Prediction
Limitless:   Reality States → Temporal Dynamics → Entropy Flows → Reality Projection
```

Instead of treating knowledge as static facts, Limitless models every concept,
entity, and system as a **living temporal process** — described by its history,
current configuration, entropy signature, and projected future trajectories.

---

## Core Concepts

| Concept | Standard View | Limitless View |
|---|---|---|
| **Entity** | Object with properties | Process described by state transitions |
| **Distance** | Spatial separation | Difference in temporal state |
| **Gravity** | Force bending spacetime | Mass compressing temporal flow |
| **Entropy** | Disorder | Expansion of possibility space |
| **Consciousness** | Brain output | Temporal self-awareness |
| **Knowledge** | Stored facts | Evolving temporal relationships |

---

## Architecture

```
┌─────────────────────────────────────────────┐
│                 Limitless API               │  ← User-facing facade
├─────────────────────────────────────────────┤
│             Agent Swarm Layer               │  ← Observer · Historian · Futurist · Synthesizer
├─────────────────────────────────────────────┤
│    Entropy Engine   │  Trajectory Engine    │  ← Reasoning engines
│    Reality Compiler │                       │
├─────────────────────────────────────────────┤
│  Temporal Kernel → Temporal Field           │  ← Core OS layer
│  TemporalNode   → TemporalState             │
└─────────────────────────────────────────────┘
```

---

## Quick Start

```python
from Limitless.api.limitless_api import Limitless

# Build a temporal world
lm = (
    Limitless("MyWorld")
    .define("market",    {"price": 100.0},  entropy=0.35)
    .define("sentiment", {"score": 0.7},    entropy=0.55)
    .connect("market", "sentiment", weight=0.8)
)

# Inject observations
lm.observe("market", "text", "The market is declining rapidly")
lm.observe("market", "numeric", {"volume": 9500, "volatility": 0.8})

# Advance temporal reality
lm.tick(10)

# Reason with the agent swarm
report = lm.think()
print(lm.render(report))

# Project one entity's future
print(lm.project("market", horizon=5))
```

---

## Scenarios & Counterfactuals

```python
from Limitless.simulation.scenario import Scenario

# Build a base scenario
base = (
    Scenario("Baseline")
    .add_entity("company", {"revenue": 1_000_000}, entropy=0.3)
    .add_entity("market",  {"index": 4200},        entropy=0.4)
    .add_link("market", "company", weight=0.7)
    .add_event("market", {"type": "text", "raw": "conditions stable"}, at_step=3)
)

# Fork it: what if a crisis hit instead?
crisis = base.fork("CrisisTimeline")
crisis.add_event(
    "market",
    {"type": "event", "raw": {"type": "crash", "severity": 0.95}},
    at_step=3, priority=9.0,
)

base.run(steps=10)
crisis.run(steps=10)
```

---

## The Temporal State Graph

Every entity is a `TemporalNode` containing:

```python
TemporalNode {
    label:         str
    current_state: TemporalState {
        state_vector:    Dict        # current configuration
        entropy:         float       # 0=ordered  1=chaotic
        coherence:       float       # 1 - entropy
        momentum:        float       # rate of change
        novelty:         float       # difference from last state
        history:         List[State] # full audit trail
        potential_paths: List[State] # projected futures
    }
    edges:         Dict[id, weight]  # temporal resonance links
}
```

The **Ω (Omega) score** measures a node's temporal complexity:

```
Ω = coherence × entropy × (1 + projection_potential)
```

High Ω nodes are at critical junctions — maximally generative.

---

## Agent Swarm

The `AgentSwarm` runs four specialist agents in sequence:

| Agent | Question Answered |
|---|---|
| **Observer** | What is true right now? |
| **Historian** | How did we get here? |
| **Futurist** | What could happen next? |
| **Synthesizer** | What does everything mean together? |

```python
from Limitless.agents.swarm import AgentSwarm

swarm = AgentSwarm(trajectory_horizon=5, trajectory_branches=3)
report = swarm.run(nodes)
print(report.narrative())
print(report.risks())
```

---

## Running Tests

```bash
pip install pytest
pytest Limitless/tests/ -v
```

---

## Running the Demo

```bash
python Limitless/demo.py
```

---

## Mathematical Foundation

The framework is built on four core axioms:

1. **Reality = Transformations** (not objects)
2. **Distance = Temporal Difference** (not spatial separation)  
3. **Knowledge = State History + State Potential**
4. **Entropy = Number of Reachable States**

The global complexity metric:

```
Ω = Σ(Sᵢ · Eᵢ · Pᵢ)

S = state coherence
E = entropy
P = projection potential
```

---

## Philosophy → Engineering

| Philosophy | Implementation |
|---|---|
| Time is generative substrate | `TemporalField` propagates influence |
| Matter is frozen time | High-coherence, low-entropy nodes |
| Entropy = possibility expansion | `EntropyEngine` allocates compute to high-entropy states |
| Consciousness navigates temporal flow | `AgentSwarm` selects optimal trajectories |
| No universal clock | Each node has its own temporal rate |

---

## License

MIT
