"""create risk assessments and anomalies"""

from alembic import op
import sqlalchemy as sa

revision = "0005_assessments"
down_revision = "0004_ml_registry"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "risk_assessments",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("asset_id", sa.Integer(), sa.ForeignKey("assets.id"), nullable=False),
        sa.Column("score", sa.Float(), nullable=False),
        sa.Column("model_version", sa.String(64), nullable=False),
        sa.Column("assessed_at", sa.DateTime(), nullable=False),
    )
    op.create_table(
        "assessment_factors",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("assessment_id", sa.Integer(), sa.ForeignKey("risk_assessments.id"), nullable=False),
        sa.Column("feature", sa.String(128), nullable=False),
        sa.Column("contribution", sa.Float(), nullable=False),
    )
    op.create_table(
        "anomaly_events",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("asset_id", sa.Integer(), sa.ForeignKey("assets.id"), nullable=False),
        sa.Column("score", sa.Float(), nullable=False),
        sa.Column("status", sa.String(32), nullable=False),
        sa.Column("contributing_features", sa.JSON(), nullable=False),
        sa.Column("detected_at", sa.DateTime(), nullable=False),
        sa.Column("reviewed_by", sa.String(255)),
        sa.Column("reviewed_at", sa.DateTime()),
        sa.Column("review_note", sa.String(2000)),
    )


def downgrade() -> None:
    op.drop_table("anomaly_events")
    op.drop_table("assessment_factors")
    op.drop_table("risk_assessments")
