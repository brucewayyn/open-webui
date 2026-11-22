"""Track daily live voice usage."""

from alembic import op
import sqlalchemy as sa

revision = 'd8a41f9c72b3'
down_revision = '9f6c2a8d1b43'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'voice_call_usage',
        sa.Column('user_id', sa.Text(), primary_key=True),
        sa.Column('day', sa.String(10), primary_key=True),
        sa.Column('used_seconds', sa.Integer(), nullable=False),
        sa.Column('active', sa.Boolean(), nullable=False),
    )


def downgrade():
    op.drop_table('voice_call_usage')
