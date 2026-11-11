"""add risk review and model lifecycle audit tables"""

from alembic import op
import sqlalchemy as sa

revision = "0008_lifecycle_audit"
down_revision = "0007_intelligence_history"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "model_lifecycle_events",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("model_version_id", sa.Integer(), sa.ForeignKey("ml_model_versions.id"), nullable=False),
        sa.Column("event_type", sa.String(32), nullable=False),
        sa.Column("actor", sa.String(255), nullable=False),
        sa.Column("occurred_at", sa.DateTime(), nullable=False),
        sa.Column("details", sa.JSON(), nullable=False),
    )
    op.create_index("ix_model_lifecycle_events_model_version_id", "model_lifecycle_events", ["model_version_id"])

    op.create_table(
        "risk_assessment_reviews",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("assessment_id", sa.Integer(), sa.ForeignKey("risk_assessments.id"), nullable=False),
        sa.Column("decision", sa.String(32), nullable=False),
        sa.Column("reviewer", sa.String(255), nullable=False),
        sa.Column("reviewed_at", sa.DateTime(), nullable=False),
        sa.Column("corrected_class", sa.Integer(), nullable=True),
        sa.Column("justification", sa.String(4000), nullable=False),
        sa.Column("validated_label_id", sa.Integer(), sa.ForeignKey("risk_labels.id"), nullable=True),
    )
    op.create_index("ix_risk_assessment_reviews_assessment_id", "risk_assessment_reviews", ["assessment_id"])


def downgrade() -> None:
    op.drop_table("risk_assessment_reviews")
    op.drop_table("model_lifecycle_events")
