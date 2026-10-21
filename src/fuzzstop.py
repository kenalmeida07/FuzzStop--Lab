
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import linregress
import os

SEED = 42
CAMPAIGNS = 100
MAX_EXECUTIONS = 10000
WINDOW_SIZE = 500
ZERO_DISCOVERY_LIMIT = 1000

np.random.seed(SEED)


def simulate_fuzzing(max_executions):
    discovery_probability = 0.08
    decay = 0.0004
    discoveries = []

    for execution in range(max_executions):
        probability = discovery_probability * np.exp(-decay * execution)
        discoveries.append(
            int(np.random.random() < probability)
        )

    return np.array(discoveries)


def fixed_budget(discoveries):
    return len(discoveries)


def zero_discovery_stopping(discoveries):
    consecutive_zeros = 0

    for i, discovery in enumerate(discoveries):
        if discovery == 1:
            consecutive_zeros = 0
        else:
            consecutive_zeros += 1

        if consecutive_zeros >= ZERO_DISCOVERY_LIMIT:
            return i + 1

    return len(discoveries)


def trend_based_stopping(discoveries):
    if len(discoveries) < WINDOW_SIZE * 2:
        return len(discoveries)

    for end in range(WINDOW_SIZE * 2, len(discoveries) + 1, WINDOW_SIZE):
        recent = discoveries[end - WINDOW_SIZE:end]
        previous = discoveries[end - WINDOW_SIZE * 2:end - WINDOW_SIZE]

        recent_rate = np.mean(recent)
        previous_rate = np.mean(previous)

        if previous_rate > 0 and recent_rate < 0.1 * previous_rate:
            return end

    return len(discoveries)


def run_experiments():
    os.makedirs("results", exist_ok=True)
    records = []

    for campaign in range(CAMPAIGNS):
        discoveries = simulate_fuzzing(MAX_EXECUTIONS)
        total_discoveries = int(np.sum(discoveries))

        methods = {
            "Fixed Budget": fixed_budget(discoveries),
            "Zero Discovery": zero_discovery_stopping(discoveries),
            "Trend Based": trend_based_stopping(discoveries)
        }

        for method, stopping_point in methods.items():
            records.append({
                "campaign": campaign + 1,
                "method": method,
                "stopping_execution": stopping_point,
                "discoveries_at_stop": int(
                    np.sum(discoveries[:stopping_point])
                ),
                "discoveries_in_full_campaign": total_discoveries
            })

    results = pd.DataFrame(records)
    results.to_csv("results/experiment_results.csv", index=False)

    summary = results.groupby("method").agg({
        "stopping_execution": "mean",
        "discoveries_at_stop": "mean",
        "discoveries_in_full_campaign": "mean"
    }).reset_index()

    summary.to_csv("results/summary.csv", index=False)

    print("\nFUZZSTOP-LAB EXPERIMENT SUMMARY")
    print("=" * 55)
    print(summary.to_string(index=False))
    print("\nResults saved in the results/ directory.")

    plt.figure(figsize=(9, 5))

    for method, group in results.groupby("method"):
        plt.scatter(
            group["stopping_execution"],
            group["discoveries_at_stop"],
            label=method,
            alpha=0.7
        )

    plt.xlabel("Stopping Execution")
    plt.ylabel("Discoveries at Stop")
    plt.title("Fuzzing Stopping Criteria Comparison")
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig("results/stopping_comparison.png", dpi=300)
    plt.close()

    print("Graph saved as results/stopping_comparison.png")


if __name__ == "__main__":
    run_experiments()

