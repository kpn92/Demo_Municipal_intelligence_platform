"""add settings business rules tables

Revision ID: d31e9f4a2b70
Revises: c21a8c4b92f0
Create Date: 2026-04-19 10:45:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "d31e9f4a2b70"
down_revision: Union[str, Sequence[str], None] = "c21a8c4b92f0"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


platform_module_table = sa.table(
    "platform_module",
    sa.column("id", sa.Integer),
    sa.column("code", sa.String),
    sa.column("name", sa.String),
    sa.column("description", sa.Text),
    sa.column("is_enabled", sa.Boolean),
    sa.column("is_visible", sa.Boolean),
)

role_table = sa.table(
    "role",
    sa.column("id", sa.Integer),
    sa.column("code", sa.String),
    sa.column("name", sa.String),
    sa.column("description", sa.Text),
    sa.column("is_active", sa.Boolean),
)

business_rule_table = sa.table(
    "business_rule",
    sa.column("id", sa.Integer),
    sa.column("code", sa.String),
    sa.column("name", sa.String),
    sa.column("description", sa.Text),
    sa.column("value_type", sa.String),
    sa.column("value", sa.Text),
    sa.column("is_active", sa.Boolean),
    sa.column("module_id", sa.Integer),
)


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "platform_module",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("code", sa.String(length=50), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("is_enabled", sa.Boolean(), nullable=False),
        sa.Column("is_visible", sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("code", name="uq_platform_module_code"),
    )
    op.create_index(
        "ix_platform_module_is_enabled",
        "platform_module",
        ["is_enabled"],
        unique=False,
    )

    op.create_table(
        "role",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("code", sa.String(length=50), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("code", name="uq_role_code"),
    )

    op.create_table(
        "app_user",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("username", sa.String(length=80), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=True),
        sa.Column("full_name", sa.String(length=150), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("is_superuser", sa.Boolean(), nullable=False),
        sa.Column("sector_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(["sector_id"], ["sector.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email", name="uq_app_user_email"),
        sa.UniqueConstraint("username", name="uq_app_user_username"),
    )
    op.create_index("ix_app_user_sector_id", "app_user", ["sector_id"], unique=False)

    op.create_table(
        "business_rule",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("code", sa.String(length=80), nullable=False),
        sa.Column("name", sa.String(length=150), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("value_type", sa.String(length=30), nullable=False),
        sa.Column("value", sa.Text(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("module_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(["module_id"], ["platform_module.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("code", name="uq_business_rule_code"),
    )
    op.create_index(
        "ix_business_rule_module_id",
        "business_rule",
        ["module_id"],
        unique=False,
    )

    op.create_table(
        "user_role",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("role_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["role_id"], ["role.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["app_user.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "role_id", name="uq_user_role_user_role"),
    )
    op.create_index("ix_user_role_role_id", "user_role", ["role_id"], unique=False)
    op.create_index("ix_user_role_user_id", "user_role", ["user_id"], unique=False)

    op.bulk_insert(
        platform_module_table,
        [
            {
                "id": 1,
                "code": "cleaning",
                "name": "Διαχείριση Καθαριότητας",
                "description": "Σχεδιασμός συνεργείων, περιοχών και ημερήσιων εργασιών.",
                "is_enabled": True,
                "is_visible": True,
            },
            {
                "id": 2,
                "code": "fleet",
                "name": "Στόλος",
                "description": "Οχήματα, διαθεσιμότητα και δρομολόγια απορριμματοφόρων.",
                "is_enabled": False,
                "is_visible": False,
            },
            {
                "id": 3,
                "code": "issues",
                "name": "Βλάβες",
                "description": "Καταγραφή και παρακολούθηση συμβάντων και βλαβών.",
                "is_enabled": False,
                "is_visible": False,
            },
            {
                "id": 4,
                "code": "settings",
                "name": "Ρυθμίσεις",
                "description": "Παραμετρικά στοιχεία, χρήστες, ρόλοι και κανόνες λειτουργίας.",
                "is_enabled": True,
                "is_visible": True,
            },
        ],
    )

    op.bulk_insert(
        role_table,
        [
            {
                "id": 1,
                "code": "admin",
                "name": "Διαχειριστής",
                "description": "Πλήρης πρόσβαση σε όλα τα ενεργά modules και τις ρυθμίσεις.",
                "is_active": True,
            },
            {
                "id": 2,
                "code": "cleaning_supervisor",
                "name": "Επόπτης Καθαριότητας",
                "description": "Πρόσβαση στη διαχείριση καθαριότητας και στις αναθέσεις περιοχής.",
                "is_active": True,
            },
            {
                "id": 3,
                "code": "fleet_operator",
                "name": "Χειριστής Στόλου",
                "description": "Πρόσβαση στα μελλοντικά στοιχεία στόλου και δρομολογίων.",
                "is_active": True,
            },
        ],
    )

    op.bulk_insert(
        business_rule_table,
        [
            {
                "id": 1,
                "code": "modules.cleaning.enabled",
                "name": "Ενεργό module καθαριότητας",
                "description": "Ελέγχει αν εμφανίζεται και λειτουργεί η Διαχείριση Καθαριότητας.",
                "value_type": "boolean",
                "value": "true",
                "is_active": True,
                "module_id": 1,
            },
            {
                "id": 2,
                "code": "modules.fleet.enabled",
                "name": "Ενεργό module στόλου",
                "description": "Ελέγχει την ενεργοποίηση του μελλοντικού module στόλου.",
                "value_type": "boolean",
                "value": "false",
                "is_active": True,
                "module_id": 2,
            },
            {
                "id": 3,
                "code": "modules.issues.enabled",
                "name": "Ενεργό module βλαβών",
                "description": "Ελέγχει την ενεργοποίηση του μελλοντικού module βλαβών.",
                "value_type": "boolean",
                "value": "false",
                "is_active": True,
                "module_id": 3,
            },
            {
                "id": 4,
                "code": "settings.user_management.enabled",
                "name": "Διαχείριση χρηστών",
                "description": "Επιτρέπει τη δημιουργία και επεξεργασία χρηστών από τις ρυθμίσεις.",
                "value_type": "boolean",
                "value": "true",
                "is_active": True,
                "module_id": 4,
            },
            {
                "id": 5,
                "code": "settings.role_management.enabled",
                "name": "Διαχείριση ρόλων",
                "description": "Επιτρέπει τη δημιουργία και επεξεργασία ρόλων από τις ρυθμίσεις.",
                "value_type": "boolean",
                "value": "true",
                "is_active": True,
                "module_id": 4,
            },
            {
                "id": 6,
                "code": "cleaning.auto_plan.enabled",
                "name": "Αυτόματο πλάνο καθαριότητας",
                "description": "Επιτρέπει την αυτόματη παραγωγή πλάνου με βάση ενεργούς καθαριστές και προτεραιότητες.",
                "value_type": "boolean",
                "value": "true",
                "is_active": True,
                "module_id": 1,
            },
            {
                "id": 7,
                "code": "cleaning.temporary_contracts.enabled",
                "name": "Προσωρινοί καθαριστές",
                "description": "Συμπεριλαμβάνει ενεργές συμβάσεις ορισμένου χρόνου στον υπολογισμό πλάνου.",
                "value_type": "boolean",
                "value": "true",
                "is_active": True,
                "module_id": 1,
            },
        ],
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index("ix_user_role_user_id", table_name="user_role")
    op.drop_index("ix_user_role_role_id", table_name="user_role")
    op.drop_table("user_role")
    op.drop_index("ix_business_rule_module_id", table_name="business_rule")
    op.drop_table("business_rule")
    op.drop_index("ix_app_user_sector_id", table_name="app_user")
    op.drop_table("app_user")
    op.drop_table("role")
    op.drop_index("ix_platform_module_is_enabled", table_name="platform_module")
    op.drop_table("platform_module")
