from __future__ import annotations

import json
import shutil
import statistics
import sys
from pathlib import Path

from PIL import Image
from pyproj import Transformer


PROJECT_ROOT = Path(__file__).resolve().parents[2]
CONTEXT_DIR = PROJECT_ROOT / "frontend" / "mapping" / "data" / "context"
CORRECT_BACKGROUND_DIR = PROJECT_ROOT / "frontend" / "mapping" / "backgrounds"
LEGACY_BACKGROUND_DIR = PROJECT_ROOT / "frontend" / "mapping" / "backrounds"
INPUT_DIRS = [
    LEGACY_BACKGROUND_DIR / "geotiff",
    CORRECT_BACKGROUND_DIR / "geotiff",
]
REFERENCE_DIRS = [
    LEGACY_BACKGROUND_DIR / "georeference",
    CORRECT_BACKGROUND_DIR / "georeference",
]
OUTPUT_DIR = CORRECT_BACKGROUND_DIR / "geotiff"

WGS84_TO_GREEK_GRID = Transformer.from_crs("EPSG:4326", "EPSG:2100", always_xy=True)

GREEK_GRID_GEO_KEY_DIRECTORY = (
    1, 1, 0, 7,
    1024, 0, 1, 1,
    1025, 0, 1, 1,
    1026, 34737, 20, 0,
    2049, 34737, 7, 20,
    2054, 0, 1, 9102,
    3072, 0, 1, 2100,
    3076, 0, 1, 9001,
)
GREEK_GRID_ASCII = "GGRS87 / Greek Grid|GGRS87|"

AREA_ALIASES = {
    "D1": "Δ1",
    "D2": "Δ2",
    "D3": "Δ3",
    "D4": "Δ4",
    "D5": "Δ5",
    "Agios_Antonios": "ΑΓ. ΑΝΤΩΝΙΟΣ",
    "Ag_Giorgis": "ΑΓ. ΓΙΩΡΓΗΣ",
    "Ag_Minas": "ΑΓ. ΜΗΝΑΣ",
    "Analipsi": "ΑΝΑΛΗΨΗ",
    "Astro_Amfialis": "ΑΣΤΡΟ ΑΜΦΙΑΛΗΣ",
    "Eugenia": "ΕΥΓΕΝΕΙΑ",
    "Kokkinovrahos": "ΚΟΚΚΙΝΟΒΡΑΧΟΣ",
    "Pan_vlaxernwn": "ΠΑΝ. ΒΛΑΧΕΡΝΩΝ",
    "Tampouria": "ΤΑΜΠΟΥΡΙΑ",
    "Xaraugi": "ΧΑΡΑΥΓΗ",
}


def main() -> int:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    area_features = load_area_features()
    padding_samples = collect_padding_samples(area_features)
    padding = median_padding(padding_samples)
    print(f"Using padding ratios: left={padding[0]:.3f}, top={padding[1]:.3f}, right={padding[2]:.3f}, bottom={padding[3]:.3f}")

    created = []
    skipped = []
    for input_path in sorted(set(path for directory in INPUT_DIRS if directory.exists() for path in directory.glob("*.png"))):
        stem = input_path.stem
        output_path = OUTPUT_DIR / f"{stem}.tif"
        reference_path = find_reference_tif(stem)
        if reference_path:
            shutil.copy2(reference_path, output_path)
            created.append(output_path)
            continue
        if output_path.exists():
            skipped.append((stem, "already exists"))
            continue
        area_name = AREA_ALIASES.get(stem)
        feature = area_features.get(area_name or "")
        if not feature:
            skipped.append((stem, "no matching area polygon"))
            continue
        image = Image.open(input_path).convert("RGBA")
        bounds = padded_bounds(projected_bounds(feature), padding)
        save_geotiff(image, bounds, output_path)
        created.append(output_path)

    print("Created:")
    for path in created:
        print(f"  {path.relative_to(PROJECT_ROOT)}")
    print("Skipped:")
    for stem, reason in skipped:
        print(f"  {stem}: {reason}")
    return 0


