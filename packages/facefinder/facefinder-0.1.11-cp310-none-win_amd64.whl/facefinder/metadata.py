from pathlib import Path
import re
import os

MODELS = [
    "Facenet512",
    "SFace",
    "ArcFace",
    "Facenet",
    "VGG-Face",
    "OpenFace",
    "DeepFace",
]

MODEL_TARGET_SIZES = {
    "VGG-Face": (224, 224),
    "Facenet": (160, 160),
    "Facenet512": (160, 160),
    "OpenFace": (96, 96),
    "DeepFace": (152, 152),
    "ArcFace": (112, 112),
    "SFace": (112, 112),
}

DEFAULT_EMBEDDING_COHERENCE_WEIGHT = 1

THRESHOLDS = {
    "VGG-Face": {"cosine": 0.40, "euclidean": 0.60, "euclidean_l2": 0.86},
    "Facenet": {"cosine": 0.40, "euclidean": 10, "euclidean_l2": 0.80},
    "Facenet512": {"cosine": 0.30, "euclidean": 23.56, "euclidean_l2": 1.04},
    "ArcFace": {"cosine": 0.68, "euclidean": 4.15, "euclidean_l2": 1.13},
    "Dlib": {"cosine": 0.07, "euclidean": 0.6, "euclidean_l2": 0.4},
    "SFace": {"cosine": 0.593, "euclidean": 10.734, "euclidean_l2": 1.055},
    "OpenFace": {"cosine": 0.10, "euclidean": 0.55, "euclidean_l2": 0.55},
    "DeepFace": {"cosine": 0.23, "euclidean": 64, "euclidean_l2": 0.64},
    "DeepID": {"cosine": 0.015, "euclidean": 45, "euclidean_l2": 0.17},
}


class _Singleton(type):
    __instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls.__instances:
            cls.__instances[cls] = super(_Singleton, cls).__call__(*args, **kwargs)
        return cls.__instances[cls]


class _Paths(metaclass=_Singleton):
    # ROOT: directory where all other dirs/files will be created
    ROOT = None

    # TARGET_IMAGE: path to image containing target face
    # EMBEDDING_IMAGES: path to directory containing images used for training embedding
    TARGET_IMAGE = None
    EMBEDDING_IMAGES = None

    # UNPROCESSED_IMAGES: directory containing raw, unscored images
    # PROCESSED_IMAGES: directory containing scored images (from unprocessed dir)
    UNPROCESSED_IMAGES = None
    PROCESSED_IMAGES = None

    # PROCESSING_DIR: intermediate processing directory containing the following 3 dirs
    # EXTRACTED_FACES_DIR: contains extracted faces from images in embedding/unprocessed dirs
    # REPRESENTATIONS_DIR: contains vector representations of faces in each image
    # EMBEDDING_SCORES_DIR: scored EMBEDDING_IMAGES images
    PROCESSING_DIR = None
    EXTRACTED_FACES_DIR = None
    REPRESENTATIONS_DIR = None
    EMBEDDING_SCORES_DIR = None

    def __str__(self) -> str:
        return str(self.as_dict())

    def __repr__(self) -> str:
        return str(self)

    def as_dict(self) -> dict[str, Path]:
        return {
            k: v
            for k, v in self.__class__.__dict__.items()
            if "__" not in k and isinstance(v, Path)
        }

    def __getattr__(self, attr: str) -> Path:
        return getattr(self.__class__, attr)


PATHS = _Paths()

_DEFAULT_PATHS = {
    "ROOT": "./FaceFinder",
    "TARGET_IMAGE": "target.png",
    "EMBEDDING_IMAGES": "embedding",
    "UNPROCESSED_IMAGES": "unprocessed",
    "PROCESSED_IMAGES": "processed",
    "PROCESSING_DIR": "data",
    "EXTRACTED_FACES_DIR": "extracted",
    "REPRESENTATIONS_DIR": "representations",
    "EMBEDDING_SCORES_DIR": "scored_embedding",
}


def set_paths(*, absolute: bool = False, **paths):
    paths = _DEFAULT_PATHS | paths

    P = PATHS.__class__

    if absolute:
        for pathname in PATHS.as_dict():
            path = paths.get(pathname, False)
            if path:
                setattr(PATHS, pathname, Path(path).resolve())

    else:
        P.ROOT = Path(paths["ROOT"]).resolve()
        P.TARGET_IMAGE = PATHS.ROOT.joinpath(paths["TARGET_IMAGE"])
        P.EMBEDDING_IMAGES = PATHS.ROOT.joinpath(paths["EMBEDDING_IMAGES"])
        P.UNPROCESSED_IMAGES = PATHS.ROOT.joinpath(paths["UNPROCESSED_IMAGES"])
        P.PROCESSED_IMAGES = PATHS.ROOT.joinpath(paths["PROCESSED_IMAGES"])
        P.PROCESSING_DIR = PATHS.ROOT.joinpath(paths["PROCESSING_DIR"])
        P.EXTRACTED_FACES_DIR = PATHS.PROCESSING_DIR.joinpath(
            paths["EXTRACTED_FACES_DIR"]
        )
        P.REPRESENTATIONS_DIR = PATHS.PROCESSING_DIR.joinpath(
            paths["REPRESENTATIONS_DIR"]
        )
        P.EMBEDDING_SCORES_DIR = PATHS.PROCESSING_DIR.joinpath(
            paths["EMBEDDING_SCORES_DIR"]
        )

    return PATHS


def create_dirs():
    for path in PATHS.as_dict().values():
        if not os.path.exists(path):
            if not path.name.endswith((".png", "jpg", "jpeg")):
                os.makedirs(path)


set_paths()
