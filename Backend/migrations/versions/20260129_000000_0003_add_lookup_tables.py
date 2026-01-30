"""Add lookup tables for Brand, Color, Condition, LCI Definition
and update ProductFamily with additional fields.

Revision ID: 0003
Revises: 0002
Create Date: 2026-01-29

This migration adds:
- brand table for manufacturer/brand lookup
- color table for color name and code lookup
- condition table for condition name and code lookup
- lci_definition table for LCI number to component name mapping
- New fields to product_family: brand_id, dimensions, weight, kit_included_products
- Updates identity_type_enum to replace 'Base' with 'Product'
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0003'
down_revision: Union[str, None] = '0002_add_users'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ========================================================================
    # Update identity_type_enum to replace 'Base' with 'Product'
    # ========================================================================
    # Rename existing enum value (PostgreSQL supports this)
    op.execute("ALTER TYPE identity_type_enum RENAME VALUE 'Base' TO 'Product'")
    
    # Remove 'S' (Service) from enum - this is more complex, 
    # we'll leave it for now as unused values don't hurt
    
    # ========================================================================
    # BRAND TABLE - Manufacturer/Brand lookup
    # ========================================================================
    op.create_table(
        'brand',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False,
                  comment="Brand name (e.g., 'Bose', 'USAV Solutions')."),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name', name='uq_brand_name')
    )
    
    # ========================================================================
    # COLOR TABLE - Color name and code lookup
    # ========================================================================
    op.create_table(
        'color',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('name', sa.String(length=50), nullable=False,
                  comment="Color name (e.g., 'Black', 'White')."),
        sa.Column('code', sa.String(length=2), nullable=False,
                  comment="Color code (e.g., 'BK', 'WY')."),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name', name='uq_color_name'),
        sa.UniqueConstraint('code', name='uq_color_code')
    )
    
    # ========================================================================
    # CONDITION TABLE - Condition name and code lookup
    # ========================================================================
    op.create_table(
        'condition',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('name', sa.String(length=50), nullable=False,
                  comment="Condition name (e.g., 'Used', 'New')."),
        sa.Column('code', sa.String(length=1), nullable=False,
                  comment="Condition code (e.g., 'U', 'N')."),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name', name='uq_condition_name'),
        sa.UniqueConstraint('code', name='uq_condition_code')
    )
    
    # ========================================================================
    # LCI_DEFINITION TABLE - Maps LCI numbers to component names per product
    # ========================================================================
    op.create_table(
        'lci_definition',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('product_id', sa.Integer(), nullable=False,
                  comment='Links to Product Family.'),
        sa.Column('lci_index', sa.Integer(), nullable=False,
                  comment='LCI number (1-99).'),
        sa.Column('component_name', sa.String(length=100), nullable=False,
                  comment="Component name (e.g., 'Motherboard', 'Power Supply')."),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.CheckConstraint('lci_index >= 1 AND lci_index <= 99', name='ck_lci_index_range'),
        sa.ForeignKeyConstraint(['product_id'], ['product_family.product_id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('product_id', 'lci_index', name='uq_lci_product_index')
    )
    op.create_index('ix_lci_product_id', 'lci_definition', ['product_id'])
    
    # ========================================================================
    # Add new columns to PRODUCT_FAMILY
    # ========================================================================
    op.add_column('product_family', sa.Column(
        'brand_id', sa.BigInteger(), nullable=True,
        comment='Links to Brand.'
    ))
    op.add_column('product_family', sa.Column(
        'dimension_length', sa.Numeric(precision=10, scale=2), nullable=True,
        comment='Product length in inches.'
    ))
    op.add_column('product_family', sa.Column(
        'dimension_width', sa.Numeric(precision=10, scale=2), nullable=True,
        comment='Product width in inches.'
    ))
    op.add_column('product_family', sa.Column(
        'dimension_height', sa.Numeric(precision=10, scale=2), nullable=True,
        comment='Product height in inches.'
    ))
    op.add_column('product_family', sa.Column(
        'weight', sa.Numeric(precision=10, scale=2), nullable=True,
        comment='Product weight in pounds.'
    ))
    op.add_column('product_family', sa.Column(
        'kit_included_products', sa.Text(), nullable=True,
        comment='Comma-separated list of included products for Kit type.'
    ))
    
    # Add foreign key constraint for brand_id
    op.create_foreign_key(
        'fk_product_family_brand',
        'product_family', 'brand',
        ['brand_id'], ['id'],
        ondelete='SET NULL'
    )
    op.create_index('ix_product_family_brand', 'product_family', ['brand_id'])
    
    # ========================================================================
    # Seed default colors
    # ========================================================================
    op.execute("""
        INSERT INTO color (name, code) VALUES
        ('Black', 'BK'),
        ('White', 'WY'),
        ('Silver', 'SV'),
        ('Gray', 'GR'),
        ('Red', 'RD'),
        ('Blue', 'BL'),
        ('Green', 'GN'),
        ('Gold', 'GD')
    """)
    
    # ========================================================================
    # Seed default conditions
    # ========================================================================
    op.execute("""
        INSERT INTO condition (name, code) VALUES
        ('Used', 'U'),
        ('New', 'N'),
        ('Refurbished', 'R')
    """)
    
    # ========================================================================
    # Seed common brands
    # ========================================================================
    op.execute("""
        INSERT INTO brand (name) VALUES
        ('Bose'),
        ('USAV Solutions'),
        ('Mad Catz'),
        ('ACTIVISION'),
        ('Altec Lansing'),
        ('Nintendo'),
        ('Sony'),
        ('Panasonic'),
        ('Definitive Technology')
    """)


def downgrade() -> None:
    # Drop indexes
    op.drop_index('ix_product_family_brand', table_name='product_family')
    op.drop_index('ix_lci_product_id', table_name='lci_definition')
    
    # Drop foreign key
    op.drop_constraint('fk_product_family_brand', 'product_family', type_='foreignkey')
    
    # Drop new columns from product_family
    op.drop_column('product_family', 'kit_included_products')
    op.drop_column('product_family', 'weight')
    op.drop_column('product_family', 'dimension_height')
    op.drop_column('product_family', 'dimension_width')
    op.drop_column('product_family', 'dimension_length')
    op.drop_column('product_family', 'brand_id')
    
    # Drop tables
    op.drop_table('lci_definition')
    op.drop_table('condition')
    op.drop_table('color')
    op.drop_table('brand')
    
    # Revert enum change
    op.execute("ALTER TYPE identity_type_enum RENAME VALUE 'Product' TO 'Base'")
