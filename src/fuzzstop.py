
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

SEED = 42
CAMPAIGNS = 100
MAX_EXECUTIONS = 10000
WINDOW_SIZE = 500
ZERO_DISCOVERY_LIMIT = 1000
TREND_RATIO = 0.10


def simulate_fuzzing(max_executions, rng):
    discoveries = np.zeros(max_executions, dtype=int)

    for i in range(max_executions):
        probability = 0.08 * np.exp(-0.0004 * i)
        discoveries[i] = int(rng.random() < probability)

    return discoveries


def fixed_budget(discoveries):
    return len(discoveries)


def zero_discovery_stopping(discoveries):
    consecutive_zeros = 0

    for i, discovery in enumerate(discoveries):
        if discovery:
            consecutive_zeros = 0
        else:
            consecutive_zeros += 1

        if consecutive_zeros >= ZERO_DISCOVERY_LIMIT:
            return i + 1

    return len(discoveries)


def trend_based_stopping(discoveries):
    for end in range(
        WINDOW_SIZE * 2,
        len(discoveries) + 1,
        WINDOW_SIZE
    ):
        previous = discoveries[
            end - WINDOW_SIZE * 2:end - WINDOW_SIZE
        ]
        recent = discoveries[end - WINDOW_SIZE:end]

        previous_rate = np.mean(previous)
        recent_rate = np.mean(recent)

        if (
            previous_rate > 0
            and recent_rate <= TREND_RATIO * previous_rate
        ):
            return end

    return len(discoveries)


def run_experiments():
    os.makedirs("results", exist_ok=True)
    rng = np.random.default_rng(SEED)
    records = []

    for campaign in range(1, CAMPAIGNS + 1):
        discoveries = simulate_fuzzing(MAX_EXECUTIONS, rng)
        full_total = int(np.sum(discoveries))

        stopping_methods = {
            "Fixed Budget": fixed_budget(discoveries),
            "Zero Discovery": zero_discovery_stopping(discoveries),
            "Trend Based": trend_based_stopping(discoveries)
        }

        for method, stop in stopping_methods.items():
            found = int(np.sum(discoveries[:stop]))

            records.append({
                "campaign": campaign,
                "method": method,
                "stopping_execution": stop,
                "discoveries_at_stop": found,
                "full_budget_discoveries": full_total,
                "discoveries_missed": full_total - found,
                "budget_used_percent": 100 * stop / MAX_EXECUTIONS
            })

    results = pd.DataFrame(records)
    results.to_csv(
        "results/experiment_results.csv", index=False
    )

    summary = results.groupby("method").agg(
        mean_stopping_execution=("stopping_execution", "mean"),
        mean_discoveries=("discoveries_at_stop", "mean"),
        mean_discoveries_missed=("discoveries_missed", "mean"),
        mean_budget_used_percent=("budget_used_percent", "mean")
    ).reset_index()

    summary.to_csv("results/summary.csv", index=False)

    print("\nFUZZSTOP-LAB: SIMULATION RESULTS")
    print("=" * 65)
    print(summary.round(3).to_string(index=False))
    print("\nNote: These are simulated results, not real fuzzing measurements.")

    plt.figure(figsize=(9, 5))

    for method, group in results.groupby("method"):
        plt.scatter(
            group["stopping_execution"],
            group["discoveries_at_stop"],
            label=method,
            alpha=0.65
        )

    plt.xlabel("Stopping Execution")
    plt.ylabel("Discovery Events at Stop")
    plt.title("Comparison of Fuzzing Stopping Criteria")
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig("results/stopping_comparison.png", dpi=300)
    plt.close()

    print("\nGenerated:")
    print("- results/experiment_results.csv")
    print("- results/summary.csv")
    print("- results/stopping_comparison.png")


if __name__ == "__main__":
    run_experiments()
