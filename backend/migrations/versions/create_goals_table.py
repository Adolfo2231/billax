"""create goals table

Revision ID: create_goals_table
Revises: 6982032c80aa
Create Date: 2024-07-10 14:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'create_goals_table'
down_revision = '6982032c80aa'
branch_labels = None
depends_on = None


def upgrade():
    """Create goals table"""
    op.create_table('goals',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('target_amount', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('current_amount', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('deadline', sa.Date(), nullable=True),
        sa.Column('category', sa.String(length=50), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create index on user_id for better performance
    op.create_index(op.f('ix_goals_user_id'), 'goals', ['user_id'], unique=False)
    
    # Create index on status for filtering
    op.create_index(op.f('ix_goals_status'), 'goals', ['status'], unique=False)
    
    # Create index on category for filtering
    op.create_index(op.f('ix_goals_category'), 'goals', ['category'], unique=False)


def downgrade():
    """Drop goals table"""
    op.drop_index(op.f('ix_goals_category'), table_name='goals')
    op.drop_index(op.f('ix_goals_status'), table_name='goals')
    op.drop_index(op.f('ix_goals_user_id'), table_name='goals')
    op.drop_table('goals') 