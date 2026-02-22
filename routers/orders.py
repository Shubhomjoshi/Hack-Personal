"""
Order Info Router - API endpoints for order information
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from database import get_db
from models import OrderInfo
from schemas import OrderInfoResponse, OrderInfoList, OrderInfoCreate, MessageResponse
from auth import get_current_user

router = APIRouter(
    prefix="/api/orders",
    tags=["Orders"]
)


@router.get("/", response_model=OrderInfoList)
def get_all_orders(
    skip: int = 0,
    limit: int = 100,
    active_only: bool = True,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Get all order numbers with customer and bill-to codes

    Args:
        skip: Number of records to skip (pagination)
        limit: Maximum number of records to return
        active_only: If True, return only active orders

    Returns:
        List of order information with total count
    """
    query = db.query(OrderInfo)

    if active_only:
        query = query.filter(OrderInfo.is_active == True)

    total = query.count()
    orders = query.offset(skip).limit(limit).all()

    return OrderInfoList(
        total=total,
        orders=orders
    )


@router.get("/{order_number}", response_model=OrderInfoResponse)
def get_order_by_number(
    order_number: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Get order information by order number

    Args:
        order_number: The order number to search for

    Returns:
        Order information details
    """
    order = db.query(OrderInfo).filter(OrderInfo.order_number == order_number).first()

    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Order number '{order_number}' not found"
        )

    return order


@router.post("/", response_model=OrderInfoResponse, status_code=status.HTTP_201_CREATED)
def create_order(
    order_data: OrderInfoCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Create a new order entry

    Args:
        order_data: Order information to create

    Returns:
        Created order information
    """
    # Check if order number already exists
    existing_order = db.query(OrderInfo).filter(
        OrderInfo.order_number == order_data.order_number
    ).first()

    if existing_order:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Order number '{order_data.order_number}' already exists"
        )

    # Create new order
    new_order = OrderInfo(
        order_number=order_data.order_number,
        customer_code=order_data.customer_code,
        bill_to_code=order_data.bill_to_code,
        driver_id=order_data.driver_id
    )

    db.add(new_order)
    db.commit()
    db.refresh(new_order)

    return new_order


@router.delete("/{order_id}", response_model=MessageResponse)
def delete_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Delete an order (soft delete - sets is_active to False)

    Args:
        order_id: Order ID to delete

    Returns:
        Success message
    """
    order = db.query(OrderInfo).filter(OrderInfo.id == order_id).first()

    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Order with ID {order_id} not found"
        )

    # Soft delete
    order.is_active = False
    db.commit()

    return MessageResponse(
        message=f"Order '{order.order_number}' deleted successfully",
        success=True
    )