def find_reference_tif(stem: str) -> Path | None:
    for directory in REFERENCE_DIRS:
        if not directory.exists():
            continue
        for candidate in (directory / f"{stem}.tif", directory / f"{stem}_georeference.tif"):
            if candidate.exists():
                return candidate
    return None


def load_area_features() -> dict[str, dict]:
    layer = json.loads((CONTEXT_DIR / "urban_units.geojson").read_text(encoding="utf-8"))
    return {
        str(feature.get("properties", {}).get("perigrafi", "")).upper(): feature
        for feature in layer.get("features", [])
    }


def collect_padding_samples(area_features: dict[str, dict]) -> list[tuple[float, float, float, float]]:
    samples = []
    for directory in REFERENCE_DIRS:
        if not directory.exists():
            continue
        for path in directory.glob("*.tif"):
            stem = path.stem.replace("_georeference", "")
            area_name = AREA_ALIASES.get(stem)
            feature = area_features.get(area_name or "")
            if not feature:
                continue
            image = Image.open(path)
            tags = image.tag_v2
            pixel_scale = tags.get(33550)
            tiepoint = tags.get(33922)
            if not pixel_scale or not tiepoint:
                continue
            image_bounds = (
                float(tiepoint[3]),
                float(tiepoint[4]) - image.height * float(pixel_scale[1]),
                float(tiepoint[3]) + image.width * float(pixel_scale[0]),
                float(tiepoint[4]),
            )
            polygon_bounds = projected_bounds(feature)
            width = polygon_bounds[2] - polygon_bounds[0]
            height = polygon_bounds[3] - polygon_bounds[1]
            if width <= 0 or height <= 0:
                continue
            samples.append((
                (polygon_bounds[0] - image_bounds[0]) / width,
                (image_bounds[3] - polygon_bounds[3]) / height,
                (image_bounds[2] - polygon_bounds[2]) / width,
                (polygon_bounds[1] - image_bounds[1]) / height,
            ))
    return samples


def median_padding(samples: list[tuple[float, float, float, float]]) -> tuple[float, float, float, float]:
    if not samples:
        return (0.12, 0.12, 0.12, 0.12)
    return tuple(max(0.03, statistics.median(sample[index] for sample in samples)) for index in range(4))


def projected_bounds(feature: dict) -> tuple[float, float, float, float]:
    points = []
    collect_coordinates((feature.get("geometry") or {}).get("coordinates"), points)
    projected = [WGS84_TO_GREEK_GRID.transform(lng, lat) for lng, lat in points]
    xs = [point[0] for point in projected]
    ys = [point[1] for point in projected]
    return min(xs), min(ys), max(xs), max(ys)


def padded_bounds(bounds: tuple[float, float, float, float], padding: tuple[float, float, float, float]) -> tuple[float, float, float, float]:
    min_x, min_y, max_x, max_y = bounds
    width = max_x - min_x
    height = max_y - min_y
    left, top, right, bottom = padding
    return (
        min_x - width * left,
        min_y - height * bottom,
        max_x + width * right,
        max_y + height * top,
    )


def save_geotiff(image: Image.Image, bounds: tuple[float, float, float, float], output_path: Path) -> None:
    min_x, min_y, max_x, max_y = bounds
    pixel_scale_x = (max_x - min_x) / image.width
    pixel_scale_y = (max_y - min_y) / image.height
    tiffinfo = Image.Exif()
    tiffinfo[33550] = (pixel_scale_x, pixel_scale_y, 0.0)
    tiffinfo[33922] = (0.0, 0.0, 0.0, min_x, max_y, 0.0)
    tiffinfo[34735] = GREEK_GRID_GEO_KEY_DIRECTORY
    tiffinfo[34737] = GREEK_GRID_ASCII
    image.save(output_path, format="TIFF", tiffinfo=tiffinfo)


def collect_coordinates(value, coordinates: list[tuple[float, float]]) -> None:
    if not isinstance(value, list):
        return
    if len(value) >= 2 and isinstance(value[0], (int, float)) and isinstance(value[1], (int, float)):
        coordinates.append((float(value[0]), float(value[1])))
        return
    for entry in value:
        collect_coordinates(entry, coordinates)


if __name__ == "__main__":
    sys.exit(main())
