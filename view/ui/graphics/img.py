from __future__ import annotations

import pathlib
import ctypes

import cv2
import numpy as np

class Img:
    def __init__(self):
        self.img = None

    def read(self, path: str | pathlib.Path,
             size: tuple[int, int] | None = None,
             keep_aspect: bool = False,
             interpolation: int = cv2.INTER_AREA) -> "Img":
        """
        Load `path` into self.img and **optionally resize**.

        Parameters
        ----------
        path : str | Path
            Image file to load.
        size : (width, height) | None
            Target size in pixels.  If None, keep original.
        keep_aspect : bool
            • False  → resize exactly to `size`
            • True   → shrink so the *longer* side fits `size` while
                       preserving aspect ratio (no cropping).
        interpolation : OpenCV flag
            E.g.  `cv2.INTER_AREA` for shrink, `cv2.INTER_LINEAR` for enlarge.

        Returns
        -------
        Img
            `self`, so you can chain:  `sprite = Img().read("foo.png", (64,64))`
        """
        path = str(path)
        self.img = cv2.imread(path, cv2.IMREAD_UNCHANGED)
        if self.img is None:
            # OpenCV may fail on Windows paths containing non-ASCII characters.
            try:
                raw = np.fromfile(path, dtype=np.uint8)
                if raw.size > 0:
                    self.img = cv2.imdecode(raw, cv2.IMREAD_UNCHANGED)
            except OSError:
                self.img = None

        if self.img is None:
            raise FileNotFoundError(f"Cannot load image: {path}")

        if size is not None:
            target_w, target_h = size
            h, w = self.img.shape[:2]

            if keep_aspect:
                scale = min(target_w / w, target_h / h)
                new_w, new_h = int(w * scale), int(h * scale)
            else:
                new_w, new_h = target_w, target_h

            self.img = cv2.resize(self.img, (new_w, new_h), interpolation=interpolation)

        return self

    def draw_on(self, other_img, x, y):
        if self.img is None or other_img.img is None:
            raise ValueError("Both images must be loaded before drawing.")

        if self.img.shape[2] != other_img.img.shape[2]:
            if self.img.shape[2] == 3 and other_img.img.shape[2] == 4:
                self.img = cv2.cvtColor(self.img, cv2.COLOR_BGR2BGRA)
            elif self.img.shape[2] == 4 and other_img.img.shape[2] == 3:
                self.img = cv2.cvtColor(self.img, cv2.COLOR_BGRA2BGR)

        h, w = self.img.shape[:2]
        H, W = other_img.img.shape[:2]

        if y + h > H or x + w > W:
            raise ValueError("Logo does not fit at the specified position.")

        roi = other_img.img[y:y + h, x:x + w]

        if self.img.shape[2] == 4:
            b, g, r, a = cv2.split(self.img)
            mask = a / 255.0
            for c in range(3):
                roi[..., c] = (1 - mask) * roi[..., c] + mask * self.img[..., c]
        else:
            other_img.img[y:y + h, x:x + w] = self.img

    def put_text(self, txt, x, y, font_size, color=(255, 255, 255, 255), thickness=1):
        if self.img is None:
            raise ValueError("Image not loaded.")
        cv2.putText(self.img, txt, (x, y),
                    cv2.FONT_HERSHEY_SIMPLEX, font_size,
                    color, thickness, cv2.LINE_AA)

    @staticmethod
    def fit_to_screen(image: np.ndarray, fill_ratio: float = 0.85) -> np.ndarray:
        """Scale a frame down to fit the current display without distortion."""
        try:
            screen_width = ctypes.windll.user32.GetSystemMetrics(0)
            screen_height = ctypes.windll.user32.GetSystemMetrics(1)
        except (AttributeError, OSError):
            screen_width, screen_height = 1280, 720

        max_width = int(screen_width * fill_ratio)
        max_height = int(screen_height * fill_ratio)
        height, width = image.shape[:2]
        scale = min(max_width / width, max_height / height, 1.0)
        if scale == 1.0:
            return image
        return cv2.resize(image, (int(width * scale), int(height * scale)), interpolation=cv2.INTER_AREA)

    def show(self, window_name: str = "Kung Fu Chess"):
        if self.img is None:
            raise ValueError("Image not loaded.")
        cv2.namedWindow(window_name, cv2.WINDOW_AUTOSIZE)
        cv2.imshow(window_name, self.fit_to_screen(self.img))
        cv2.waitKey(0)
        cv2.destroyAllWindows()
