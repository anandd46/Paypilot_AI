"""Product routes — CRUD + paginated search."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import and_, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.deps import get_current_user, require_merchant
from app.core.database import get_db
from app.models import AuditLog, Product, User
from app.schemas.schemas import (
    PaginatedResponse,
    ProductCreate,
    ProductResponse,
    ProductUpdate,
)

router = APIRouter()


def _to_response(p: Product) -> ProductResponse:
    price = float(p.price)
    orig = float(p.original_price) if p.original_price else None
    discount = round((1 - price / orig) * 100, 1) if orig and orig > price else None
    return ProductResponse(
        id=p.id,
        name=p.name,
        description=p.description,
        category=p.category,
        sub_category=p.sub_category,
        price=price,
        original_price=orig,
        discount_percent=discount,
        stock=p.stock,
        rating=p.rating,
        review_count=p.review_count,
        brand=p.brand,
        tags=p.tags or [],
        features=p.features or [],
        specifications=p.specifications or {},
        cross_sell_ids=p.cross_sell_ids or [],
        upsell_ids=p.upsell_ids or [],
        image_url=p.image_url,
        is_active=p.is_active,
        created_at=p.created_at,
        updated_at=p.updated_at,
    )


@router.get("", response_model=PaginatedResponse)
async def list_products(
    q: str | None = Query(None),
    category: str | None = None,
    brand: str | None = None,
    min_price: float | None = Query(None, ge=0),
    max_price: float | None = Query(None, ge=0),
    min_rating: float | None = Query(None, ge=0, le=5),
    in_stock: bool | None = None,
    sort_by: str = "rating",
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
) -> PaginatedResponse:
    query = select(Product).where(Product.is_active == True)  # noqa: E712

    if q:
        query = query.where(
            or_(
                Product.name.ilike(f"%{q}%"),
                Product.description.ilike(f"%{q}%"),
                Product.brand.ilike(f"%{q}%"),
            )
        )
    if category:
        query = query.where(Product.category.ilike(f"%{category}%"))
    if brand:
        query = query.where(Product.brand.ilike(f"%{brand}%"))
    if min_price is not None:
        query = query.where(Product.price >= min_price)
    if max_price is not None:
        query = query.where(Product.price <= max_price)
    if min_rating is not None:
        query = query.where(Product.rating >= min_rating)
    if in_stock is not None and in_stock:
        query = query.where(Product.stock > 0)

    # Count
    count_q = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_q)
    total = total_result.scalar_one()

    # Sort
    sort_map = {
        "rating": Product.rating.desc(),
        "price_asc": Product.price.asc(),
        "price_desc": Product.price.desc(),
        "newest": Product.created_at.desc(),
    }
    query = query.order_by(sort_map.get(sort_by, Product.rating.desc()))

    # Paginate
    query = query.offset((page - 1) * limit).limit(limit)
    result = await db.execute(query)
    products = result.scalars().all()

    return PaginatedResponse(
        items=[_to_response(p) for p in products],
        total=total,
        page=page,
        limit=limit,
        pages=-(-total // limit),
    )


@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(product_id: str, db: AsyncSession = Depends(get_db)) -> ProductResponse:
    result = await db.execute(select(Product).where(Product.id == product_id))
    product = result.scalar_one_or_none()
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    return _to_response(product)


@router.post("", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
async def create_product(
    data: ProductCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_merchant),
) -> ProductResponse:
    product = Product(**data.model_dump())
    db.add(product)
    db.add(AuditLog(user_id=current_user.id, action="product_created", entity_type="product"))
    await db.commit()
    await db.refresh(product)
    return _to_response(product)


@router.put("/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: str,
    data: ProductUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_merchant),
) -> ProductResponse:
    result = await db.execute(select(Product).where(Product.id == product_id))
    product = result.scalar_one_or_none()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    for field, value in data.model_dump(exclude_none=True).items():
        setattr(product, field, value)

    db.add(AuditLog(user_id=current_user.id, action="product_updated", entity_type="product", entity_id=product_id))
    await db.commit()
    await db.refresh(product)
    return _to_response(product)


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(
    product_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_merchant),
) -> None:
    result = await db.execute(select(Product).where(Product.id == product_id))
    product = result.scalar_one_or_none()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    product.is_active = False  # Soft delete
    db.add(AuditLog(user_id=current_user.id, action="product_deactivated", entity_type="product", entity_id=product_id))
    await db.commit()
