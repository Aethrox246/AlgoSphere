from alembic import op
import sqlalchemy as sa

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "user_profiles",
        sa.Column("user_id", sa.String(length=64), primary_key=True),
        sa.Column("name", sa.String(length=100)),
        sa.Column("bio", sa.String(length=500)),
        sa.Column("location", sa.String(length=100)),
        sa.Column("level", sa.String(length=50)),
        sa.Column("interests", sa.String(length=255)),
        sa.Column("avatar_url", sa.String(length=255)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )


def downgrade():
    op.drop_table("user_profiles")
