"""add vulnerability intelligence history and ingestion audit schema"""

from alembic import op
import sqlalchemy as sa

revision = "0007_intelligence_history"
down_revision = "0006_v3_contract"
branch_labels = None
depends_on = None


def upgrade() -> None:
    for name, column in (
        ("vulnerability_catalog", sa.Column("cvss_version", sa.String(16), nullable=True)),
        ("vulnerability_catalog", sa.Column("cvss_published_at", sa.DateTime(), nullable=True)),
        ("vulnerability_catalog", sa.Column("epss_percentile", sa.Float(), nullable=True)),
        ("vulnerability_catalog", sa.Column("epss_score_date", sa.DateTime(), nullable=True)),
        ("vulnerability_catalog", sa.Column("kev_date_added", sa.DateTime(), nullable=True)),
        ("vulnerability_catalog", sa.Column("kev_due_date", sa.DateTime(), nullable=True)),
        ("vulnerability_catalog", sa.Column("kev_required_action", sa.Text(), nullable=True)),
        ("vulnerability_catalog", sa.Column("kev_ransomware_use", sa.String(32), nullable=True)),
        ("vulnerability_catalog", sa.Column("source_provenance", sa.JSON(), nullable=False, server_default="{}")),
        ("asset_vulnerabilities", sa.Column("observed_at", sa.DateTime(), nullable=True)),
        ("asset_vulnerabilities", sa.Column("valid_from", sa.DateTime(), nullable=True)),
        ("asset_vulnerabilities", sa.Column("valid_to", sa.DateTime(), nullable=True)),
    ):
        op.add_column(name, column)

    op.create_table(
        "vulnerability_intelligence_snapshots",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("cve_id", sa.String(32), nullable=False),
        sa.Column("source", sa.String(32), nullable=False),
        sa.Column("source_version", sa.String(128), nullable=True),
        sa.Column("effective_at", sa.DateTime(), nullable=False),
        sa.Column("retrieved_at", sa.DateTime(), nullable=False),
        sa.Column("payload_hash", sa.String(128), nullable=False, unique=True),
        sa.Column("payload", sa.JSON(), nullable=False),
    )
    op.create_index("ix_vulnerability_intelligence_snapshots_cve_id", "vulnerability_intelligence_snapshots", ["cve_id"])
    op.create_index("ix_vulnerability_intelligence_snapshots_source", "vulnerability_intelligence_snapshots", ["source"])
    op.create_index("ix_vulnerability_intelligence_snapshots_effective_at", "vulnerability_intelligence_snapshots", ["effective_at"])
    op.create_index("ix_vulnerability_snapshot_lookup", "vulnerability_intelligence_snapshots", ["cve_id", "source", "effective_at"])
    op.create_index("ix_vulnerability_intelligence_snapshots_payload_hash", "vulnerability_intelligence_snapshots", ["payload_hash"])

    op.create_table(
        "vulnerability_ingestion_runs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("source", sa.String(32), nullable=False),
        sa.Column("source_version", sa.String(128), nullable=True),
        sa.Column("started_at", sa.DateTime(), nullable=False),
        sa.Column("completed_at", sa.DateTime(), nullable=True),
        sa.Column("status", sa.String(32), nullable=False),
        sa.Column("records_seen", sa.Integer(), nullable=False),
        sa.Column("records_imported", sa.Integer(), nullable=False),
        sa.Column("error", sa.Text(), nullable=True),
    )
    op.create_index("ix_vulnerability_ingestion_runs_source", "vulnerability_ingestion_runs", ["source"])


def downgrade() -> None:
    op.drop_table("vulnerability_ingestion_runs")
    op.drop_table("vulnerability_intelligence_snapshots")
    for name, column in (
        ("asset_vulnerabilities", "valid_to"),
        ("asset_vulnerabilities", "valid_from"),
        ("asset_vulnerabilities", "observed_at"),
        ("vulnerability_catalog", "source_provenance"),
        ("vulnerability_catalog", "kev_ransomware_use"),
        ("vulnerability_catalog", "kev_required_action"),
        ("vulnerability_catalog", "kev_due_date"),
        ("vulnerability_catalog", "kev_date_added"),
        ("vulnerability_catalog", "epss_score_date"),
        ("vulnerability_catalog", "epss_percentile"),
        ("vulnerability_catalog", "cvss_published_at"),
        ("vulnerability_catalog", "cvss_version"),
    ):
        op.drop_column(name, column)
