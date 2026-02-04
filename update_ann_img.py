"""add image_url to announcements

Revision ID: add_announcement_image
Revises: 29de38c4d25d
Create Date: 2026-02-04

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_announcement_image'
down_revision = '29de38c4d25d'
branch_labels = None
depends_on = None


def upgrade():
    # Add image_url column to announcements table
    with op.batch_alter_table('announcements', schema=None) as batch_op:
        batch_op.add_column(sa.Column('image_url', sa.String(length=500), nullable=True))


def downgrade():
    # Remove image_url column from announcements table
    with op.batch_alter_table('announcements', schema=None) as batch_op:
        batch_op.drop_column('image_url')