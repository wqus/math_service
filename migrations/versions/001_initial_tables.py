"""initial tables

Revision ID: 001
Revises:
Create Date: 2026-04-04 12:00:00.000000
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import BIGINT, INTEGER, TEXT, TIMESTAMP, BOOLEAN

# revision identifiers
revision = '001'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    # 1. Таблица users
    op.create_table(
        'users',
        sa.Column('id', INTEGER, autoincrement=True, nullable=False),
        sa.Column('user_id', BIGINT, nullable=False, unique=True),
        sa.Column('created_at', TIMESTAMP(timezone=True), server_default=sa.text('now()')),
        sa.Column('language', TEXT, server_default='RU', nullable=False),
        sa.Column('premium_until', TIMESTAMP(timezone=True), nullable=True),
        sa.Column('premium_plan', TEXT, nullable=True),
        sa.Column('last_premium_at', TIMESTAMP(timezone=True), nullable=True),
        sa.Column('free_attempts_reset', TIMESTAMP(timezone=True), nullable=True),
        sa.Column('free_attempts_left', INTEGER, server_default='5'),
        sa.Column('role', TEXT, server_default='normal'),
        sa.Column('role_before_ban', TEXT, nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', name='users_user_id_key')
    )

    # 2. Таблица history
    op.create_table(
        'history',
        sa.Column('id', INTEGER, autoincrement=True, nullable=False),
        sa.Column('user_id', BIGINT, nullable=True),
        sa.Column('input_message', TEXT, nullable=True),
        sa.Column('output_message', TEXT, nullable=True),
        sa.Column('created_at', TIMESTAMP(timezone=True), server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id')
    )

    # 3. Таблица banned_users
    op.create_table(
        'banned_users',
        sa.Column('id', INTEGER, autoincrement=True, nullable=False),
        sa.Column('user_id', BIGINT, nullable=True),
        sa.Column('banned_by', BIGINT, nullable=True),
        sa.Column('banned_at', TIMESTAMP(timezone=True), nullable=True),
        sa.Column('reason', TEXT, nullable=True),
        sa.Column('active', BOOLEAN, server_default=sa.text('true')),
        sa.PrimaryKeyConstraint('id')
    )

    # 4. Таблица stars_transactions
    op.create_table(
        'stars_transactions',
        sa.Column('id', INTEGER, autoincrement=True, nullable=False),
        sa.Column('user_id', BIGINT, nullable=True),
        sa.Column('payload', TEXT, nullable=False),
        sa.Column('amount', INTEGER, nullable=False),
        sa.Column('purchased_at', TIMESTAMP(timezone=True), server_default=sa.text('now()')),
        sa.Column('charge_id', TEXT, nullable=False),
        sa.Column('status', TEXT, server_default='success'),
        sa.Column('refund_at', TIMESTAMP(timezone=True), nullable=True),
        sa.Column('product_type', TEXT, nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('charge_id', name='unique_charge_id')
    )

    # 5. Таблица support_messages
    op.create_table(
        'support_messages',
        sa.Column('id', INTEGER, autoincrement=True, nullable=False),
        sa.Column('user_id', BIGINT, nullable=True),
        sa.Column('send_time', TIMESTAMP(timezone=True), server_default=sa.text('now()')),
        sa.Column('message', TEXT, nullable=False),
        sa.Column('status', TEXT, server_default='open'),
        sa.Column('answered_by', BIGINT, nullable=True),
        sa.Column('answered_at', TIMESTAMP(timezone=True), nullable=True),
        sa.Column('answer_message', TEXT, nullable=True),
        sa.Column('rating', INTEGER, nullable=True),
        sa.PrimaryKeyConstraint('id')
    )

    # Внешние ключи
    op.create_foreign_key(
        'history_user_id_fkey', 'history', 'users',
        ['user_id'], ['user_id'], ondelete='CASCADE'
    )
    op.create_foreign_key(
        'banned_users_user_id_fkey', 'banned_users', 'users',
        ['user_id'], ['user_id']
    )
    op.create_foreign_key(
        'fk_banned_users_banned_by', 'banned_users', 'users',
        ['banned_by'], ['user_id']
    )
    op.create_foreign_key(
        'stars_transactions_user_id_fkey', 'stars_transactions', 'users',
        ['user_id'], ['user_id']
    )
    op.create_foreign_key(
        'support_messages_user_id_fkey', 'support_messages', 'users',
        ['user_id'], ['user_id']
    )
    op.create_foreign_key(
        'support_messages_answered_by_fkey', 'support_messages', 'users',
        ['answered_by'], ['user_id']
    )

    # Индексы
    op.create_index('idx_history_user_id_created_at', 'history', ['user_id', 'created_at'])
    op.create_index('idx_history_user_id', 'history', ['user_id'])
    op.create_index('idx_banned_users_active_id', 'banned_users', ['active', 'id'])
    op.create_index('idx_support_messages_status_id', 'support_messages', ['status', 'id'])
    op.create_index('idx_support_messages_user_id', 'support_messages', ['user_id'])
    op.create_index('idx_stars_transactions_user_id', 'stars_transactions', ['user_id'])
    op.create_index('idx_users_user_id', 'users', ['user_id'])

def downgrade():
    # Удаляем индексы
    op.drop_index('idx_users_user_id', table_name='users')
    op.drop_index('idx_stars_transactions_user_id', table_name='stars_transactions')
    op.drop_index('idx_support_messages_user_id', table_name='support_messages')
    op.drop_index('idx_support_messages_status_id', table_name='support_messages')
    op.drop_index('idx_banned_users_active_id', table_name='banned_users')
    op.drop_index('idx_history_user_id', table_name='history')
    op.drop_index('idx_history_user_id_created_at', table_name='history')

    # Удаляем внешние ключи
    op.drop_constraint('support_messages_answered_by_fkey', 'support_messages', type_='foreignkey')
    op.drop_constraint('support_messages_user_id_fkey', 'support_messages', type_='foreignkey')
    op.drop_constraint('stars_transactions_user_id_fkey', 'stars_transactions', type_='foreignkey')
    op.drop_constraint('fk_banned_users_banned_by', 'banned_users', type_='foreignkey')
    op.drop_constraint('banned_users_user_id_fkey', 'banned_users', type_='foreignkey')
    op.drop_constraint('history_user_id_fkey', 'history', type_='foreignkey')

    # Удаляем таблицы
    op.drop_table('support_messages')
    op.drop_table('stars_transactions')
    op.drop_table('banned_users')
    op.drop_table('history')
    op.drop_table('users')