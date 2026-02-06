"""Unit tests for product service."""

import pytest
from unittest.mock import AsyncMock
from app.models.products import Product
from app.exceptions.products import InvalidProductPriceException, InvalidProductTypeException


@pytest.mark.unit
class TestProductService:
    """Test product service business logic."""
    
    @pytest.mark.asyncio
    async def test_create_product_success(self, product_service, sample_product, mock_cache):
        """Test successful product creation."""
        product_service.repository.create = AsyncMock(return_value=sample_product)
        
        result = await product_service.create_product(sample_product, "admin123")
        
        assert result.id == 1
        assert result.name == "Test Product"
        product_service.repository.create.assert_called_once()
        mock_cache.clear_pattern.assert_called_once_with("products:")
    
    @pytest.mark.asyncio
    async def test_create_product_invalid_price(self, product_service, sample_product):
        """Test product creation with invalid price."""
        sample_product.price = -10
        
        with pytest.raises(InvalidProductPriceException):
            await product_service.create_product(sample_product, "admin123")
    
    @pytest.mark.asyncio
    async def test_create_product_invalid_type(self, product_service, sample_product):
        """Test product creation with invalid type."""
        sample_product.product_type = "INVALID"
        
        with pytest.raises(InvalidProductTypeException):
            await product_service.create_product(sample_product, "admin123")
    
    @pytest.mark.asyncio
    async def test_get_product_by_id_from_cache(self, product_service, sample_product, mock_cache):
        """Test getting product from cache."""
        mock_cache.get = AsyncMock(return_value=sample_product.model_dump())
        
        result = await product_service.get_product_by_id(1)
        
        assert result.id == 1
        assert result.name == "Test Product"
        mock_cache.get.assert_called_once_with("product:1")
    
    @pytest.mark.asyncio
    async def test_get_product_by_id_from_db(self, product_service, sample_product, mock_cache):
        """Test getting product from database when not in cache."""
        mock_cache.get = AsyncMock(return_value=None)
        product_service.repository.get_by_id = AsyncMock(return_value=sample_product)
        
        result = await product_service.get_product_by_id(1)
        
        assert result.id == 1
        product_service.repository.get_by_id.assert_called_once_with(1)
        mock_cache.set.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_update_price_success(self, product_service, sample_product, mock_cache):
        """Test successful price update."""
        product_service.repository.get_by_id = AsyncMock(return_value=sample_product)
        updated_product = Product(**sample_product.model_dump())
        updated_product.price = 149.99
        product_service.repository.update_price = AsyncMock(return_value=updated_product)
        
        result = await product_service.update_price(1, 149.99, "admin123")
        
        assert result.price == 149.99
        mock_cache.delete.assert_called_once_with("product:1")
        mock_cache.clear_pattern.assert_called_once_with("products:")
    
    @pytest.mark.asyncio
    async def test_update_price_invalid(self, product_service):
        """Test price update with invalid price."""
        with pytest.raises(InvalidProductPriceException):
            await product_service.update_price(1, -50, "admin123")
    
    @pytest.mark.asyncio
    async def test_delete_product_success(self, product_service, sample_product, mock_cache):
        """Test successful product deletion."""
        product_service.repository.get_by_id = AsyncMock(return_value=sample_product)
        product_service.repository.delete = AsyncMock()
        
        await product_service.delete_product(1, "admin123")
        
        product_service.repository.delete.assert_called_once_with(1)
        mock_cache.delete.assert_called_once_with("product:1")
        mock_cache.clear_pattern.assert_called_once_with("products:")
    
    @pytest.mark.asyncio
    async def test_update_availability(self, product_service, sample_product, mock_cache):
        """Test updating product availability."""
        updated_product = Product(**sample_product.model_dump())
        updated_product.is_available = False
        product_service.repository.update_availability = AsyncMock(return_value=updated_product)
        
        result = await product_service.update_availability(1, False, "admin123")
        
        assert result.is_available is False
        mock_cache.delete.assert_called_once_with("product:1")
