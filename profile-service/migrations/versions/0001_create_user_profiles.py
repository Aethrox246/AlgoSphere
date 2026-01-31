from alembic import op
import sqlalchemy as sa

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "user_profiles",
        sa.Column("user_id", sa.String(), primary_key=True),
        sa.Column("name", sa.String(length=100)),
        sa.Column("bio", sa.String(length=500)),
        sa.Column("avatar_url", sa.String(length=255)),
        sa.Column("created_at", sa.DateTime()),
    )


def downgrade():
    op.drop_table("user_profiles")
