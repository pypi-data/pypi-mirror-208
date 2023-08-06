# -*- coding: utf-8 -*-

# Standard Imports
from __future__ import annotations
from enum import Enum, auto
from typing import Optional, Iterable
from pathlib import Path
import os


def valid_model(model: str) -> bool:
    if not model.endswith((".safetensors", ".ckpt")):
        return False

    for invalid in ["inpaint", "instruct"]:
        if invalid in model:
            return False

    return True


ROOT = Path(__file__).parent.resolve()
MODELS = [
    model
    for model in os.listdir(
        ROOT.joinpath("stable-diffusion-webui/models/Stable-diffusion")
    )
    if valid_model(model)
]


class Sampler(Enum):
    EULER_A = "euler a"
    EULER = "euler"
    LMS = "LMS"
    HEUN = "Heun"
    DPM2 = "DPM2"
    DPM2A = "DPM2a"
    DPMPP_2S_A = "DPM++ 2S a"
    DPMPP_2M = "DPM++ 2M"
    DPMPP_SDE = "DPM++ SDE"
    DPM_FAST = "DPM fast"
    DPM_ADAPTIVE = "DPM adaptive"
    LMS_KARRAS = "LMS Karras"
    DPM2_KARRAS = "DPM2 Karras"
    DPM2_A_KARRAS = "DPM2 a Karras"
    DPMPP_2S_A_KARRAS = "DPM++ 2S a Karras"
    DPMPP_2M_KARRAS = "DPM++ 2M Karras"
    DPMPP_SDE_KARRAS = "DPM++ SDE Karras"
    DDIM = "DDIM"
    PLMS = "PLMS"


class Tag(Enum):
    EMBEDDING = auto()
    LOCATION = auto()
    STYLE = auto()
    ATTIRE = auto()
    EMOTION = auto()
    ACTION = auto()
    MEDIUM = auto()
    FEATURES = auto()
    DESCRIPTOR = auto()
    NSFW = auto()


class Component:
    def __init__(
        self, content: str, strength: float, tags: Optional[Tag | list[Tag]]
    ) -> None:
        self.content = content
        self.strength = strength
        self.tags = tags if isinstance(tags, list) else [tags]

    def __str__(self) -> str:
        if self.strength != 1:
            return f"({self.content}:{self.strength})"
        return f"{self.content}"


class Prompt:
    def __init__(
        self,
        positive: Iterable[Component],
        negative: Iterable[Component],
        steps: int,
        sampler: Sampler,
        cfg_scale: float,
        width: int = 512,
        height: int = 512,
        seed: int = -1,
        model: str = "chilloutmix_Ni",
        batch_size: int = 10,
        restore_faces: bool = True,
    ) -> None:
        self._positive = positive
        self._negative = negative
        self._steps = steps
        self._sampler = sampler
        self._cfg_scale = cfg_scale
        self._seed = seed
        self._width = width
        self._height = height
        self._size = (width, height)
        self._model = model
        self._batch_size = batch_size
        self._restore_faces = restore_faces

    def __str__(self) -> str:
        args = {
            "sd_model": None,
            "outpath_samples": None,
            "outpath_grids": None,
            "prompt_for_display": None,
            "prompt": self.positive,
            "negative_prompt": self.negative,
            "styles": None,
            "seed": self.seed,
            "subseed_strength": None,
            "subseed": None,
            "seed_resize_from_h": None,
            "seed_resize_from_w": None,
            "sampler_index": None,
            "sampler_name": self.sampler,
            "batch_size": self.batch_size,
            "n_iter": None,
            "steps": self.steps,
            "cfg_scale": self.cfg_scale,
            "width": self.width,
            "height": self.height,
            "restore_faces": self.restore_faces,
            "tiling": None,
            "do_not_save_samples": None,
            "do_not_save_grid": None,
        }

        prompt = []
        for arg, val in args.items():
            if val is not None:
                prompt.append(f"--{arg} {val}")
        return " ".join(prompt)

    @property
    def positive(self) -> str:
        return ", ".join([str(component) for component in self._positive])

    @property
    def negative(self) -> str:
        return ", ".join([str(component) for component in self._negative])

    @property
    def seed(self) -> int:
        return self._seed

    @property
    def sampler(self) -> str:
        return self._sampler.value

    @property
    def batch_size(self) -> int:
        return self._batch_size

    @property
    def steps(self) -> int:
        return self._steps

    @property
    def cfg_scale(self) -> float:
        return self._cfg_scale

    @property
    def width(self) -> int:
        return self._width

    @property
    def height(self) -> int:
        return self._height

    @property
    def restore_faces(self) -> bool:
        return self._restore_faces


if __name__ == "__main__":
    component = Component("{embedding}", 1, Tag.EMBEDDING)
    prompt = Prompt([component], [component], 1, Sampler.DPMPP_2M_KARRAS, 10)
    x = 0
