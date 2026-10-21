# FuzzStop-Lab: When Should You Stop Fuzzing?

## Research Overview

Fuzzing is a software testing technique that supplies inputs to a program to discover crashes, bugs, and potential vulnerabilities. However, fuzzing campaigns can consume substantial computational resources, making the decision of when to stop an important research problem.

**FuzzStop-Lab** is a simulation-based research project that compares three stopping criteria under different discovery patterns.

The goal is to investigate the trade-off between computational budget and discoveries retained when a fuzzing campaign terminates early.

## Research Objectives

- Compare fixed-budget, zero-discovery, and trend-based stopping criteria.
- Evaluate their behaviour under different simulated discovery patterns.
- Measure execution budget usage and discoveries missed by early stopping.
- Identify situations in which early termination may reduce testing costs.

## Stopping Criteria

1. **Fixed Budget:** Runs until the maximum execution budget is reached.
2. **Zero Discovery:** Stops after a configured number of consecutive executions produce no discoveries.
3. **Trend Based:** Compares discovery rates over consecutive windows and stops when the recent rate falls below a configured fraction of the previous rate.

## Experimental Methodology

The experiment uses Python, NumPy, pandas, and Matplotlib.

- Random seed: 42
- Campaigns per scenario: 100
- Maximum executions per campaign: 10,000
- Discovery model: Random binary discovery events with scenario-dependent probabilities
- Scenarios: Fast decay, slow decay, and intermittent discovery probability

Each stopping criterion is evaluated against the same simulated campaign. Results are aggregated across campaigns for each scenario.

## Experimental Results

### Fast Decay

| Stopping Criterion | Mean Executions | Mean Discoveries Missed | Mean Budget Used |
|---|---:|---:|---:|
| Fixed Budget | 10,000 | 0.00 | 100.00% |
| Trend Based | 4,910 | 2.50 | 49.10% |
| Zero Discovery | 5,787.39 | 1.26 | 57.87% |

In the fast-decay scenario, trend-based stopping reduced the average execution budget by approximately 50.9%, while missing an average of 2.50 discoveries compared with completing the full simulated campaign.

### Slow Decay

All three methods used the full 10,000-execution budget on average. Neither early stopping criterion terminated a campaign before the budget limit under this configuration.

### Intermittent Discovery

All three methods used the full execution budget on average. The intermittent scenario generated a relatively high number of simulated discoveries, preventing the configured early stopping conditions from triggering.

## Metrics

The experiment records:

- Mean stopping execution
- Mean discoveries observed at stopping
- Mean discoveries missed compared with the full simulated campaign
- Mean percentage of execution budget used

## Repository Structure

```text
FuzzStop-Lab/
├── README.md
├── config.json
├── requirements.txt
├── src/
│   └── fuzzstop.py
├── experiments/
│   └── run_experiments.py
└── results/
    ├── experiment_results.csv
    ├── summary.csv
    ├── fast_decay_budget_comparison.png
    ├── slow_decay_budget_comparison.png
    └── intermittent_budget_comparison.png
```

## Reproducibility

Install the required dependencies:

```bash
python -m pip install -r requirements.txt
```

Run the experiment from the repository root:

```bash
python experiments/run_experiments.py
```

The program generates detailed campaign-level results, a summary CSV, and scenario-specific budget comparison graphs in the `results/` directory.

## Limitations

This project currently uses a simplified simulation rather than a real fuzzing engine. A discovery event represents a simulated event, not necessarily a unique software bug or vulnerability.

The intermittent scenario currently models per-execution random changes in discovery probability rather than sustained, temporally correlated bursts. The trend-based criterion is a heuristic and has not been established as a statistically optimal stopping rule.

The results should therefore be interpreted as preliminary simulation findings, not evidence of performance on real-world software targets.

## Future Work

- Integrate a real fuzzing engine and collect actual execution data.
- Model temporally correlated discovery bursts.
- Test additional stopping thresholds and window sizes.
- Repeat experiments across more random seeds.
- Evaluate statistical uncertainty and compare stopping decisions across multiple target programs.

## Author

**Kenneth Almeida**

Research project: *When Should You Stop Fuzzing? A Comparative Evaluation of Statistical Stopping Criteria*
