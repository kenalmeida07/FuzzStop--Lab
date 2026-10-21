
import json
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


def load_config():
    with open("config.json", "r", encoding="utf-8") as file:
        return json.load(file)


def simulate_fuzzing(max_executions, initial_probability, decay, rng):
    discoveries = np.zeros(max_executions, dtype=int)

    for i in range(max_executions):
        probability = initial_probability * np.exp(-decay * i)
        discoveries[i] = int(rng.random() < probability)

    return discoveries


def fixed_budget(discoveries):
    return len(discoveries)


def zero_discovery_stopping(discoveries, limit):
    consecutive_zeros = 0

    for i, discovery in enumerate(discoveries):
        if discovery:
            consecutive_zeros = 0
        else:
            consecutive_zeros += 1

        if consecutive_zeros >= limit:
            return i + 1

    return len(discoveries)


def trend_based_stopping(discoveries, window_size, ratio):
    for end in range(window_size * 2, len(discoveries) + 1, window_size):
        previous = discoveries[end - 2 * window_size:end - window_size]
        recent = discoveries[end - window_size:end]

        previous_rate = np.mean(previous)
        recent_rate = np.mean(recent)

        if previous_rate > 0 and recent_rate <= ratio * previous_rate:
            return end

    return len(discoveries)


def run_experiments():
    config = load_config()

    experiment = config["experiment"]
    simulation = config["simulation"]
    criteria = config["stopping_criteria"]

    campaigns = experiment["campaigns"]
    max_executions = experiment["maximum_executions"]

    rng = np.random.default_rng(experiment["random_seed"])
    os.makedirs("results", exist_ok=True)

    records = []

    for campaign in range(1, campaigns + 1):
        discoveries = simulate_fuzzing(
            max_executions,
            simulation["initial_discovery_probability"],
            simulation["discovery_probability_decay"],
            rng
        )

        full_total = int(np.sum(discoveries))
        stopping_points = {}

        if criteria["fixed_budget"]["enabled"]:
            stopping_points["Fixed Budget"] = fixed_budget(discoveries)

        if criteria["zero_discovery"]["enabled"]:
            stopping_points["Zero Discovery"] = zero_discovery_stopping(
                discoveries,
                criteria["zero_discovery"]["consecutive_zero_limit"]
            )

        if criteria["trend_based"]["enabled"]:
            stopping_points["Trend Based"] = trend_based_stopping(
                discoveries,
                criteria["trend_based"]["window_size"],
                criteria["trend_based"]["discovery_rate_ratio"]
            )

        for method, stop in stopping_points.items():
            found = int(np.sum(discoveries[:stop]))

            records.append({
                "campaign": campaign,
                "method": method,
                "stopping_execution": stop,
                "discoveries_at_stop": found,
                "full_budget_discoveries": full_total,
                "discoveries_missed": full_total - found,
                "budget_used_percent": 100 * stop / max_executions
            })

    results = pd.DataFrame(records)
    results.to_csv("results/experiment_results.csv", index=False)

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
    print("\nThese are simulated results, not real fuzzing measurements.")

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
    print("results/experiment_results.csv")
    print("results/summary.csv")
    print("results/stopping_comparison.png")


if __name__ == "__main__":
    run_experiments()
