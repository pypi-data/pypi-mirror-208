from . import metadata
from .metrics import get_multimodel_metrics, euclid_dist
from functools import partial

import numpy as np

from typing import Optional, Any


def _concat(objs: dict, remove_idx: np.ndarray) -> np.ndarray:
    vals = [objs["target"], objs["embedding"][remove_idx], objs["candidate"]]
    vals = [np.atleast_1d(val) for val in vals]
    return np.concatenate(vals, axis=0)


def choose_k(metrics: dict, k: int = 16, models: Optional[list[str]] = None) -> Any:
    remove_idx = (metrics["distances"]["embedding_target"] != 0).flatten()
    concat = partial(_concat, remove_idx=remove_idx)

    if models is None:
        models = list(metrics["representations"].keys())

    paths = concat(metrics["paths"])
    k = min(k, paths.shape[0])
    results = {}

    for model in models:
        # Initial setup
        selected = [0]
        reprs = concat(metrics["representations"][model])
        parent_idx = np.arange(reprs.shape[0])[1:]
        target = reprs[[0], :]
        current = reprs[[0], :]

        # Selection process
        while current.shape[0] < k:
            n = current.shape[0]
            candidates = reprs[parent_idx]

            current_mean = current.mean(axis=0)[None, :]
            current_mean *= n / (n + 1)

            g = candidates - current_mean
            g /= n + 1

            r = target - current_mean

            distances = euclid_dist(g, r).flatten()
            best_idx = distances.argmin()
            selected.append(parent_idx[best_idx])

            current = np.concatenate((current, candidates[(best_idx,), :]), axis=0)
            parent_idx = np.delete(parent_idx, best_idx)

        # Stats
        threshold = metadata.THRESHOLDS[model]["euclidean"]

        accuracy = euclid_dist(current.mean(axis=0)[None, :], target).flatten()[0]
        accuracy /= threshold

        variance = (current / np.linalg.norm(target)).var(axis=0)
        average_variance = variance.mean()
        variance_variance = variance.var()

        target_distance = (euclid_dist(current, target) / threshold).mean()

        results[model] = {
            "selected": selected,
            "paths": paths[selected],
            "accuracy": accuracy,
            "variance": average_variance,
            "variance_variance": variance_variance,
            "target_distance": target_distance,
        }

    return results


def choose_k_concat(
    metrics: dict, k: int = 16, models: Optional[list[str]] = None
) -> Any:
    remove_idx = (metrics["distances"]["embedding_target"] != 0).flatten()
    concat = partial(_concat, remove_idx=remove_idx)

    if models is None:
        models = list(metrics["representations"].keys())

    paths = concat(metrics["paths"])
    k = min(k, paths.shape[0])

    reprs = []
    threshold = 0
    for model in models:
        model_reprs = concat(metrics["representations"][model])
        norm = np.linalg.norm(model_reprs)
        reprs.append(model_reprs / norm)
        threshold += metadata.THRESHOLDS[model]["euclidean_l2"] * model_reprs.shape[1]
    reprs = np.concatenate(reprs, axis=1)
    parent_idx = np.arange(reprs.shape[0])[1:]
    threshold /= reprs.shape[1]

    target = reprs[[0], :]
    current = reprs[[0], :]
    selected = [0]

    # Selection process
    while current.shape[0] < k:
        n = current.shape[0]
        candidates = reprs[parent_idx]

        current_mean = current.mean(axis=0)[None, :]
        current_mean *= n / (n + 1)

        g = candidates - current_mean
        g /= n + 1

        r = target - current_mean

        distances = euclid_dist(g, r).flatten()
        best_idx = distances.argmin()
        selected.append(parent_idx[best_idx])

        current = np.concatenate((current, candidates[(best_idx,), :]), axis=0)
        parent_idx = np.delete(parent_idx, best_idx)

    # Stats
    accuracy = euclid_dist(current.mean(axis=0)[None, :], target).flatten()[0]
    accuracy /= threshold

    variance = (current / np.linalg.norm(target)).var(axis=0)
    average_variance = variance.mean()
    variance_variance = variance.var()

    target_distance = (euclid_dist(current, target) / threshold).mean()

    return {
        "selected": selected,
        "paths": paths[selected],
        "accuracy": accuracy,
        "variance": average_variance,
        "variance_variance": variance_variance,
        "target_distance": target_distance,
    }


def search(
    metrics: dict, k: int = 16, models: Optional[list[str]] = None
) -> dict[str, Any]:
    if models is None:
        models = list(metrics["representations"].keys())

    if len(models) > 1:
        return choose_k_concat(metrics, k, models)
    return choose_k(metrics, k, models)[models[0]]


def main():
    MODEL = "VGG-Face"

    metadata.create_dirs()
    metrics = get_multimodel_metrics([MODEL])

    target = np.array(metrics["representations"][MODEL]["target"])
    candidates = np.array(metrics["representations"][MODEL]["candidate"])
    parent_candidates = candidates[...]

    N = 5

    current = target[...]
    parent_idx = np.arange(candidates.shape[0])
    selection_idx = []

    while current.shape[0] < N:
        n = current.shape[0]
        current_mean = current.mean(axis=0)[None, :] * (n / (n + 1))
        g = (candidates - current_mean) / (n + 1)
        r = target - current_mean

        distances = euclid_dist(g, r).flatten()
        best_idx = distances.argmin()
        best_parent_idx = parent_idx[best_idx]
        selection_idx.append(best_parent_idx)

        current = np.concatenate((current, candidates[(best_idx,), :]), axis=0)
        candidates = np.delete(candidates, best_idx, axis=0)
        parent_idx = np.delete(parent_idx, best_idx)

    score = euclid_dist(current.mean(axis=0)[None, :], target).flatten()[0]
    print(score / metadata.THRESHOLDS[MODEL]["euclidean"])


if __name__ == "__main__":
    MODELS = ["VGG-Face"]

    metadata.create_dirs()
    metrics = get_multimodel_metrics(MODELS)

    k = choose_k_concat(metrics, k=5)
    q = choose_k(metrics, k=5)

    print(k["selected"], q[MODELS[0]]["selected"])
    x = 0
