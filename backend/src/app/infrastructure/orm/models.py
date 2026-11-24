from datetime import datetime
from decimal import Decimal
from typing import Any
from uuid import UUID, uuid4

from sqlalchemy import (
    JSON,
    Boolean,
    CheckConstraint,
    Column,
    DateTime,
    ForeignKey,
    Numeric,
    String,
    Table,
    Text,
    UniqueConstraint,
    Uuid,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


user_roles = Table(
    "user_roles",
    Base.metadata,
    Column(
        "user_id",
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "role_id",
        Uuid(as_uuid=True),
        ForeignKey("roles.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)

role_permissions = Table(
    "role_permissions",
    Base.metadata,
    Column(
        "role_id",
        Uuid(as_uuid=True),
        ForeignKey("roles.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "permission_id",
        Uuid(as_uuid=True),
        ForeignKey("permissions.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)


class UserModel(Base):
    __tablename__ = "users"
    __table_args__ = (CheckConstraint("email = lower(email)", name="ck_users_email_lower"),)

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    email: Mapped[str] = mapped_column(String(320), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(120))
    password_hash: Mapped[str] = mapped_column(String(512))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    roles: Mapped[list["RoleModel"]] = relationship(
        secondary=user_roles,
        back_populates="users",
        lazy="selectin",
        order_by="RoleModel.name",
    )
    organizations: Mapped[list["OrganizationModel"]] = relationship(
        back_populates="owner",
        passive_deletes=True,
    )
    refresh_tokens: Mapped[list["RefreshTokenModel"]] = relationship(
        back_populates="user",
        passive_deletes=True,
    )
    recommendation_filters: Mapped[list["RecommendationFilterModel"]] = relationship(
        back_populates="user",
        passive_deletes=True,
    )


class RoleModel(Base):
    __tablename__ = "roles"
    __table_args__ = (CheckConstraint("name = lower(name)", name="ck_roles_name_lower"),)

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    description: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    users: Mapped[list[UserModel]] = relationship(
        secondary=user_roles,
        back_populates="roles",
    )
    permissions: Mapped[list["PermissionModel"]] = relationship(
        secondary=role_permissions,
        back_populates="roles",
        lazy="selectin",
        order_by="PermissionModel.code",
    )


class PermissionModel(Base):
    __tablename__ = "permissions"
    __table_args__ = (CheckConstraint("code = lower(code)", name="ck_permissions_code_lower"),)

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    code: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(150))
    description: Mapped[str | None] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    roles: Mapped[list[RoleModel]] = relationship(
        secondary=role_permissions,
        back_populates="permissions",
    )


class OrganizationTypeModel(Base):
    __tablename__ = "organization_types"

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    code: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(120))
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    organizations: Mapped[list["OrganizationModel"]] = relationship(back_populates="type")


class OrganizationModel(Base):
    __tablename__ = "organizations"
    __table_args__ = (
        CheckConstraint(
            "latitude IS NULL OR latitude BETWEEN -90 AND 90",
            name="ck_organizations_latitude",
        ),
        CheckConstraint(
            "longitude IS NULL OR longitude BETWEEN -180 AND 180",
            name="ck_organizations_longitude",
        ),
    )

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    type_id: Mapped[UUID] = mapped_column(
        ForeignKey("organization_types.id", ondelete="RESTRICT"),
        index=True,
    )
    owner_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"),
        index=True,
    )
    name: Mapped[str] = mapped_column(String(180), index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    address: Mapped[str | None] = mapped_column(String(255), nullable=True)
    city: Mapped[str | None] = mapped_column(String(120), nullable=True, index=True)
    latitude: Mapped[Decimal | None] = mapped_column(Numeric(9, 6), nullable=True)
    longitude: Mapped[Decimal | None] = mapped_column(Numeric(9, 6), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    type: Mapped[OrganizationTypeModel] = relationship(back_populates="organizations")
    owner: Mapped[UserModel] = relationship(back_populates="organizations")
    catalogs: Mapped[list["CatalogModel"]] = relationship(back_populates="organization")


class CatalogModel(Base):
    __tablename__ = "catalogs"
    __table_args__ = (
        UniqueConstraint("organization_id", "name", name="uq_catalogs_organization_name"),
    )

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    organization_id: Mapped[UUID] = mapped_column(
        ForeignKey("organizations.id", ondelete="CASCADE"),
        index=True,
    )
    name: Mapped[str] = mapped_column(String(180))
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    organization: Mapped[OrganizationModel] = relationship(back_populates="catalogs")
    categories: Mapped[list["ItemCategoryModel"]] = relationship(
        back_populates="catalog",
        passive_deletes=True,
    )
    items: Mapped[list["CatalogItemModel"]] = relationship(
        back_populates="catalog",
        passive_deletes=True,
    )


class ItemCategoryModel(Base):
    __tablename__ = "item_categories"
    __table_args__ = (
        UniqueConstraint("catalog_id", "name", name="uq_item_categories_catalog_name"),
    )

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    catalog_id: Mapped[UUID] = mapped_column(
        ForeignKey("catalogs.id", ondelete="CASCADE"),
        index=True,
    )
    name: Mapped[str] = mapped_column(String(120))
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    catalog: Mapped[CatalogModel] = relationship(back_populates="categories")
    items: Mapped[list["CatalogItemModel"]] = relationship(back_populates="category")


class CatalogItemModel(Base):
    __tablename__ = "catalog_items"
    __table_args__ = (
        CheckConstraint("price >= 0", name="ck_catalog_items_price_nonnegative"),
        CheckConstraint("currency = upper(currency)", name="ck_catalog_items_currency_upper"),
        CheckConstraint(
            "price_unit IN ('item', 'person', 'ticket', 'hour', 'service')",
            name="ck_catalog_items_price_unit",
        ),
    )

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    catalog_id: Mapped[UUID] = mapped_column(
        ForeignKey("catalogs.id", ondelete="CASCADE"),
        index=True,
    )
    category_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("item_categories.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    name: Mapped[str] = mapped_column(String(180), index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    price: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    currency: Mapped[str] = mapped_column(String(3), default="RUB")
    price_unit: Mapped[str] = mapped_column(String(20), default="item")
    attributes: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    is_available: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    catalog: Mapped[CatalogModel] = relationship(back_populates="items")
    category: Mapped[ItemCategoryModel | None] = relationship(back_populates="items")


class RefreshTokenModel(Base):
    __tablename__ = "refresh_tokens"

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    token_hash: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    replaced_by_token_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("refresh_tokens.id", ondelete="SET NULL"),
        nullable=True,
    )
    user_agent: Mapped[str | None] = mapped_column(String(255), nullable=True)
    ip_address: Mapped[str | None] = mapped_column(String(64), nullable=True)
    user: Mapped[UserModel] = relationship(back_populates="refresh_tokens")


class RecommendationFilterModel(Base):
    __tablename__ = "recommendation_filters"
    __table_args__ = (
        CheckConstraint("budget IS NULL OR budget >= 0", name="ck_filters_budget_nonnegative"),
        CheckConstraint(
            "party_size IS NULL OR party_size BETWEEN 1 AND 20",
            name="ck_filters_party_size",
        ),
        CheckConstraint("currency = upper(currency)", name="ck_filters_currency_upper"),
    )

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    user_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    client_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), index=True)
    organization_type_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("organization_types.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    budget: Mapped[Decimal | None] = mapped_column(Numeric(12, 2), nullable=True)
    party_size: Mapped[int | None] = mapped_column(nullable=True)
    city: Mapped[str | None] = mapped_column(String(120), nullable=True, index=True)
    wishes: Mapped[str | None] = mapped_column(String(500), nullable=True)
    currency: Mapped[str] = mapped_column(String(3), default="RUB")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    user: Mapped[UserModel | None] = relationship(back_populates="recommendation_filters")
    organization_type: Mapped[OrganizationTypeModel | None] = relationship()
