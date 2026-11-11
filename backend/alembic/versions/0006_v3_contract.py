"""add v3 risk contract and label provenance tables"""

from alembic import op
import sqlalchemy as sa

revision = "0006_v3_contract"
down_revision = "0005_assessments"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("assets", sa.Column("criticality_score", sa.Float(), nullable=True))
    op.add_column("assets", sa.Column("criticality_source", sa.String(128), nullable=True))
    op.add_column("assets", sa.Column("criticality_updated_at", sa.DateTime(), nullable=True))

    op.add_column("ml_model_versions", sa.Column("feature_names", sa.JSON(), nullable=False, server_default="[]"))
    op.add_column("ml_model_versions", sa.Column("contract_hash", sa.String(128), nullable=True))
    op.add_column("ml_model_versions", sa.Column("training_metadata", sa.JSON(), nullable=False, server_default="{}"))
    op.add_column("ml_model_versions", sa.Column("deployment_mode", sa.String(32), nullable=False, server_default="active"))

    op.add_column("risk_assessments", sa.Column("risk_class", sa.Integer(), nullable=True))
    op.add_column("risk_assessments", sa.Column("observation_id", sa.Integer(), sa.ForeignKey("asset_observations.id"), nullable=True))
    op.add_column("risk_assessments", sa.Column("deployment_mode", sa.String(32), nullable=False, server_default="active"))

    op.create_table(
        "risk_labels",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("asset_id", sa.Integer(), sa.ForeignKey("assets.id"), nullable=False),
        sa.Column("observation_id", sa.Integer(), sa.ForeignKey("asset_observations.id"), nullable=False),
        sa.Column("risk_class", sa.Integer(), nullable=False),
        sa.Column("label_source", sa.String(64), nullable=False),
        sa.Column("reviewer", sa.String(255), nullable=False),
        sa.Column("assessed_at", sa.DateTime(), nullable=False),
        sa.Column("justification", sa.String(4000), nullable=False),
        sa.Column("label_version", sa.String(32), nullable=False),
        sa.CheckConstraint("risk_class IN (0, 1, 2)", name="ck_risk_label_class"),
    )
    op.create_index("ix_risk_labels_asset_id", "risk_labels", ["asset_id"])
    op.create_index("ix_risk_labels_observation_id", "risk_labels", ["observation_id"])

    op.create_table(
        "exploitation_outcomes",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("asset_id", sa.Integer(), sa.ForeignKey("assets.id"), nullable=False),
        sa.Column("observation_id", sa.Integer(), sa.ForeignKey("asset_observations.id"), nullable=True),
        sa.Column("outcome_type", sa.String(128), nullable=False),
        sa.Column("occurred_at", sa.DateTime(), nullable=False),
        sa.Column("verified_at", sa.DateTime(), nullable=False),
        sa.Column("verifier", sa.String(255), nullable=False),
        sa.Column("evidence", sa.JSON(), nullable=False),
        sa.Column("source", sa.String(128), nullable=False),
    )
    op.create_index("ix_exploitation_outcomes_asset_id", "exploitation_outcomes", ["asset_id"])
    op.create_index("ix_exploitation_outcomes_observation_id", "exploitation_outcomes", ["observation_id"])

    op.create_table(
        "training_dataset_rows",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("dataset_version", sa.String(128), nullable=False),
        sa.Column("asset_id", sa.Integer(), sa.ForeignKey("assets.id"), nullable=False),
        sa.Column("observation_id", sa.Integer(), sa.ForeignKey("asset_observations.id"), nullable=False),
        sa.Column("observed_at", sa.DateTime(), nullable=False),
        sa.Column("feature_version", sa.String(32), nullable=False),
        sa.Column("feature_values", sa.JSON(), nullable=False),
        sa.Column("vulnerability_relationships", sa.JSON(), nullable=False),
        sa.Column("intelligence_provenance", sa.JSON(), nullable=False),
        sa.Column("risk_label_id", sa.Integer(), sa.ForeignKey("risk_labels.id"), nullable=False),
        sa.Column("row_hash", sa.String(128), nullable=False, unique=True),
    )
    op.create_index("ix_training_dataset_rows_dataset_version", "training_dataset_rows", ["dataset_version"])
    op.create_index("ix_training_dataset_rows_asset_id", "training_dataset_rows", ["asset_id"])
    op.create_index("ix_training_dataset_rows_observation_id", "training_dataset_rows", ["observation_id"])
    op.create_index("ix_training_dataset_rows_observed_at", "training_dataset_rows", ["observed_at"])
    op.create_index("ix_training_dataset_rows_risk_label_id", "training_dataset_rows", ["risk_label_id"])
    op.create_index("ix_training_dataset_rows_row_hash", "training_dataset_rows", ["row_hash"])


def downgrade() -> None:
    op.drop_table("training_dataset_rows")
    op.drop_table("exploitation_outcomes")
    op.drop_table("risk_labels")
    op.drop_column("risk_assessments", "deployment_mode")
    op.drop_column("risk_assessments", "observation_id")
    op.drop_column("risk_assessments", "risk_class")
    op.drop_column("ml_model_versions", "deployment_mode")
    op.drop_column("ml_model_versions", "training_metadata")
    op.drop_column("ml_model_versions", "contract_hash")
    op.drop_column("ml_model_versions", "feature_names")
    op.drop_column("assets", "criticality_updated_at")
    op.drop_column("assets", "criticality_source")
    op.drop_column("assets", "criticality_score")
