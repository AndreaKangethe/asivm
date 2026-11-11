"""create model registry tables"""

from alembic import op
import sqlalchemy as sa

revision = "0004_ml_registry"
down_revision = "0003_vulnerabilities"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "ml_model_versions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(64), nullable=False),
        sa.Column("version", sa.String(64), nullable=False, unique=True),
        sa.Column("artifact_path", sa.String(512), nullable=False),
        sa.Column("feature_version", sa.String(32), nullable=False),
        sa.Column("metrics", sa.JSON(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
    )
    op.create_table(
        "ml_training_runs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("model_version_id", sa.Integer(), sa.ForeignKey("ml_model_versions.id")),
        sa.Column("started_at", sa.DateTime(), nullable=False),
        sa.Column("completed_at", sa.DateTime()),
        sa.Column("status", sa.String(32), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("ml_training_runs")
    op.drop_table("ml_model_versions")
