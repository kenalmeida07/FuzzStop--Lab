
import json
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


def load_config():
    with open("config.json", "r", encoding="utf-8") as file:
        return json.load(file)


def simulate_fuzzing(max_executions, scenario, rng):
    discoveries = np.zeros(max_executions, dtype=int)

    initial = scenario["initial_probability"]
    decay = scenario["decay"]

    for i in range(max_executions):
        probability = initial * np.exp(-decay * i)

        if "burst_probability" in scenario:
            if rng.random() < scenario["burst_probability"]:
                probability = scenario["burst_discovery_probability"]

        probability = min(max(probability, 0.0), 1.0)
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
    for end in range(
        window_size * 2,
        len(discoveries) + 1,
        window_size
    ):
        previous = discoveries[
            end - 2 * window_size:end - window_size
        ]
        recent = discoveries[end - window_size:end]

        previous_rate = np.mean(previous)
        recent_rate = np.mean(recent)

        if previous_rate > 0 and recent_rate <= ratio * previous_rate:
            return end

    return len(discoveries)


def run_experiments():
    config = load_config()
    experiment = config["experiment"]
    criteria = config["stopping_criteria"]
    scenarios = config["scenarios"]

    rng = np.random.default_rng(experiment["random_seed"])
    campaigns = experiment["campaigns"]
    max_executions = experiment["maximum_executions"]

    os.makedirs("results", exist_ok=True)
    records = []

    for scenario_name, scenario in scenarios.items():
        for campaign in range(1, campaigns + 1):
            discoveries = simulate_fuzzing(
                max_executions, scenario, rng
            )
            full_total = int(np.sum(discoveries))

            methods = {}

            if criteria["fixed_budget"]["enabled"]:
                methods["Fixed Budget"] = fixed_budget(discoveries)

            if criteria["zero_discovery"]["enabled"]:
                methods["Zero Discovery"] = zero_discovery_stopping(
                    discoveries,
                    criteria["zero_discovery"]["consecutive_zero_limit"]
                )

            if criteria["trend_based"]["enabled"]:
                methods["Trend Based"] = trend_based_stopping(
                    discoveries,
                    criteria["trend_based"]["window_size"],
                    criteria["trend_based"]["discovery_rate_ratio"]
                )

            for method, stop in methods.items():
                found = int(np.sum(discoveries[:stop]))

                records.append({
                    "scenario": scenario_name,
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

    summary = results.groupby(["scenario", "method"]).agg(
        mean_stopping_execution=("stopping_execution", "mean"),
        mean_discoveries=("discoveries_at_stop", "mean"),
        mean_discoveries_missed=("discoveries_missed", "mean"),
        mean_budget_used_percent=("budget_used_percent", "mean")
    ).reset_index()

    summary.to_csv("results/summary.csv", index=False)

    print("\nFUZZSTOP-LAB: MULTI-SCENARIO RESULTS")
    print("=" * 90)
    print(summary.round(3).to_string(index=False))
    print("\nAll results are simulated, not real-world fuzzing measurements.")

    for scenario_name, group in summary.groupby("scenario"):
        plt.figure(figsize=(9, 5))

        plt.bar(
            group["method"],
            group["mean_budget_used_percent"]
        )

        plt.ylabel("Average Budget Used (%)")
        plt.xlabel("Stopping Criterion")
        plt.title(f"Budget Usage: {scenario_name}")
        plt.ylim(0, 100)
        plt.tight_layout()

        filename = f"results/{scenario_name}_budget_comparison.png"
        plt.savefig(filename, dpi=300)
        plt.close()

        print(f"Generated: {filename}")

    print("\nGenerated:")
    print("results/experiment_results.csv")
    print("results/summary.csv")


if __name__ == "__main__":
    run_experiments()
