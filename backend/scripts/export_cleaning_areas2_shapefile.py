from __future__ import annotations

from datetime import date

from sqlalchemy import create_engine

from app.core.config import settings
from scripts.export_cleaning_areas_shapefile import (
    GROUP_FIELD,
    SOURCE_PATH,
    TARGET_DIR,
    group_features,
    write_polygon_shapefile,
)
from scripts.export_gis_context_layers import (
    read_shapefile,
    sort_group_key,
    transform_grouped_geometry,
)


TARGET_BASENAME = "cleaning_areas2"


def main() -> None:
    engine = create_engine(settings.database_url)
    features = read_shapefile(SOURCE_PATH)
    grouped = group_features(features, GROUP_FIELD)

    TARGET_DIR.mkdir(parents=True, exist_ok=True)

    with engine.connect() as connection:
        records = []
        for index, key in enumerate(sorted(grouped, key=sort_group_key), start=1):
            geometry = transform_grouped_geometry(
                connection,
                [feature["wkt"] for feature in grouped[key]],
                extract_type=3,
            )
            if geometry is None:
                continue

            records.append(
                {
                    "geometry": geometry,
                    "properties": {
                        "ktim_tomea": str(key),
                        "name": f"P{index}",
                        "label": f"Π{index}",
                        "area_code": f"P{index}",
                        "feature_cnt": len(grouped[key]),
                        "src_file": SOURCE_PATH.name,
                        "created_on": date.today().isoformat(),
                    },
                }
            )

    write_polygon_shapefile(TARGET_DIR / TARGET_BASENAME, records)
    print(f"Exported {len(records)} cleaning area polygon(s) to {TARGET_DIR}")


if __name__ == "__main__":
    main()
