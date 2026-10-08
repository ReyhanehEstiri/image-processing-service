from PIL import Image, ImageOps


def apply_transformations(img: Image.Image, t: dict) -> Image.Image:
    if crop := t.get("crop"):
        img = img.crop(
            (crop["x"], crop["y"], crop["x"] + crop["width"], crop["y"] + crop["height"])
        )

    if size := t.get("resize"):
        img = img.resize((size["width"], size["height"]))

    if angle := t.get("rotate"):
        img = img.rotate(-angle, expand=True)

    if t.get("flip"):
        img = ImageOps.flip(img)

    if t.get("mirror"):
        img = ImageOps.mirror(img)

    filters = t.get("filters") or {}
    if filters.get("grayscale"):
        img = ImageOps.grayscale(img).convert("RGB")

    return img