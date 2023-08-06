from functools import partial
from typing import Any, Callable
import cv2
import numpy as np


class InteractiveSession:
    def __init__(self, metrics: dict[str, Any]) -> None:
        self.metrics = metrics
        self.halt_inputs = ["quit", "stop", "exit"]

    def session(self):
        user_input = ""
        while user_input.strip() not in self.halt_inputs:
            user_input = input("> ")
            try:
                self.parse_input(user_input.strip().lower())()
            except ValueError as e:
                print(
                    f"\nUnable to complete the request due to the following error: {e}"
                )
                print(
                    "Now continuing interactive console. Please type quit or exit to terminate the program.\n"
                )

    @staticmethod
    def show_image(image: np.ndarray, text: str = "image") -> None:
        cv2.imshow(text, image)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    def show_match(self, rank: int) -> None:
        idx = self.metrics["indices"]["candidate_embedding_pair_idx"][rank]
        j = self.metrics["paths"]["candidate"][idx[0]]
        k = self.metrics["paths"]["embedding"][idx[1]]

        im1 = cv2.imread(str(j))
        im2 = cv2.imread(str(k))

        h1, w1 = im1.shape[:2]
        h2, w2 = im2.shape[:2]
        h, w = max(h1, h2), max(w1, w2)

        match_distance = self.metrics["distances"]["pairs"][idx]
        target_distance = self.metrics["distances"]["candidate_target"][idx[0]].item()
        embedding_distance = np.mean(
            self.metrics["distances"]["candidate_embedding"][idx[0]]
        )
        score = self.metrics["metrics"]["candidate_scores"][idx[0]]

        text_area = np.zeros((h, 500, 3), dtype="uint8")
        text_area.fill(255)
        text1 = f"score: {score}"
        text2 = f"match distance: {match_distance}"
        text3 = f"target distance: {target_distance}"
        text4 = f"embedding distance: {embedding_distance}"

        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 0.5
        font_color = (0, 0, 0)
        font_thickness = 1

        for hm, text in zip(range(4, 8), [text1, text2, text3, text4]):
            text_area = cv2.putText(
                text_area,
                text,
                (int(w / 10), int(hm * h / 10)),
                font,
                font_scale,
                font_color,
                font_thickness,
            )

        im1 = cv2.copyMakeBorder(im1, 0, h - h1, 0, 0, cv2.BORDER_CONSTANT)
        im2 = cv2.copyMakeBorder(im2, 0, h - h2, 0, 0, cv2.BORDER_CONSTANT)

        image = np.concatenate((im1, im2), axis=1)
        image = np.concatenate((image, text_area), axis=1)

        self.show_image(image)

    def show_cumulative(self, rank: int, target: bool = False) -> None:
        idx = (
            self.metrics["indices"]["candidate_target_idx"][rank]
            if target
            else self.metrics["indices"]["candidate_score_idx"][rank]
        )
        image = cv2.imread(str(self.metrics["paths"]["candidate"][idx]))

        h, w = image.shape[:2]
        target_distance = self.metrics["distances"]["candidate_target"][idx].item()
        embedding_distance = np.mean(
            self.metrics["distances"]["candidate_embedding"][idx]
        )
        score = self.metrics["metrics"]["candidate_scores"][idx]

        text_area = np.zeros((h, 500, 3)).astype("uint8")
        text_area.fill(255)
        text1 = f"score: {score}"
        text2 = f"target distance: {target_distance}"
        text3 = f"embedding distance: {embedding_distance}"

        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 0.5
        font_color = (0, 0, 0)
        font_thickness = 1

        for hm, text in zip(range(4, 7), [text1, text2, text3]):
            text_area = cv2.putText(
                text_area,
                text,
                (int(w / 10), int(hm * h / 10)),
                font,
                font_scale,
                font_color,
                font_thickness,
            )

        image = np.concatenate((image, text_area), axis=1)

        self.show_image(image)

    @staticmethod
    def show_range(f: Callable, start: int, stop: int, step: int) -> None:
        for n in range(start, stop, step):
            f(n)

    def parse_input(self, user_input: str) -> Callable:
        if user_input in self.halt_inputs:
            print("Terminating program.")
            return lambda: None

        parts = user_input.split(" ")
        if len(parts) < 2:
            raise ValueError(
                f"Missing arguments: Please provide a function (m, e, t) and a stopping point/range (as an integer)"
            )
        f, _range, *other_args = parts
        n_images = len(self.metrics["paths"]["candidate"])

        if f.startswith("m"):
            f = self.show_match
        elif f.startswith("e"):
            f = self.show_cumulative
        elif f.startswith("t"):
            f = partial(self.show_cumulative, target=True)
        else:
            raise ValueError(
                f"'{f}' not recognized as a valid function (try m for direct match, e for embedding, or t for target)"
            )

        if ":" in _range:
            if list(_range).count(":") > 1:
                raise ValueError("Cannot parse range with more than one colon")

            start = 0
            stop = 0
            step = 1

            if _range.startswith(":"):
                start = 0
            else:
                start = int(_range.split(":")[0])

            if _range.endswith(":"):
                stop = n_images
            else:
                stop = int(_range.split(":")[-1])

            start = np.clip(start, 0, n_images).item()
            stop = np.clip(stop, 0, n_images).item()

            if start > stop:
                step = -1

            diff = abs(start - stop)
            if diff > 100:
                _continue = input(
                    f"Requested to display more than {diff} images in succession. Continue? (y/n): "
                )
                if not _continue.lower().startswith("y"):
                    raise ValueError(f"Request cancelled by user")

            f = partial(self.show_range, f, start, stop, step)
        else:
            _range = int(_range)
            clipped_range = np.clip(_range, 0, n_images).item()
            if _range < 0 or _range > n_images:
                print(f"Cannot show {_range}; showing {clipped_range} instead")
            f = partial(f, clipped_range)

        return f
