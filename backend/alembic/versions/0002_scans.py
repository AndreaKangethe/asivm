"""create scans and observations"""

from alembic import op
import sqlalchemy as sa

revision = "0002_scans"
down_revision = "0001_assets"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "scans",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("started_at", sa.DateTime(), nullable=False),
        sa.Column("completed_at", sa.DateTime()),
        sa.Column("status", sa.String(32), nullable=False),
    )
    op.create_table(
        "asset_observations",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("scan_id", sa.Integer(), sa.ForeignKey("scans.id"), nullable=False),
        sa.Column("asset_id", sa.Integer(), sa.ForeignKey("assets.id")),
        sa.Column("identifier_type", sa.String(64), nullable=False),
        sa.Column("identifier_value", sa.String(255), nullable=False),
        sa.Column("observed_at", sa.DateTime(), nullable=False),
        sa.Column("payload", sa.JSON(), nullable=False),
        sa.Column("error", sa.Text()),
    )


def downgrade() -> None:
    op.drop_table("asset_observations")
    op.drop_table("scans")
