"""create vulnerability catalog"""

from alembic import op
import sqlalchemy as sa

revision = "0003_vulnerabilities"
down_revision = "0002_scans"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "vulnerability_catalog",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("cve_id", sa.String(32), nullable=False, unique=True),
        sa.Column("description", sa.String(4000)),
        sa.Column("cvss_score", sa.Float()),
        sa.Column("epss_score", sa.Float()),
        sa.Column("is_kev", sa.Boolean(), nullable=False),
        sa.Column("retrieved_at", sa.DateTime(), nullable=False),
        sa.Column("kev_retrieved_at", sa.DateTime()),
        sa.Column("epss_retrieved_at", sa.DateTime()),
    )
    op.create_index("ix_vulnerability_catalog_cve_id", "vulnerability_catalog", ["cve_id"])
    op.create_table(
        "asset_vulnerabilities",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("asset_id", sa.Integer(), sa.ForeignKey("assets.id"), nullable=False),
        sa.Column("vulnerability_id", sa.Integer(), sa.ForeignKey("vulnerability_catalog.id"), nullable=False),
        sa.Column("evidence", sa.JSON(), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("asset_vulnerabilities")
    op.drop_index("ix_vulnerability_catalog_cve_id", table_name="vulnerability_catalog")
    op.drop_table("vulnerability_catalog")
