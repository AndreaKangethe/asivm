"""create assets and identifiers"""

from alembic import op
import sqlalchemy as sa

revision = "0001_assets"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "assets",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.UniqueConstraint("name"),
    )
    op.create_index("ix_assets_name", "assets", ["name"])
    op.create_table(
        "asset_identifiers",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("asset_id", sa.Integer(), sa.ForeignKey("assets.id"), nullable=False),
        sa.Column("identifier_type", sa.String(64), nullable=False),
        sa.Column("value", sa.String(255), nullable=False),
        sa.Column("valid_from", sa.DateTime(), nullable=False),
        sa.Column("valid_to", sa.DateTime()),
    )
    op.create_index("ix_asset_identifiers_asset_id", "asset_identifiers", ["asset_id"])
    op.create_index("ix_asset_identifier_lookup", "asset_identifiers", ["identifier_type", "value"])
    op.create_index(
        "uq_active_asset_identifier",
        "asset_identifiers",
        ["identifier_type", "value"],
        unique=True,
        postgresql_where=sa.text("valid_to IS NULL"),
        sqlite_where=sa.text("valid_to IS NULL"),
    )


def downgrade() -> None:
    op.drop_index("ix_asset_identifier_lookup", table_name="asset_identifiers")
    op.drop_index("uq_active_asset_identifier", table_name="asset_identifiers")
    op.drop_index("ix_asset_identifiers_asset_id", table_name="asset_identifiers")
    op.drop_table("asset_identifiers")
    op.drop_index("ix_assets_name", table_name="assets")
    op.drop_table("assets")
