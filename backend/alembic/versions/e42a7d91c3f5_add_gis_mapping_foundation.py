"""add gis mapping foundation

Revision ID: e42a7d91c3f5
Revises: d31e9f4a2b70
Create Date: 2026-04-19 22:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

from app.db.geometry import Geometry


# revision identifiers, used by Alembic.
revision: str = "e42a7d91c3f5"
down_revision: Union[str, Sequence[str], None] = "d31e9f4a2b70"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("CREATE EXTENSION IF NOT EXISTS postgis")

    op.create_table(
        "municipality_boundary",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("code", sa.String(length=50), nullable=False),
        sa.Column("name", sa.String(length=150), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("geom", Geometry("MULTIPOLYGON", 4326), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("code", name="uq_municipality_boundary_code"),
    )
    op.create_index(
        "ix_municipality_boundary_geom",
        "municipality_boundary",
        ["geom"],
        unique=False,
        postgresql_using="gist",
    )

    op.create_table(
        "cleaning_zone",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("code", sa.String(length=50), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("priority", sa.Integer(), nullable=False),
        sa.Column("geom", Geometry("MULTIPOLYGON", 4326), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("code", name="uq_cleaning_zone_code"),
    )
    op.create_index(
        "ix_cleaning_zone_geom",
        "cleaning_zone",
        ["geom"],
        unique=False,
        postgresql_using="gist",
    )

    op.create_table(
        "road_segment",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("code", sa.String(length=80), nullable=False),
        sa.Column("name", sa.String(length=160), nullable=False),
        sa.Column("road_type", sa.String(length=40), nullable=False),
        sa.Column("default_priority", sa.Integer(), nullable=False),
        sa.Column("geom", Geometry("LINESTRING", 4326), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("cleaning_zone_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(["cleaning_zone_id"], ["cleaning_zone.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("code", name="uq_road_segment_code"),
    )
    op.create_index(
        "ix_road_segment_cleaning_zone_id",
        "road_segment",
        ["cleaning_zone_id"],
        unique=False,
    )
    op.create_index(
        "ix_road_segment_geom",
        "road_segment",
        ["geom"],
        unique=False,
        postgresql_using="gist",
    )

    op.create_table(
        "map_asset",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("code", sa.String(length=80), nullable=False),
        sa.Column("name", sa.String(length=160), nullable=False),
        sa.Column("asset_type", sa.String(length=50), nullable=False),
        sa.Column("address", sa.String(length=255), nullable=True),
        sa.Column("priority", sa.Integer(), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("geom", Geometry("GEOMETRY", 4326), nullable=False),
        sa.Column("is_public_property", sa.Boolean(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("cleaning_zone_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(["cleaning_zone_id"], ["cleaning_zone.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("code", name="uq_map_asset_code"),
    )
    op.create_index(
        "ix_map_asset_asset_type",
        "map_asset",
        ["asset_type"],
        unique=False,
    )
    op.create_index(
        "ix_map_asset_cleaning_zone_id",
        "map_asset",
        ["cleaning_zone_id"],
        unique=False,
    )
    op.create_index(
        "ix_map_asset_geom",
        "map_asset",
        ["geom"],
        unique=False,
        postgresql_using="gist",
    )

    op.create_table(
        "cleaning_status_event",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("target_type", sa.String(length=40), nullable=False),
        sa.Column("target_id", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(length=30), nullable=False),
        sa.Column("priority", sa.Integer(), nullable=False),
        sa.Column("source", sa.String(length=40), nullable=False),
        sa.Column("event_date", sa.Date(), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("assignment_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(["assignment_id"], ["daily_assignment.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_cleaning_status_event_assignment_id",
        "cleaning_status_event",
        ["assignment_id"],
        unique=False,
    )
    op.create_index(
        "ix_cleaning_status_event_target",
        "cleaning_status_event",
        ["target_type", "target_id"],
        unique=False,
    )
    op.create_index(
        "ix_cleaning_status_event_event_date",
        "cleaning_status_event",
        ["event_date"],
        unique=False,
    )

    op.create_table(
        "daily_assignment_map_target",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("daily_assignment_id", sa.Integer(), nullable=False),
        sa.Column("target_type", sa.String(length=40), nullable=False),
        sa.Column("target_id", sa.Integer(), nullable=False),
        sa.Column("planned_order", sa.Integer(), nullable=True),
        sa.Column("status", sa.String(length=30), nullable=False),
        sa.ForeignKeyConstraint(["daily_assignment_id"], ["daily_assignment.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "daily_assignment_id",
            "target_type",
            "target_id",
            name="uq_daily_assignment_map_target",
        ),
    )
    op.create_index(
        "ix_daily_assignment_map_target_assignment_id",
        "daily_assignment_map_target",
        ["daily_assignment_id"],
        unique=False,
    )
    op.create_index(
        "ix_daily_assignment_map_target_target",
        "daily_assignment_map_target",
        ["target_type", "target_id"],
        unique=False,
    )

    _seed_demo_gis_data()


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index("ix_daily_assignment_map_target_target", table_name="daily_assignment_map_target")
    op.drop_index("ix_daily_assignment_map_target_assignment_id", table_name="daily_assignment_map_target")
    op.drop_table("daily_assignment_map_target")
    op.drop_index("ix_cleaning_status_event_event_date", table_name="cleaning_status_event")
    op.drop_index("ix_cleaning_status_event_target", table_name="cleaning_status_event")
    op.drop_index("ix_cleaning_status_event_assignment_id", table_name="cleaning_status_event")
    op.drop_table("cleaning_status_event")
    op.drop_index("ix_map_asset_geom", table_name="map_asset")
    op.drop_index("ix_map_asset_cleaning_zone_id", table_name="map_asset")
    op.drop_index("ix_map_asset_asset_type", table_name="map_asset")
    op.drop_table("map_asset")
    op.drop_index("ix_road_segment_geom", table_name="road_segment")
    op.drop_index("ix_road_segment_cleaning_zone_id", table_name="road_segment")
    op.drop_table("road_segment")
    op.drop_index("ix_cleaning_zone_geom", table_name="cleaning_zone")
    op.drop_table("cleaning_zone")
    op.drop_index("ix_municipality_boundary_geom", table_name="municipality_boundary")
    op.drop_table("municipality_boundary")


def _seed_demo_gis_data() -> None:
    op.execute(
        """
        INSERT INTO municipality_boundary (id, code, name, description, geom, is_active)
        VALUES (
            1,
            'keratsini_drapetsona',
            'Δήμος Κερατσινίου - Δραπετσώνας',
            'Demo όριο δήμου για το MVP. Θα αντικατασταθεί από επίσημο GIS όριο.',
            ST_Multi(ST_GeomFromText('POLYGON((23.586 37.941, 23.646 37.941, 23.646 37.988, 23.586 37.988, 23.586 37.941))', 4326)),
            true
        )
        """
    )
    op.execute(
        """
        INSERT INTO cleaning_zone (id, code, name, description, priority, geom, is_active)
        VALUES
        (1, 'amfiali', 'Αμφιάλη', 'Demo περιοχή καθαριότητας.', 2,
         ST_Multi(ST_GeomFromText('POLYGON((23.598 37.955, 23.621 37.955, 23.621 37.972, 23.598 37.972, 23.598 37.955))', 4326)), true),
        (2, 'drapetsona', 'Δραπετσώνα', 'Demo περιοχή καθαριότητας.', 1,
         ST_Multi(ST_GeomFromText('POLYGON((23.586 37.944, 23.607 37.944, 23.607 37.960, 23.586 37.960, 23.586 37.944))', 4326)), true),
        (3, 'keratsini_center', 'Κέντρο Κερατσινίου', 'Demo περιοχή καθαριότητας.', 1,
         ST_Multi(ST_GeomFromText('POLYGON((23.616 37.954, 23.640 37.954, 23.640 37.973, 23.616 37.973, 23.616 37.954))', 4326)), true),
        (4, 'ischyoskala', 'Ιχθυόσκαλα', 'Demo περιοχή καθαριότητας.', 1,
         ST_Multi(ST_GeomFromText('POLYGON((23.590 37.960, 23.610 37.960, 23.610 37.979, 23.590 37.979, 23.590 37.960))', 4326)), true)
        """
    )
    op.execute(
        """
        INSERT INTO road_segment (id, code, name, road_type, default_priority, cleaning_zone_id, geom, is_active)
        VALUES
        (1, 'road-dimokratias-01', 'Λεωφόρος Δημοκρατίας', 'main_road', 1, 3,
         ST_GeomFromText('LINESTRING(23.617 37.960, 23.627 37.965, 23.636 37.969)', 4326), true),
        (2, 'road-salamonos-01', 'Σαλαμίνος', 'main_road', 2, 2,
         ST_GeomFromText('LINESTRING(23.592 37.950, 23.600 37.954, 23.606 37.958)', 4326), true),
        (3, 'road-amfialis-01', 'Αμφιάλης', 'collector', 2, 1,
         ST_GeomFromText('LINESTRING(23.602 37.958, 23.612 37.963, 23.620 37.969)', 4326), true),
        (4, 'road-ischyoskala-01', 'Ζώνη Ιχθυόσκαλας', 'industrial', 1, 4,
         ST_GeomFromText('LINESTRING(23.592 37.965, 23.600 37.970, 23.608 37.976)', 4326), true),
        (5, 'road-tampouria-01', 'Ταμπούρια', 'street', 3, 3,
         ST_GeomFromText('LINESTRING(23.620 37.955, 23.626 37.959, 23.632 37.962)', 4326), true)
        """
    )
    op.execute(
        """
        INSERT INTO map_asset (id, code, name, asset_type, address, priority, notes, cleaning_zone_id, geom, is_public_property, is_active)
        VALUES
        (1, 'asset-square-eleftherias', 'Πλατεία Ελευθερίας', 'square', 'Κέντρο Κερατσινίου', 1, 'Κεντρική πλατεία υψηλής προτεραιότητας.', 3,
         ST_GeomFromText('POINT(23.626 37.963)', 4326), true, true),
        (2, 'asset-park-amfiali', 'Πάρκο Αμφιάλης', 'park', 'Αμφιάλη', 2, 'Πράσινος χώρος καθημερινής φροντίδας.', 1,
         ST_GeomFromText('POINT(23.611 37.965)', 4326), true, true),
        (3, 'asset-bin-drapetsona-01', 'Συστάδα κάδων Δραπετσώνας', 'bin_point', 'Δραπετσώνα', 1, 'Σημείο υψηλού φόρτου.', 2,
         ST_GeomFromText('POINT(23.599 37.952)', 4326), true, true),
        (4, 'asset-school-keratsini-01', 'Σχολικό συγκρότημα Κερατσινίου', 'school', 'Κερατσίνι', 2, 'Σχολική μονάδα με πρωινό καθαρισμό περιμέτρου.', 3,
         ST_GeomFromText('POINT(23.632 37.967)', 4326), true, true),
        (5, 'asset-municipal-building-01', 'Δημοτικό κτίριο', 'municipal_building', 'Κερατσίνι', 2, 'Δημόσια περιουσία.', 3,
         ST_GeomFromText('POINT(23.623 37.961)', 4326), true, true)
        """
    )
    op.execute(
        """
        INSERT INTO cleaning_status_event
            (target_type, target_id, status, priority, source, event_date, notes, assignment_id)
        VALUES
            ('road_segment', 1, 'urgent', 1, 'supervisor', '2026-04-18', 'Υψηλή ανάγκη λόγω κεντρικού άξονα.', NULL),
            ('road_segment', 2, 'pending', 2, 'supervisor', '2026-04-18', 'Προγραμματισμένο για βάρδια.', NULL),
            ('map_asset', 1, 'urgent', 1, 'supervisor', '2026-04-18', 'Πλατεία με προτεραιότητα.', NULL),
            ('map_asset', 2, 'assigned', 2, 'supervisor', '2026-04-18', 'Ανάθεση σε συνεργείο καθαριότητας.', NULL)
        """
    )
