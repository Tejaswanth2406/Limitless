# Limitless — API Reference

## Top-Level: `Limitless`

```python
from Limitless.api.limitless_api import Limitless

lm = Limitless(name="MyWorld")
```

### Methods

| Method | Signature | Description |
|---|---|---|
| `define` | `(label, state={}, entropy=0.5) → self` | Add an entity |
| `connect` | `(a, b, weight=1.0) → self` | Link two entities |
| `observe` | `(target, type, raw, priority=1.0) → self` | Inject observation |
| `tick` | `(n=1) → self` | Advance n simulation steps |
| `think` | `(context=None) → SwarmReport` | Run agent swarm |
| `project` | `(label, horizon=5) → str` | Project entity's future |
| `render` | `(report) → str` | Format a SwarmReport |
| `table` | `() → str` | Print entity table |
| `summary` | `() → None` | Print world summary |
| `snapshot` | `() → dict` | Capture current state |
| `entity` | `(label) → TemporalNode` | Get entity by label |
| `entities` | `() → List[TemporalNode]` | All entities |

---

## Simulation: `TemporalWorld`

```python
from Limitless.simulation.world import TemporalWorld
world = TemporalWorld("W")
world.add_entity("market", {"price": 100.0}, entropy=0.4)
world.inject_event("market", {"type": "text", "raw": "crash"})
world.step(n=10)
report = world.analyse()
```

## Simulation: `Scenario`

```python
from Limitless.simulation.scenario import Scenario
s = (
    Scenario("Base")
    .add_entity("a", entropy=0.3)
    .add_entity("b", entropy=0.6)
    .add_link("a", "b", weight=0.8)
    .add_event("a", {"type": "text", "raw": "signal"}, at_step=3)
)
s.run(steps=10)
fork = s.fork("Alternative")
```

---

## Agents

```python
from Limitless.agents.swarm import AgentSwarm
swarm = AgentSwarm(trajectory_horizon=5, trajectory_branches=3)
report = swarm.run(nodes, context={"goal": "stability"})
print(report.narrative())
print(report.risks())
print(report.confidence())
```

### Individual agents
```python
from Limitless.agents import (
    ObserverAgent, HistorianAgent, FuturistAgent,
    ContradictionHunterAgent, NoveltyAgent, SynthesizerAgent
)
obs = ObserverAgent()
result = obs.run(nodes)
print(result.findings)
print(result.confidence)
```

---

## Engines

```python
from Limitless.engine import EntropyEngine, TrajectoryEngine, OmegaOptimizer

# Entropy
ee = EntropyEngine()
ee.rank_nodes(nodes)                        # by importance
ee.allocate_compute(nodes, budget=1.0)     # compute allocation
ee.detect_phase_transition(nodes)          # critical junctions

# Trajectories
te = TrajectoryEngine(horizon=5, branching_factor=3)
trajectories = te.project(node)
best = te.select_best(trajectories)

# Omega Optimization
oo = OmegaOptimizer(lr=0.05, max_steps=100)
result = oo.optimise(node, apply=True)     # move node toward H*=0.5
print(result.summary())
```

---

## Utilities

```python
# Logger
from Limitless.utils.logger import get_logger, Level
log = get_logger("my.module", level=Level.DEBUG)
log.info("something happened", node="market", entropy=0.7)

# Serialiser
from Limitless.utils.serialiser import save_nodes, load_nodes
save_nodes(nodes, "checkpoint.json")
nodes = load_nodes("checkpoint.json")

# Math
from Limitless.utils.math_utils import omega_matrix, entropy_gradient
matrix = omega_matrix(nodes)   # N×N influence matrix
grad   = entropy_gradient(nodes)

# Formatters
from Limitless.utils.formatters import format_node_table, format_swarm_report
print(format_node_table(nodes))
```

---

## Visualiser

```python
from Limitless.visualiser import FieldVisualiser
vis = FieldVisualiser(width=64, color=True)
print(vis.entropy_bars(nodes))
print(vis.trajectory_sparklines(nodes))
print(vis.phase_portrait(nodes))
print(vis.influence_matrix(nodes))
print(vis.full_report(field))
```

---

## Benchmarks

```python
from Limitless.benchmarks import BenchmarkRunner
from Limitless.benchmarks.temporal_benchmarks import *

runner = BenchmarkRunner()
runner.add_all([
    BenchmarkOmegaConvergence(),
    BenchmarkFieldPropagation(),
    BenchmarkSwarmLatency(),
    BenchmarkTrajectoryAccuracy(),
    BenchmarkEntropyExpansion(),
])
results = runner.run_all()
runner.print_report(results)
```
