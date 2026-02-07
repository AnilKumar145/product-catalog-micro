"""Unit tests for product repository."""

import pytest
from unittest.mock import AsyncMock
from app.exceptions.products import ProductNotFoundException


@pytest.mark.unit
class TestProductRepository:
    """Test product repository data access."""
    
    @pytest.mark.asyncio
    async def test_get_by_id_success(self, product_repository, mock_db, sample_product):
        """Test getting product by ID."""
        mock_db.fetch_one = AsyncMock(return_value={
            "id": 1,
            "name": "Test Product",
            "description": "Test Description",
            "category": "Hardware",
            "unit": "Unit",
            "business_unit": "IT",
            "location": "US",
            "price": 99.99,
            "product_type": "HW",
            "is_available": True,
            "created_at": None,
            "updated_at": None
        })
        
        result = await product_repository.get_by_id(1)
        
        assert result.id == 1
        assert result.name == "Test Product"
        mock_db.fetch_one.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_by_id_not_found(self, product_repository, mock_db):
        """Test getting non-existent product."""
        mock_db.fetch_one = AsyncMock(return_value=None)
        
        with pytest.raises(ProductNotFoundException):
            await product_repository.get_by_id(999)
    
    @pytest.mark.asyncio
    async def test_create_product(self, product_repository, mock_db, sample_product):
        """Test creating a product."""
        mock_db.fetch_one = AsyncMock(return_value={
            "id": 1,
            "name": sample_product.name,
            "description": sample_product.description,
            "category": sample_product.category,
            "unit": sample_product.unit,
            "business_unit": sample_product.business_unit,
            "location": sample_product.location,
            "price": sample_product.price,
            "product_type": sample_product.product_type,
            "is_available": sample_product.is_available,
            "created_at": None,
            "updated_at": None
        })
        
        result = await product_repository.create(sample_product)
        
        assert result.name == "Test Product"
        mock_db.fetch_one.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_update_price(self, product_repository, mock_db):
        """Test updating product price."""
        mock_db.fetch_one = AsyncMock(return_value={
            "id": 1,
            "name": "Test Product",
            "price": 149.99,
            "description": "Test",
            "category": "Hardware",
            "unit": "Unit",
            "business_unit": "IT",
            "location": "US",
            "product_type": "HW",
            "is_available": True,
            "created_at": None,
            "updated_at": None
        })
        
        result = await product_repository.update_price(1, 149.99)
        
        assert result.price == 149.99
        mock_db.fetch_one.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_delete_product(self, product_repository, mock_db):
        """Test deleting a product."""
        mock_db.fetch_one = AsyncMock(return_value={"id": 1})
        
        await product_repository.delete(1)
        
        mock_db.fetch_one.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_delete_product_not_found(self, product_repository, mock_db):
        """Test deleting non-existent product."""
        mock_db.fetch_one = AsyncMock(return_value=None)
        
        with pytest.raises(ProductNotFoundException):
            await product_repository.delete(999)
