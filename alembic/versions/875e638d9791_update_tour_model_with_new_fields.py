"""Update Tour model with new fields

Revision ID: 875e638d9791
Revises: 001
Create Date: 2025-03-30 00:32:00.997392

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '875e638d9791'
down_revision: Union[str, None] = '001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('tours', sa.Column('duration', sa.Integer(), nullable=True))
    op.add_column('tours', sa.Column('image_url', sa.String(), nullable=True))
    op.add_column('tours', sa.Column('location', sa.String(), nullable=True))
    op.add_column('tours', sa.Column('rating', sa.Float(), nullable=True))
    op.add_column('tours', sa.Column('max_participants', sa.Integer(), nullable=True))
    op.add_column('tours', sa.Column('available_dates', sa.ARRAY(sa.DateTime()), nullable=True))
    op.alter_column('tours', 'title',
               existing_type=sa.VARCHAR(),
               nullable=True)
    op.alter_column('tours', 'description',
               existing_type=sa.TEXT(),
               nullable=True)
    op.alter_column('tours', 'price',
               existing_type=sa.DOUBLE_PRECISION(precision=53),
               nullable=True)
    op.alter_column('tours', 'available_spots',
               existing_type=sa.INTEGER(),
               nullable=True)
    op.alter_column('tours', 'is_hot',
               existing_type=sa.BOOLEAN(),
               nullable=True)
    op.alter_column('tours', 'departure_date',
               existing_type=postgresql.TIMESTAMP(),
               nullable=True)
    op.alter_column('tours', 'return_date',
               existing_type=postgresql.TIMESTAMP(),
               nullable=True)
    op.alter_column('tours', 'created_at',
               existing_type=postgresql.TIMESTAMP(),
               nullable=True)
    op.create_index(op.f('ix_tours_id'), 'tours', ['id'], unique=False)
    op.drop_column('tours', 'city')
    op.drop_column('tours', 'original_price')
    op.drop_column('tours', 'country')
    op.alter_column('travel_requests', 'user_id',
               existing_type=sa.INTEGER(),
               nullable=True)
    op.alter_column('travel_requests', 'tour_id',
               existing_type=sa.INTEGER(),
               nullable=True)
    op.alter_column('travel_requests', 'status',
               existing_type=sa.VARCHAR(),
               nullable=True)
    op.alter_column('travel_requests', 'created_at',
               existing_type=postgresql.TIMESTAMP(),
               nullable=True)
    op.alter_column('travel_requests', 'updated_at',
               existing_type=postgresql.TIMESTAMP(),
               nullable=True)
    op.create_index(op.f('ix_travel_requests_id'), 'travel_requests', ['id'], unique=False)
    op.alter_column('users', 'username',
               existing_type=sa.VARCHAR(),
               nullable=True)
    op.alter_column('users', 'email',
               existing_type=sa.VARCHAR(),
               nullable=True)
    op.alter_column('users', 'hashed_password',
               existing_type=sa.VARCHAR(),
               nullable=True)
    op.alter_column('users', 'is_active',
               existing_type=sa.BOOLEAN(),
               nullable=True)
    op.alter_column('users', 'is_admin',
               existing_type=sa.BOOLEAN(),
               nullable=True)
    op.alter_column('users', 'created_at',
               existing_type=postgresql.TIMESTAMP(),
               nullable=True)
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_users_id'), table_name='users')
    op.alter_column('users', 'created_at',
               existing_type=postgresql.TIMESTAMP(),
               nullable=False)
    op.alter_column('users', 'is_admin',
               existing_type=sa.BOOLEAN(),
               nullable=False)
    op.alter_column('users', 'is_active',
               existing_type=sa.BOOLEAN(),
               nullable=False)
    op.alter_column('users', 'hashed_password',
               existing_type=sa.VARCHAR(),
               nullable=False)
    op.alter_column('users', 'email',
               existing_type=sa.VARCHAR(),
               nullable=False)
    op.alter_column('users', 'username',
               existing_type=sa.VARCHAR(),
               nullable=False)
    op.drop_index(op.f('ix_travel_requests_id'), table_name='travel_requests')
    op.alter_column('travel_requests', 'updated_at',
               existing_type=postgresql.TIMESTAMP(),
               nullable=False)
    op.alter_column('travel_requests', 'created_at',
               existing_type=postgresql.TIMESTAMP(),
               nullable=False)
    op.alter_column('travel_requests', 'status',
               existing_type=sa.VARCHAR(),
               nullable=False)
    op.alter_column('travel_requests', 'tour_id',
               existing_type=sa.INTEGER(),
               nullable=False)
    op.alter_column('travel_requests', 'user_id',
               existing_type=sa.INTEGER(),
               nullable=False)
    op.add_column('tours', sa.Column('country', sa.VARCHAR(), autoincrement=False, nullable=False))
    op.add_column('tours', sa.Column('original_price', sa.DOUBLE_PRECISION(precision=53), autoincrement=False, nullable=False))
    op.add_column('tours', sa.Column('city', sa.VARCHAR(), autoincrement=False, nullable=False))
    op.drop_index(op.f('ix_tours_id'), table_name='tours')
    op.alter_column('tours', 'created_at',
               existing_type=postgresql.TIMESTAMP(),
               nullable=False)
    op.alter_column('tours', 'return_date',
               existing_type=postgresql.TIMESTAMP(),
               nullable=False)
    op.alter_column('tours', 'departure_date',
               existing_type=postgresql.TIMESTAMP(),
               nullable=False)
    op.alter_column('tours', 'is_hot',
               existing_type=sa.BOOLEAN(),
               nullable=False)
    op.alter_column('tours', 'available_spots',
               existing_type=sa.INTEGER(),
               nullable=False)
    op.alter_column('tours', 'price',
               existing_type=sa.DOUBLE_PRECISION(precision=53),
               nullable=False)
    op.alter_column('tours', 'description',
               existing_type=sa.TEXT(),
               nullable=False)
    op.alter_column('tours', 'title',
               existing_type=sa.VARCHAR(),
               nullable=False)
    op.drop_column('tours', 'available_dates')
    op.drop_column('tours', 'max_participants')
    op.drop_column('tours', 'rating')
    op.drop_column('tours', 'location')
    op.drop_column('tours', 'image_url')
    op.drop_column('tours', 'duration')
    # ### end Alembic commands ### 