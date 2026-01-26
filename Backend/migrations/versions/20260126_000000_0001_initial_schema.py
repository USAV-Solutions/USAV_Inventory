"""Initial schema creation

Revision ID: 0001
Revises: 
Create Date: 2026-01-26

This migration creates the complete USAV Inventory Database schema
implementing the Two-Layer Identification Model.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '0001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# Define enum types with create_type=False since we create them manually
identity_type_enum = postgresql.ENUM('Base', 'B', 'P', 'K', 'S', name='identity_type_enum', create_type=False)
physical_class_enum = postgresql.ENUM('E', 'C', 'P', 'S', 'W', 'A', name='physical_class_enum', create_type=False)
condition_code_enum = postgresql.ENUM('N', 'R', name='condition_code_enum', create_type=False)
zoho_sync_status_enum = postgresql.ENUM('PENDING', 'SYNCED', 'ERROR', 'DIRTY', name='zoho_sync_status_enum', create_type=False)
platform_sync_status_enum = postgresql.ENUM('PENDING', 'SYNCED', 'ERROR', name='platform_sync_status_enum', create_type=False)
inventory_status_enum = postgresql.ENUM('AVAILABLE', 'SOLD', 'RESERVED', 'RMA', 'DAMAGED', name='inventory_status_enum', create_type=False)
bundle_role_enum = postgresql.ENUM('Primary', 'Accessory', 'Satellite', name='bundle_role_enum', create_type=False)
platform_enum = postgresql.ENUM('ZOHO', 'AMAZON_US', 'AMAZON_CA', 'EBAY', 'ECWID', name='platform_enum', create_type=False)


def upgrade() -> None:
    # Create enum types explicitly
    identity_type_enum.create(op.get_bind(), checkfirst=True)
    physical_class_enum.create(op.get_bind(), checkfirst=True)
    condition_code_enum.create(op.get_bind(), checkfirst=True)
    zoho_sync_status_enum.create(op.get_bind(), checkfirst=True)
    platform_sync_status_enum.create(op.get_bind(), checkfirst=True)
    inventory_status_enum.create(op.get_bind(), checkfirst=True)
    bundle_role_enum.create(op.get_bind(), checkfirst=True)
    platform_enum.create(op.get_bind(), checkfirst=True)

    # ========================================================================
    # PRODUCT_FAMILY - Top-level product grouping
    # ========================================================================
    op.create_table(
        'product_family',
        sa.Column('product_id', sa.Integer(), nullable=False, 
                  comment='The 5-digit ECWID ID (e.g., 00845). Acts as namespace root.'),
        sa.Column('base_name', sa.String(length=255), nullable=False,
                  comment="Human-readable name (e.g., 'Bose 201 Series')."),
        sa.Column('description', sa.Text(), nullable=True,
                  comment='Optional detailed description.'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.CheckConstraint('product_id >= 0 AND product_id <= 99999', name='ck_product_family_id_range'),
        sa.PrimaryKeyConstraint('product_id')
    )

    # ========================================================================
    # PRODUCT_IDENTITY - Layer 1: Engineering Layer (UPIS-H)
    # ========================================================================
    op.create_table(
        'product_identity',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('product_id', sa.Integer(), nullable=False,
                  comment='Links to Family.'),
        sa.Column('type', identity_type_enum, nullable=False,
                  comment='B (Bundle), P (Part), K (Kit), S (Service), Base (Product).'),
        sa.Column('lci', sa.Integer(), nullable=True,
                  comment='Local Component Index (1-99). NULL unless Type=P.'),
        sa.Column('physical_class', physical_class_enum, nullable=True,
                  comment='Registry Code: E (Electronics), C (Cover), etc.'),
        sa.Column('generated_upis_h', sa.String(length=50), nullable=False,
                  comment="Computed identity string (e.g., '00845-P-1')."),
        sa.Column('hex_signature', sa.String(length=8), nullable=False,
                  comment='32-bit HEX encoding. IMMUTABLE after creation.'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.CheckConstraint('(lci IS NULL) OR (lci >= 1 AND lci <= 99)', name='ck_identity_lci_range'),
        sa.CheckConstraint("(type = 'P' AND lci IS NOT NULL) OR (type != 'P' AND lci IS NULL)", 
                          name='ck_identity_lci_type_constraint'),
        sa.ForeignKeyConstraint(['product_id'], ['product_family.product_id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('generated_upis_h'),
        sa.UniqueConstraint('product_id', 'type', 'lci', name='uq_identity_product_type_lci')
    )
    op.create_index('ix_identity_product_id', 'product_identity', ['product_id'])
    op.create_index('ix_identity_hex_signature', 'product_identity', ['hex_signature'])

    # ========================================================================
    # PRODUCT_VARIANT - Layer 2: Sales Layer (Sellable SKUs)
    # ========================================================================
    op.create_table(
        'product_variant',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('identity_id', sa.BigInteger(), nullable=False,
                  comment='Links to the immutable Identity.'),
        sa.Column('color_code', sa.String(length=2), nullable=True,
                  comment='BK, WY, SV (See Color Index in Spec).'),
        sa.Column('condition_code', condition_code_enum, nullable=True,
                  comment='N (New), R (Repair), or NULL (Used/Default).'),
        sa.Column('full_sku', sa.String(length=100), nullable=False,
                  comment="Complete sellable string (e.g., '00845-P-1-WY-N')."),
        sa.Column('zoho_item_id', sa.String(length=50), nullable=True,
                  comment='Item ID on Zoho Inventory System.'),
        sa.Column('zoho_sync_status', zoho_sync_status_enum, nullable=False, server_default='PENDING',
                  comment='Sync status with Zoho.'),
        sa.Column('zoho_last_synced_at', sa.DateTime(timezone=True), nullable=True,
                  comment='Last successful sync timestamp.'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true',
                  comment='Soft-delete flag for discontinued variants.'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['identity_id'], ['product_identity.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('full_sku'),
        sa.UniqueConstraint('identity_id', 'color_code', 'condition_code', name='uq_variant_identity_color_condition')
    )
    op.create_index('ix_variant_identity_id', 'product_variant', ['identity_id'])
    op.create_index('ix_variant_zoho_item_id', 'product_variant', ['zoho_item_id'])
    op.create_index('ix_variant_zoho_sync_status', 'product_variant', ['zoho_sync_status'])
    op.create_index('ix_variant_is_active', 'product_variant', ['is_active'])

    # ========================================================================
    # BUNDLE_COMPONENT - Bill of Materials
    # ========================================================================
    op.create_table(
        'bundle_component',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('parent_identity_id', sa.BigInteger(), nullable=False,
                  comment="The Bundle/Kit Identity (e.g., '02391-B')."),
        sa.Column('child_identity_id', sa.BigInteger(), nullable=False,
                  comment="The Component Identity (e.g., '00845')."),
        sa.Column('quantity_required', sa.Integer(), nullable=False, server_default='1',
                  comment='How many of this component are needed.'),
        sa.Column('role', bundle_role_enum, nullable=False, server_default='Primary',
                  comment='Context: Primary, Accessory, Satellite.'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.CheckConstraint('parent_identity_id != child_identity_id', name='ck_bundle_no_self_reference'),
        sa.CheckConstraint('quantity_required > 0', name='ck_bundle_positive_quantity'),
        sa.ForeignKeyConstraint(['parent_identity_id'], ['product_identity.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['child_identity_id'], ['product_identity.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('parent_identity_id', 'child_identity_id', name='uq_bundle_parent_child')
    )
    op.create_index('ix_bundle_parent_id', 'bundle_component', ['parent_identity_id'])
    op.create_index('ix_bundle_child_id', 'bundle_component', ['child_identity_id'])

    # ========================================================================
    # PLATFORM_LISTING - External Platform Sync
    # ========================================================================
    op.create_table(
        'platform_listing',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('variant_id', sa.BigInteger(), nullable=False,
                  comment='The specific item being sold.'),
        sa.Column('platform', platform_enum, nullable=False,
                  comment='ZOHO, AMAZON_US, EBAY, etc.'),
        sa.Column('external_ref_id', sa.String(length=100), nullable=True,
                  comment='The ID on the remote platform (Zoho Item ID, ASIN).'),
        sa.Column('listing_price', sa.Numeric(precision=10, scale=2), nullable=True,
                  comment='The specific price for this platform.'),
        sa.Column('sync_status', platform_sync_status_enum, nullable=False, server_default='PENDING',
                  comment='PENDING (needs push), SYNCED (clean), ERROR (retrying).'),
        sa.Column('last_synced_at', sa.DateTime(timezone=True), nullable=True,
                  comment='Last successful sync timestamp.'),
        sa.Column('sync_error_message', sa.Text(), nullable=True,
                  comment='Error message from last failed sync attempt.'),
        sa.Column('platform_metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=True,
                  comment='Platform-specific fields (Amazon Bullet Points, eBay Category ID).'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['variant_id'], ['product_variant.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('variant_id', 'platform', name='uq_listing_variant_platform')
    )
    op.create_index('ix_listing_variant_id', 'platform_listing', ['variant_id'])
    op.create_index('ix_listing_platform', 'platform_listing', ['platform'])
    op.create_index('ix_listing_sync_status', 'platform_listing', ['sync_status'])
    op.create_index('ix_listing_external_ref', 'platform_listing', ['platform', 'external_ref_id'])

    # ========================================================================
    # INVENTORY_ITEM - Physical Inventory Tracking
    # ========================================================================
    op.create_table(
        'inventory_item',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('serial_number', sa.String(length=100), nullable=True,
                  comment='Manufacturer serial (if applicable).'),
        sa.Column('variant_id', sa.BigInteger(), nullable=False,
                  comment='Links to what this item IS.'),
        sa.Column('status', inventory_status_enum, nullable=False, server_default='AVAILABLE',
                  comment='AVAILABLE, SOLD, RESERVED, RMA, DAMAGED.'),
        sa.Column('location_code', sa.String(length=50), nullable=True,
                  comment="Warehouse location (e.g., 'A1-S2')."),
        sa.Column('cost_basis', sa.Numeric(precision=10, scale=2), nullable=True,
                  comment='Exact acquisition cost (for accounting/COGS).'),
        sa.Column('notes', sa.Text(), nullable=True,
                  comment='Additional notes about this specific item.'),
        sa.Column('received_at', sa.DateTime(timezone=True), nullable=True,
                  comment='When this item was received into inventory.'),
        sa.Column('sold_at', sa.DateTime(timezone=True), nullable=True,
                  comment='When this item was sold (if applicable).'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.CheckConstraint('cost_basis IS NULL OR cost_basis >= 0', name='ck_inventory_positive_cost'),
        sa.ForeignKeyConstraint(['variant_id'], ['product_variant.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('serial_number')
    )
    op.create_index('ix_inventory_variant_id', 'inventory_item', ['variant_id'])
    op.create_index('ix_inventory_status', 'inventory_item', ['status'])
    op.create_index('ix_inventory_location', 'inventory_item', ['location_code'])
    op.create_index('ix_inventory_variant_status', 'inventory_item', ['variant_id', 'status'])

    # ========================================================================
    # TRIGGER: Auto-update updated_at timestamp
    # ========================================================================
    op.execute("""
        CREATE OR REPLACE FUNCTION update_updated_at_column()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.updated_at = CURRENT_TIMESTAMP;
            RETURN NEW;
        END;
        $$ language 'plpgsql';
    """)

    # Apply trigger to all tables with updated_at
    for table in ['product_family', 'product_identity', 'product_variant', 
                  'bundle_component', 'platform_listing', 'inventory_item']:
        op.execute(f"""
            CREATE TRIGGER update_{table}_updated_at
            BEFORE UPDATE ON {table}
            FOR EACH ROW
            EXECUTE FUNCTION update_updated_at_column();
        """)


def downgrade() -> None:
    # Drop triggers first
    for table in ['product_family', 'product_identity', 'product_variant', 
                  'bundle_component', 'platform_listing', 'inventory_item']:
        op.execute(f"DROP TRIGGER IF EXISTS update_{table}_updated_at ON {table}")
    
    op.execute("DROP FUNCTION IF EXISTS update_updated_at_column()")

    # Drop tables in reverse order (respecting foreign key constraints)
    op.drop_table('inventory_item')
    op.drop_table('platform_listing')
    op.drop_table('bundle_component')
    op.drop_table('product_variant')
    op.drop_table('product_identity')
    op.drop_table('product_family')

    # Drop enum types
    op.execute("DROP TYPE IF EXISTS platform_enum")
    op.execute("DROP TYPE IF EXISTS bundle_role_enum")
    op.execute("DROP TYPE IF EXISTS inventory_status_enum")
    op.execute("DROP TYPE IF EXISTS platform_sync_status_enum")
    op.execute("DROP TYPE IF EXISTS zoho_sync_status_enum")
    op.execute("DROP TYPE IF EXISTS condition_code_enum")
    op.execute("DROP TYPE IF EXISTS physical_class_enum")
    op.execute("DROP TYPE IF EXISTS identity_type_enum")
