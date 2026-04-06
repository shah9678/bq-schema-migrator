"""
SQLModel definitions — the desired schema state.

These models represent what the BigQuery tables SHOULD look like.
Compare them against data/bigquery_schema.json to find the drift.
"""

from typing import Optional
from datetime import datetime, timezone
from uuid import uuid4

from sqlmodel import SQLModel, Field


class BaseModel(SQLModel):
    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    modified_at: Optional[datetime] = Field(default=None)
    deleted_at: Optional[datetime] = Field(default=None)


class Customer(BaseModel, table=True):
    __tablename__ = "customers"

    name: str
    email: str
    tier: str = Field(default="free")  # free, pro, enterprise
    is_active: bool = Field(default=True)
    company_name: Optional[str] = Field(default=None)
    annual_revenue: Optional[float] = Field(default=None)
    notes: Optional[str] = Field(default=None)


class Product(BaseModel, table=True):
    __tablename__ = "products"

    name: str
    sku: str
    category: str
    unit_price: float
    cost_price: Optional[float] = Field(default=None)
    is_active: bool = Field(default=True)
    weight_kg: Optional[float] = Field(default=None)
    description: Optional[str] = Field(default=None)


class Order(BaseModel, table=True):
    __tablename__ = "orders"

    customer_id: str = Field(foreign_key="customers.id")
    order_date: datetime
    status: str = Field(default="pending")  # pending, confirmed, shipped, delivered, cancelled
    total_amount: float
    currency: str = Field(default="USD")
    shipping_address: Optional[str] = Field(default=None)
    tracking_number: Optional[str] = Field(default=None)
    fulfilled_at: Optional[datetime] = Field(default=None)


class OrderItem(BaseModel, table=True):
    __tablename__ = "order_items"

    order_id: str = Field(foreign_key="orders.id")
    product_id: str = Field(foreign_key="products.id")
    quantity: int
    unit_price: float
    discount_pct: Optional[float] = Field(default=None)
    line_total: float


class InventorySnapshot(BaseModel, table=True):
    __tablename__ = "inventory_snapshots"

    product_id: str = Field(foreign_key="products.id")
    warehouse_id: str
    snapshot_date: datetime
    quantity_on_hand: int
    quantity_reserved: int = Field(default=0)
    quantity_available: int
    reorder_point: Optional[int] = Field(default=None)
