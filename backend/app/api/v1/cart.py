"""Cart routes."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.v1.deps import get_current_user
from app.core.database import get_db
from app.models import Cart, CartItem, CartStatus, Product, User
from app.schemas.schemas import (
    AddToCartRequest,
    CartItemResponse,
    CartResponse,
    ProductResponse,
    UpdateCartItemRequest,
)
from app.services.cart_service import CartService

router = APIRouter()


def _build_cart_response(cart: Cart) -> CartResponse:
    items = []
    for item in cart.items or []:
        if not item.product:
            continue
        p = item.product
        price = float(p.price)
        orig = float(p.original_price) if p.original_price else None
        discount = round((1 - price / orig) * 100, 1) if orig and orig > price else None
        prod_resp = ProductResponse(
            id=p.id, name=p.name, description=p.description, category=p.category,
            sub_category=p.sub_category, price=price, original_price=orig,
            discount_percent=discount, stock=p.stock, rating=p.rating,
            review_count=p.review_count, brand=p.brand, tags=p.tags or [],
            features=p.features or [], specifications=p.specifications or {},
            cross_sell_ids=p.cross_sell_ids or [], upsell_ids=p.upsell_ids or [],
            image_url=p.image_url, is_active=p.is_active,
            created_at=p.created_at, updated_at=p.updated_at,
        )
        items.append(CartItemResponse(
            id=item.id, product_id=item.product_id, product=prod_resp,
            quantity=item.quantity, unit_price=float(item.unit_price),
            total_price=float(item.total_price),
        ))
    return CartResponse(
        id=cart.id, status=cart.status.value, items=items,
        subtotal=float(cart.subtotal), discount=float(cart.discount),
        total=float(cart.total), item_count=len(items),
        created_at=cart.created_at, updated_at=cart.updated_at,
    )


@router.get("", response_model=CartResponse)
async def get_cart(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> CartResponse:
    svc = CartService(db)
    cart = await svc.get_or_create_cart(current_user.id)
    return _build_cart_response(cart)


@router.post("/items", response_model=CartResponse, status_code=status.HTTP_201_CREATED)
async def add_item(
    data: AddToCartRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> CartResponse:
    try:
        svc = CartService(db)
        cart = await svc.add_item(current_user.id, data.product_id, data.quantity)
        return _build_cart_response(cart)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e


@router.put("/items/{item_id}", response_model=CartResponse)
async def update_item(
    item_id: str,
    data: UpdateCartItemRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> CartResponse:
    svc = CartService(db)
    cart = await svc.get_or_create_cart(current_user.id)
    try:
        updated = await svc.update_quantity(cart.id, item_id, data.quantity)
        return _build_cart_response(updated)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.delete("/items/{item_id}", response_model=CartResponse)
async def remove_item(
    item_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> CartResponse:
    svc = CartService(db)
    cart = await svc.get_or_create_cart(current_user.id)
    updated = await svc.remove_item(cart.id, item_id)
    return _build_cart_response(updated)
