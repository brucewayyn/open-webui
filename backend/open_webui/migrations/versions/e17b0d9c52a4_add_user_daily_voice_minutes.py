"""Store admin-managed daily voice limits on user accounts."""

from alembic import op
import sqlalchemy as sa

revision = 'e17b0d9c52a4'
down_revision = 'd8a41f9c72b3'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('user', sa.Column('daily_voice_minutes', sa.Integer(), nullable=True))


def downgrade():
    op.drop_column('user', 'daily_voice_minutes')
