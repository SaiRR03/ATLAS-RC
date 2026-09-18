"""
ATLAS-RC v1.0.0
A compact reproduction of the frozen experiment.

Expected input:
    dataset.csv

Target:
    investmentUSD / powerCapacityMW

Frozen similarity features:
    powerCapacityMW, totalSquareFeet
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from sklearn.model_selection import train_test_split, KFold
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import NearestNeighbors
from sklearn.metrics import mean_absolute_error, mean_squared_error


RANDOM_STATE = 42
FEATURES = ["powerCapacityMW", "totalSquareFeet"]
K_VALUES = [3, 5, 10, 15, 20, 30, 50, 75, 100]


def prepare_data(path="dataset.csv"):
    df = pd.read_csv(path)

    required = ["investmentUSD", "powerCapacityMW", "totalSquareFeet"]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"Dataset is missing required columns: {missing}")

    cost_data = df[
        df["investmentUSD"].notna()
        & (df["investmentUSD"] > 0)
        & df["powerCapacityMW"].notna()
        & (df["powerCapacityMW"] > 0)
    ].copy()

    cost_data["investmentPerMW"] = (
        cost_data["investmentUSD"] / cost_data["powerCapacityMW"]
    )

    experiment_data = cost_data[
        cost_data[FEATURES].notna().all(axis=1)
        & (cost_data["totalSquareFeet"] > 0)
        & (cost_data["investmentPerMW"] > 0)
    ].copy()

    return df, cost_data, experiment_data


def predict_reference_class(train, validation, k):
    scaler = StandardScaler()
    x_train = scaler.fit_transform(train[FEATURES])
    x_val = scaler.transform(validation[FEATURES])

    y_train = train["investmentPerMW"].to_numpy()

    knn = NearestNeighbors(n_neighbors=k, metric="euclidean")
    knn.fit(x_train)
    _, neighbour_indices = knn.kneighbors(x_val)

    return np.array([
        np.median(y_train[neighbours])
        for neighbours in neighbour_indices
    ])


def evaluate_k_cv(data, k_values=K_VALUES, n_splits=5):
    kfold = KFold(
        n_splits=n_splits,
        shuffle=True,
        random_state=RANDOM_STATE
    )

    rows = []

    for k in k_values:
        fold_maes = []

        for train_idx, val_idx in kfold.split(data):
            train = data.iloc[train_idx].copy()
            validation = data.iloc[val_idx].copy()

            predictions = predict_reference_class(train, validation, k)

            fold_maes.append(
                mean_absolute_error(
                    validation["investmentPerMW"],
                    predictions
                )
            )

        rows.append({
            "k": k,
            "mean_cv_mae": np.mean(fold_maes),
            "std_cv_mae": np.std(fold_maes)
        })

    return pd.DataFrame(rows).sort_values("mean_cv_mae")


def global_cv_mae(data, n_splits=5):
    kfold = KFold(
        n_splits=n_splits,
        shuffle=True,
        random_state=RANDOM_STATE
    )

    fold_maes = []

    for train_idx, val_idx in kfold.split(data):
        train = data.iloc[train_idx]
        validation = data.iloc[val_idx]

        prediction = train["investmentPerMW"].median()
        predictions = np.full(len(validation), prediction)

        fold_maes.append(
            mean_absolute_error(
                validation["investmentPerMW"],
                predictions
            )
        )

    return float(np.mean(fold_maes))


def final_locked_test(development_data, test_data, k):
    y_test = test_data["investmentPerMW"].to_numpy()

    rcf_predictions = predict_reference_class(
        development_data,
        test_data,
        k
    )

    global_median = development_data["investmentPerMW"].median()
    global_predictions = np.full(len(test_data), global_median)

    global_mae = mean_absolute_error(y_test, global_predictions)
    rcf_mae = mean_absolute_error(y_test, rcf_predictions)

    global_rmse = np.sqrt(
        mean_squared_error(y_test, global_predictions)
    )
    rcf_rmse = np.sqrt(
        mean_squared_error(y_test, rcf_predictions)
    )

    mae_change = ((global_mae - rcf_mae) / global_mae) * 100

    return {
        "n_train": len(development_data),
        "n_test": len(test_data),
        "k": k,
        "global_mae": global_mae,
        "rcf_mae": rcf_mae,
        "global_rmse": global_rmse,
        "rcf_rmse": rcf_rmse,
        "mae_change": mae_change
    }


def save_final_figure(result, path="figures/atlas_final_test.png"):
    model_names = [
        "Global outside view",
        "ML-selected reference class"
    ]
    mae_values = [
        result["global_mae"] / 1e6,
        result["rcf_mae"] / 1e6
    ]

    fig, ax = plt.subplots(figsize=(8, 6))
    bars = ax.bar(model_names, mae_values)

    for bar, value in zip(bars, mae_values):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height(),
            f"${value:.2f}m/MW",
            ha="center",
            va="bottom",
            fontsize=12,
            fontweight="bold"
        )

    ax.set_ylabel("Mean Absolute Error ($m/MW)")
    ax.set_title(
        "ATLAS RCF: Locked Out-of-Sample Performance",
        fontsize=14,
        fontweight="bold"
    )
    fig.text(
        0.5,
        0.91,
        f"RCF MAE change relative to global baseline: "
        f"{result['mae_change']:+.2f}%",
        ha="center",
        fontsize=10
    )
    ax.set_ylim(0, max(mae_values) * 1.15)
    plt.tight_layout(rect=[0, 0, 1, 0.90])
    plt.savefig(path, dpi=300, bbox_inches="tight")
    plt.close()


def main():
    _, _, experiment_data = prepare_data("dataset.csv")

    development_data, test_data = train_test_split(
        experiment_data,
        test_size=0.20,
        random_state=RANDOM_STATE
    )

    k_results = evaluate_k_cv(development_data)
    best_row = k_results.loc[k_results["mean_cv_mae"].idxmin()]
    best_k = int(best_row["k"])
    best_rcf_cv_mae = float(best_row["mean_cv_mae"])
    baseline_cv_mae = global_cv_mae(development_data)

    final = final_locked_test(
        development_data,
        test_data,
        best_k
    )

    print("=" * 60)
    print("ATLAS-RC v1.0.0")
    print("=" * 60)
    print(f"Analytical sample:     {len(experiment_data)}")
    print(f"Development projects:  {len(development_data)}")
    print(f"Locked test projects:  {len(test_data)}")
    print(f"Selected k:            {best_k}")
    print(f"Global CV MAE:         ${baseline_cv_mae/1e6:.2f}m/MW")
    print(f"RCF CV MAE:            ${best_rcf_cv_mae/1e6:.2f}m/MW")
    print()
    print("LOCKED TEST")
    print(f"Global MAE:            ${final['global_mae']/1e6:.2f}m/MW")
    print(f"RCF MAE:               ${final['rcf_mae']/1e6:.2f}m/MW")
    print(f"Global RMSE:           ${final['global_rmse']/1e6:.2f}m/MW")
    print(f"RCF RMSE:              ${final['rcf_rmse']/1e6:.2f}m/MW")
    print(f"MAE change vs global:  {final['mae_change']:+.2f}%")

    save_final_figure(final)


if __name__ == "__main__":
    main()
