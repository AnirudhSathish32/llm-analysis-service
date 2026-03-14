"""initial schema - create all tables

Revision ID: 0001
Revises: 
Create Date: 2024-01-01 00:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSON

revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "documents",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("filename", sa.String(), nullable=False),
        sa.Column("file_type", sa.String(), nullable=False),
        sa.Column("status", sa.String(), nullable=False),
        sa.Column("chunk_count", sa.Integer(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
        ),
    )

    op.create_table(
        "analysis_requests",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("input_hash", sa.String(), nullable=False, index=True),
        sa.Column("analysis_type", sa.String(), nullable=False),
        sa.Column("prompt_version", sa.String(), nullable=False),
        sa.Column("status", sa.String(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
        ),
    )

    op.create_table(
        "analysis_results",
        sa.Column(
            "request_id",
            UUID(as_uuid=True),
            sa.ForeignKey("analysis_requests.id"),
            primary_key=True,
        ),
        sa.Column("result", JSON(), nullable=True),
        sa.Column("duration_ms", sa.Integer()),
        sa.Column("token_usage", sa.Integer()),
        sa.Column("cost_usd", sa.Numeric(10, 4)),
    )


def downgrade() -> None:
    op.drop_table("analysis_results")
    op.drop_table("analysis_requests")
    op.drop_table("documents")
