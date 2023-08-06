# -*- coding: utf-8 -*-

# Standard Imports
from __future__ import annotations
from pathlib import Path
from collections import defaultdict
import contextlib
import pickle
import os
import io

# Third Party Imports
from deepface import DeepFace
from deepface.commons.functions import extract_faces as _extract_faces
from retinaface.commons.postprocess import alignment_procedure
from tqdm import tqdm
import numpy as np
import mediapipe
import cv2

# Local Imports
from facefinder import rust
from . import metadata

# Typing imports
from typing import Callable, Any, Optional

def _build_mediapipe():
    mp_face_detection = mediapipe.solutions.face_detection
    face_detection = mp_face_detection.FaceDetection(min_detection_confidence=0.99)
    return face_detection

_mediapipe = _build_mediapipe()

def _normalize_mediapipe_detections(face_objs, target_size):
    extracted_faces = []

    for current_img, current_region, confidence in face_objs:
        if current_img.shape[0] > 0 and current_img.shape[1] > 0:

            # resize and padding
            if current_img.shape[0] > 0 and current_img.shape[1] > 0:
                factor_0 = target_size[0] / current_img.shape[0]
                factor_1 = target_size[1] / current_img.shape[1]
                factor = min(factor_0, factor_1)

                dsize = (
                    int(current_img.shape[1] * factor),
                    int(current_img.shape[0] * factor),
                )
                current_img = cv2.resize(current_img, dsize)

                diff_0 = target_size[0] - current_img.shape[0]
                diff_1 = target_size[1] - current_img.shape[1]

                # Put the base image in the middle of the padded image
                current_img = np.pad(
                    current_img,
                    (
                        (diff_0 // 2, diff_0 - diff_0 // 2),
                        (diff_1 // 2, diff_1 - diff_1 // 2),
                        (0, 0),
                    ),
                    "constant",
                )

            # double check: if target image is not still the same size with target.
            if current_img.shape[0:2] != target_size:
                current_img = cv2.resize(current_img, target_size)

            # normalizing the image pixels
            img_pixels = current_img[None, ...].astype(np.float32)
            img_pixels /= 255  # normalize input in [0, 1]

            # int cast is for the exception - object of type 'float32' is not JSON serializable
            region_obj = {
                "x": int(current_region[0]),
                "y": int(current_region[1]),
                "w": int(current_region[2]),
                "h": int(current_region[3]),
            }

            extracted_face = [img_pixels, region_obj, confidence]
            extracted_faces.append(extracted_face)

    return extracted_faces

def _mediapipe_detect(img, target_size, force_detection:bool = True, align=True):
    with open(img, "rb") as img_f:
        chunk = img_f.read()
        chunk_arr = np.frombuffer(chunk, dtype=np.uint8)
        img = cv2.imdecode(chunk_arr, cv2.IMREAD_COLOR)

    resp = []

    img_width = img.shape[1]
    img_height = img.shape[0]

    results = _mediapipe.process(img)

    if results.detections:
        for detection in results.detections:

            (confidence,) = detection.score

            bounding_box = detection.location_data.relative_bounding_box
            landmarks = detection.location_data.relative_keypoints

            x = int(bounding_box.xmin * img_width)
            w = int(bounding_box.width * img_width)
            y = int(bounding_box.ymin * img_height)
            h = int(bounding_box.height * img_height)

            right_eye = (int(landmarks[0].x * img_width), int(landmarks[0].y * img_height))
            left_eye = (int(landmarks[1].x * img_width), int(landmarks[1].y * img_height))
            nose = (int(landmarks[2].x * img_width), int(landmarks[2].y * img_height))
            
            if x > 0 and y > 0:
                detected_face = img[y : y + h, x : x + w]
                img_region = [x, y, w, h]

                if align:
                    detected_face = alignment_procedure(
                        detected_face, right_eye, left_eye, nose
                    )

                resp.append((detected_face, img_region, confidence))

    if not resp and force_detection:
        raise ValueError("Face could not be detected with mediapipe")
    
    return _normalize_mediapipe_detections(resp, target_size)

def extract_faces(image_path: Path, model: str) -> None:
    with contextlib.redirect_stdout(io.StringIO()):
        try:
            return _mediapipe_detect(str(image_path), metadata.MODEL_TARGET_SIZES[model])
        except (ValueError, TypeError):
            return _extract_faces(
                img=str(image_path),
                target_size=metadata.MODEL_TARGET_SIZES[model],
                detector_backend="retinaface",
                grayscale=False,
                enforce_detection=False,
                align=True,
            )


def _temp_view_extraction(objs, filename, show=False):
    from PIL import Image
    for data in objs:
        data = (data[0][0, :, :, ::-1] * 255).astype(np.uint8)
        image = Image.fromarray(data)
        image.save(metadata.PATHS.EMBEDDING_SCORES_DIR.joinpath(filename))
        if show:
            image.show()

def get_extracted_faces(image_path: Path, model: str) -> None:
    extracted_path = metadata.PATHS.EXTRACTED_FACES_DIR.joinpath(
        f"{image_path.name[:-4]}.pkl"
    )

    if not os.path.exists(extracted_path):
        img_objs = extract_faces(image_path, model)
        _temp_view_extraction(img_objs, f"{image_path.name[:-4]}.png")
        with open(extracted_path, "wb+") as f:
            pickle.dump(img_objs, f)
        return img_objs

    else:
        with open(extracted_path, "rb") as f:
            return pickle.load(f)


def create_representation(
    image_path: Path,
    model: str,
    skip_face: bool = False,
    choose_best: bool = False,
) -> list[list[float]]:
    img_objs = get_extracted_faces(image_path, model)

    representations = []
    for img_content, _, confidence in img_objs:
        if skip_face or confidence:
            embedding_obj = DeepFace.represent(
                img_path=img_content,
                model_name=model,
                enforce_detection=False,
                detector_backend="skip",
                align=True,
                normalization="base",
            )
            representations.append((embedding_obj[0]["embedding"], confidence))

    if choose_best:
        representations.sort(key=lambda repr: repr[1], reverse=True)
        return [representations[0][0]]
    return [r[0] for r in representations]


def get_representation(
    image_path: Path,
    model: str,
    skip_face: bool = False,
    choose_best: bool = False
) -> list[list[float]]:
    repr_name = f"{model}_{os.path.splitext(image_path.name)[0]}.repr"
    repr_path = metadata.PATHS.REPRESENTATIONS_DIR.joinpath(repr_name).resolve()

    if not os.path.exists(repr_path):
        img_representation = create_representation(image_path, model, skip_face, choose_best)
        with open(repr_path, "wb+") as f:
            pickle.dump(img_representation, f)
        return img_representation

    else:
        with open(repr_path, "rb") as f:
            return pickle.load(f)


def get_representations(
    images: Path,
    model: str,
    skip_face: bool = False,
    silent: bool = False,
) -> tuple[list[Path], list[list[float]]]:
    valid = (".png", ".jpg", ".jpeg")
    images = [
        images.joinpath(image) for image in os.listdir(images) if image.endswith(valid)
    ]
    paths = []
    representations = []

    with tqdm(
        total=len(images),
        disable=silent,
        desc=f"Gathering face representations for {model}",
    ) as pbar:
        for image_path in images:
            reprs = get_representation(image_path, model, skip_face)

            for rep in reprs:
                paths.append(image_path)
                representations.append(rep)

            pbar.update(1)

    return paths, representations


# n_embedding_images x 512 @ n_candidate_images x 512 -> n_candidate_images x n_embedding_images
def cosine_dist(
    source_reprs: list[list[float]],
    target_reprs: list[list[float]],
) -> list[list[float]]:
    target_reprs = np.array(target_reprs)
    source_reprs = np.array(source_reprs)

    # Dims 1 must match (length of representation vector)
    assert source_reprs.shape[1] == target_reprs.shape[1]

    a = np.matmul(target_reprs, source_reprs.T)
    b = np.sqrt(np.sum(target_reprs**2, axis=1))
    c = np.sqrt(np.sum(source_reprs**2, axis=1))
    return np.ones(a.shape) - (a / np.matmul(b[:, None], c[None, :]))


def euclid_dist(
    source_reprs: np.ndarray,
    target_reprs: np.ndarray,
) -> np.ndarray:
    # Dims 1 must match (length of representation vector)
    target_reprs = np.array(target_reprs)[:, None, :]
    source_reprs = np.array(source_reprs)[None, :, :]
    assert source_reprs.shape[2] == target_reprs.shape[2]

    target_reprs = target_reprs.repeat(source_reprs.shape[1], axis=1)
    source_reprs = source_reprs.repeat(target_reprs.shape[0], axis=0)

    return ((source_reprs - target_reprs) ** 2).sum(axis=2) ** 0.5


def filter_duplicates(paths: list[Path], distances: list[float]) -> list[int]:
    """Returns a numpy index that will filter out the duplicates with non-max scores"""
    visited = defaultdict(list)
    for i, path in enumerate(paths):
        visited[path].append(i)
    duplicates = {k: v for k, v in visited.items() if len(v) > 1}
    visited = {k: v[0] for k, v in visited.items()}
    for path, idx in duplicates.items():
        scores = distances[np.array(idx)]
        visited[path] = idx[np.argmin(scores)]
    non_duplicate_idx = np.array(list(visited.values()))
    return non_duplicate_idx


def get_filtered(
    target_repr: list[float],
    candidate_reprs: list[list[float]],
    candidate_paths: list[Path],
) -> tuple[list[Path], list[list[float]], list[float]]:
    # Finding metrics for distance from target image (BASE_FACE)
    target_distances = euclid_dist(target_repr, candidate_reprs)

    # Filtering embedding duplicates by distance to target
    non_duplicate_idx = filter_duplicates(candidate_paths, target_distances)
    candidate_paths = np.array(candidate_paths)[non_duplicate_idx]
    candidate_reprs = np.array(candidate_reprs)[non_duplicate_idx]
    target_distances = np.array(target_distances)[non_duplicate_idx]

    return candidate_paths, candidate_reprs, target_distances


def calculate_weighted_distances(
    embedding_target_distances: list[float],
    candidate_embedding_distances: list[list[float]],
    target_distance_bias: int = 1,
) -> list[float]:
    weights = np.power(embedding_target_distances.T, 1 / (target_distance_bias + 1))
    weighted_distances = candidate_embedding_distances * weights
    return weighted_distances.mean(axis=1)


def calculate_scores(
    target_distances: np.ndarray,
    weighted_distances: np.ndarray,
    embedding_accuracy: float,
) -> np.ndarray:
    wd_weight = 0.8 * (0.5 ** (5 * embedding_accuracy))
    td_weight = 1 - wd_weight
    scores = (target_distances.flatten() * td_weight) + (
        weighted_distances.flatten() * wd_weight
    )
    return scores


def get_embedding_metrics(
    model: str,
    target_path: Optional[Path] = None,
    embedding_dir: Optional[Path] = None,
) -> dict[str, Any]:
    target_path = target_path or metadata.PATHS.TARGET_IMAGE
    embedding_dir = embedding_dir or metadata.PATHS.EMBEDDING_IMAGES

    # Initial (non-filtered) target/embedding representations
    target_representation = get_representation(target_path, model, skip_face=True, choose_best=True)
    paths, representations = get_representations(embedding_dir, model, skip_face=True)

    # Filtering representations/paths by distance to target repr
    paths, representations, embedding_target_distances = get_filtered(
        target_representation, representations, paths
    )

    mean_target_distance = float(np.mean(embedding_target_distances))

    # Finding overall similarity between faces in the embedding train set
    embedding_embedding_distances = np.mean(
        euclid_dist(representations, representations), axis=1
    )
    mean_embedding_distance = float(np.mean(embedding_embedding_distances))

    return {
        "target_path": target_path,
        "target_representation": target_representation,
        "representations": representations,
        "paths": paths,
        "embedding_target_distances": embedding_target_distances,
        "mean_target_distance": mean_target_distance,
        "embedding_embedding_distances": embedding_embedding_distances,
        "mean_embedding_distance": mean_embedding_distance,
    }


def get_candidate_metrics(
    model: str,
    target_repr: list[float],
    embedding_reprs: list[list[float]],
    embedding_target_distances: list[float],
    candidate_dir: Optional[Path] = None,
    target_distance_bias: int = 1,
) -> dict[str, Any]:
    candidate_dir = candidate_dir or metadata.PATHS.UNPROCESSED_IMAGES

    # Initial (non-filtered) candidate representations
    paths, representations = get_representations(candidate_dir, model)
    x = 0

    # Filtering processed images by distance to target
    paths, representations, candidate_target_distances = get_filtered(
        target_repr, representations, paths
    )

    # Distances between candidates and embeddings
    candidate_embedding_pair_distances = euclid_dist(embedding_reprs, representations)
    candidate_embedding_distances = candidate_embedding_pair_distances.mean(axis=1)

    # Weighting the candidate distances by the embedding image scores (relative to the target)
    candidate_weighted_distances = calculate_weighted_distances(
        embedding_target_distances,
        candidate_embedding_pair_distances,
        target_distance_bias,
    )

    # Doing the same for embedding images
    embedding_weighted_distances = calculate_weighted_distances(
        embedding_target_distances,
        euclid_dist(embedding_reprs, embedding_reprs),
        target_distance_bias,
    )

    return {
        "paths": paths,
        "representations": representations,
        "candidate_target_distances": candidate_target_distances,
        "candidate_embedding_pair_distances": candidate_embedding_pair_distances,
        "candidate_embedding_distances": candidate_embedding_distances,
        "candidate_weighted_distances": candidate_weighted_distances,
        "embedding_weighted_distances": embedding_weighted_distances,
    }


def get_indices(metrics: dict) -> dict:
    # Gathering sorted indices for interactive functions (candidate images only)
    candidate_embedding_pair_distances = metrics["distances"]["pairs"]
    candidate_embedding_distances = metrics["distances"]["candidate_embedding"]
    candidate_weighted_distances = metrics["metrics"]["candidate_weighted_distances"]
    candidate_target_distances = metrics["distances"]["candidate_target"]
    candidate_scores = metrics["metrics"]["candidate_scores"]

    candidate_embedding_pair_idx = list(
        zip(
            *np.unravel_index(
                np.argsort(candidate_embedding_pair_distances, axis=None),
                candidate_embedding_pair_distances.shape,
            )
        )
    )
    candidate_embedding_idx = np.argsort(
        candidate_embedding_distances, axis=None
    ).tolist()
    candidate_weighted_idx = np.argsort(
        candidate_weighted_distances, axis=None
    ).tolist()
    candidate_score_idx = np.argsort(candidate_scores, axis=None).tolist()
    candidate_target_idx = np.argsort(candidate_target_distances, axis=None).tolist()

    # Gathering sorted indices for interactive functions (embedding images only)
    embedding_embedding_distances = metrics["distances"]["embedding_embedding"]
    embedding_weighted_distances = metrics["metrics"]["embedding_weighted_distances"]
    embedding_target_distances = metrics["distances"]["embedding_target"]
    embedding_scores = metrics["metrics"]["embedding_scores"]

    embedding_embedding_idx = np.argsort(
        embedding_embedding_distances, axis=None
    ).tolist()
    embedding_weighted_idx = np.argsort(
        embedding_weighted_distances, axis=None
    ).tolist()
    embedding_score_idx = np.argsort(embedding_scores, axis=None).tolist()
    embedding_target_idx = np.argsort(embedding_target_distances, axis=None).tolist()

    return {
        "candidate_embedding_idx": candidate_embedding_idx,
        "candidate_score_idx": candidate_score_idx,
        "candidate_target_idx": candidate_target_idx,
        "candidate_weighted_idx": candidate_weighted_idx,
        "embedding_embedding_idx": embedding_embedding_idx,
        "embedding_score_idx": embedding_score_idx,
        "embedding_target_idx": embedding_target_idx,
        "embedding_weighted_idx": embedding_weighted_idx,
        "candidate_embedding_pair_idx": candidate_embedding_pair_idx,
    }


def add_scores(metrics: dict) -> dict:
    candidate_scores = calculate_scores(
        metrics["distances"]["candidate_target"],
        metrics["metrics"]["candidate_weighted_distances"],
        metrics["metrics"]["embedding_accuracy"],
    )
    embedding_scores = calculate_scores(
        metrics["distances"]["embedding_target"],
        metrics["metrics"]["embedding_weighted_distances"],
        metrics["metrics"]["embedding_accuracy"],
    )
    metrics["metrics"]["candidate_scores"] = candidate_scores
    metrics["metrics"]["embedding_scores"] = embedding_scores


def get_metrics(
    model: str,
    target_path: Optional[str | Path] = None,
    embedding_dir: Optional[str | Path] = None,
    candidate_dir: Optional[str | Path] = None,
    target_distance_bias: int = 1,
) -> dict[str, Any]:
    target_path = target_path or metadata.PATHS.TARGET_IMAGE
    embedding_dir = embedding_dir or metadata.PATHS.EMBEDDING_IMAGES
    candidate_dir = candidate_dir or metadata.PATHS.UNPROCESSED_IMAGES

    embedding_metrics = get_embedding_metrics(model, target_path, embedding_dir)
    candidate_metrics = get_candidate_metrics(
        model,
        embedding_metrics["target_representation"],
        embedding_metrics["representations"],
        embedding_metrics["embedding_target_distances"],
        candidate_dir,
        target_distance_bias,
    )
    metrics = {
        "paths": {
            "target": embedding_metrics["target_path"],
            "embedding": embedding_metrics["paths"],
            "candidate": candidate_metrics["paths"],
        },
        "representations": {
            "target": embedding_metrics["target_representation"],
            "embedding": embedding_metrics["representations"],
            "candidate": candidate_metrics["representations"],
        },
        "distances": {
            "embedding_target": embedding_metrics["embedding_target_distances"],
            "embedding_embedding": embedding_metrics["embedding_embedding_distances"],
            "candidate_target": candidate_metrics["candidate_target_distances"],
            "candidate_embedding": candidate_metrics["candidate_embedding_distances"],
            "pairs": candidate_metrics["candidate_embedding_pair_distances"],
        },
        "metrics": {
            "embedding_accuracy": embedding_metrics["mean_target_distance"],
            "embedding_coherence": embedding_metrics["mean_embedding_distance"],
            "candidate_weighted_distances": candidate_metrics[
                "candidate_weighted_distances"
            ],
            "embedding_weighted_distances": candidate_metrics[
                "embedding_weighted_distances"
            ],
        },
        "metadata": {"model": model, "target_distance_bias": target_distance_bias},
    }

    add_scores(metrics)
    metrics["indices"] = get_indices(metrics)
    return metrics


def get_quantiles(metrics: dict) -> dict:
    preprocess = {
        "embedding_target_distances": metrics["distances"]["embedding_target"],
        "embedding_embedding_distances": metrics["distances"]["embedding_embedding"],
        "embedding_weighted_distances": metrics["metrics"][
            "embedding_weighted_distances"
        ],
        "candidate_target_distances": metrics["distances"]["candidate_target"],
        "candidate_embedding_distances": metrics["distances"]["candidate_embedding"],
        "candidate_weighted_distances": metrics["metrics"][
            "candidate_weighted_distances"
        ],
        "pair_distances": metrics["distances"]["pairs"],
    }

    quantile_values = np.arange(0, 1, 0.01)
    return {k: np.quantile(v, quantile_values) for k, v in preprocess.items()}


def create_scaler(n: float) -> Callable:
    def sigmoid(x: np.ndarray) -> np.ndarray:
        return 1 / (1 + np.exp(-10 * (x - n)))

    def f(x: np.ndarray) -> np.ndarray:
        return sigmoid(x) - sigmoid(0)

    def g(x: np.ndarray) -> np.ndarray:
        return f(x) / f(100)

    return g


def distance_mean(distances: dict[str, np.ndarray]) -> float:
    total_distance = 0
    total_size = 0
    for distance in distances.values():
        total_distance += np.sum(distance)
        total_size += distance.size

    return total_distance / total_size


def get_zscores(distances: np.ndarray) -> np.ndarray:
    """Returns a set of z scores that have been right-shifted to min=0, mean=1"""
    mean = distances.mean()
    std = np.std(distances)
    zscores = (distances - mean) / std

    # Normalizing to min=0, mean (originally 0 by definition) = 1
    zmin = -zscores.min()
    zscores = (zscores + zmin) / zmin

    return zscores


def merge_metrics(metrics: list[dict[str, Any]]) -> dict[str, Any]:
    if not metrics:
        raise ValueError(f"list of metrics must not be empty, {len(metrics)=}")

    paths = metrics[0]["paths"]
    representations = {m["metadata"]["model"]: m["representations"] for m in metrics}
    _metadata = {
        "model": [m["metadata"]["model"] for m in metrics],
        "target_distance_bias": [
            m["metadata"]["target_distance_bias"] for m in metrics
        ],
    }

    # TODO THIS IS A TEMPORARY FIX THAT DOES NOT SCALE THE VALUES
    distances = {
        "embedding_target": [],
        "embedding_embedding": [],
        "candidate_target": [],
        "candidate_embedding": [],
        "pairs": [],
    }

    for k in distances:
        for m in metrics:
            distance = m["distances"][k]
            distance /= metadata.THRESHOLDS[m["metadata"]["model"]]["euclidean"]
            if len(distance.shape) == 1:
                distance = distance[:, None]
            distance = distance[:, None]

            distances[k].append(distance)
        distances[k] = np.mean(np.concatenate(distances[k], axis=2), axis=2)

    candidate_weighted_distances = calculate_weighted_distances(
        distances["embedding_target"],
        distances["candidate_embedding"],
        np.mean(_metadata["target_distance_bias"]),
    )
    embedding_weighted_distances = calculate_weighted_distances(
        distances["embedding_target"],
        distances["embedding_embedding"],
        np.mean(_metadata["target_distance_bias"]),
    )
    embedding_accuracy = np.mean(distances["embedding_target"])
    embedding_coherence = np.mean(distances["embedding_embedding"])
    sub_metrics = {
        "embedding_accuracy": embedding_accuracy,
        "embedding_coherence": embedding_coherence,
        "candidate_weighted_distances": candidate_weighted_distances,
        "embedding_weighted_distances": embedding_weighted_distances,
    }

    metrics = {
        "paths": paths,
        "representations": representations,
        "distances": distances,
        "metrics": sub_metrics,
        "metadata": _metadata,
    }

    add_scores(metrics)
    metrics["indices"] = get_indices(metrics)
    metrics["quantiles"] = get_quantiles(metrics)

    return metrics


def get_multimodel_metrics(
    models: list[str],
    target_path: Optional[str | Path] = None,
    embedding_dir: Optional[str | Path] = None,
    candidate_dir: Optional[str | Path] = None,
    target_distance_bias: int = 1,
) -> dict[str, Any]:
    target_path = target_path or metadata.PATHS.TARGET_IMAGE
    embedding_dir = embedding_dir or metadata.PATHS.EMBEDDING_IMAGES
    candidate_dir = candidate_dir or metadata.PATHS.UNPROCESSED_IMAGES

    all_metrics = [
        get_metrics(
            model, target_path, embedding_dir, candidate_dir, target_distance_bias
        )
        for model in models
    ]
    return merge_metrics(all_metrics)


def save_processed_embedding_images(
    metrics: dict[str, Any], output_dir: Optional[Path] = None
) -> None:
    output_dir = output_dir or metadata.PATHS.EMBEDDING_SCORES_DIR

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    n_images = len(metrics["paths"]["embedding"])
    for path, accuracy, coherence in tqdm(
        zip(
            metrics["paths"]["embedding"],
            metrics["distances"]["embedding_target"],
            metrics["distances"]["embedding_embedding"],
        ),
        desc=f"Saving {n_images} embedding images",
        total=n_images,
    ):
        image_id = path.name.split("-")[0]
        image_name = f"{accuracy.item():.04f}_{coherence.item():.04f}_{image_id}.png"
        image_path = str(output_dir.joinpath(image_name))
        cv2.imwrite(image_path, cv2.imread(str(path)))


def save_processed_candidate_images(
    metrics: dict[str, Any], output_dir: Optional[Path] = None
) -> None:
    output_dir = output_dir or metadata.PATHS.PROCESSED_IMAGES

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    n_images = len(metrics["paths"]["candidate"])
    for path, score, accuracy, coherence in tqdm(
        zip(
            metrics["paths"]["candidate"],
            metrics["metrics"]["candidate_weighted_distances"],
            metrics["distances"]["candidate_target"],
            np.mean(metrics["distances"]["candidate_embedding"], axis=1),
        ),
        desc=f"Saving {n_images}, Processed Images",
        total=n_images,
    ):
        image_id = path.name.split("-")[0]
        image_name = (
            f"{score:.04f}_{accuracy.item():.04f}_{coherence:.04f}_{image_id}.png"
        )
        image_path = str(output_dir.joinpath(image_name))
        cv2.imwrite(image_path, cv2.imread(str(path)))


def main(interactive: bool = False) -> None:
    # Processing Images
    metrics = get_multimodel_metrics(
        ["Facenet512", "SFace"], target_distance_bias=1
    )  # "SFace", "ArcFace"])

    # Saving scored images
    # save_processed_embedding_images(metrics)
    # save_processed_candidate_images(metrics)

    x = 0


if __name__ == "__main__":
    metadata.create_dirs()
    main(interactive=True)
