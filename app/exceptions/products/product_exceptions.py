"""Product domain exceptions."""

from app.exceptions.base import NotFoundException


class ProductNotFoundException(NotFoundException):
    """Product not found exception."""
    
    def __init__(self, product_id: int):
        super().__init__(f"Product with ID {product_id} not found")
        self.product_id = product_id


class InvalidProductPriceException(Exception):
    """Invalid product price exception."""
    
    def __init__(self, price: float):
        super().__init__(f"Invalid price: {price}. Price must be greater than 0")
        self.price = price


class InvalidProductTypeException(Exception):
    """Invalid product type exception."""
    
    def __init__(self, product_type: str):
        super().__init__(f"Invalid product type: {product_type}. Must be HW or SW")
        self.product_type = product_type
