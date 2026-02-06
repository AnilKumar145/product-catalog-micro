"""Integration tests for product endpoints."""

import pytest
from unittest.mock import patch, AsyncMock


@pytest.mark.integration
class TestProductEndpoints:
    """Test product API endpoints integration."""
    
    def test_get_all_products(self, client):
        """Test getting all products endpoint."""
        with patch('app.api.v1.products.product_endpoints.get_product_service') as mock_service:
            mock_service.return_value.get_all_products = AsyncMock(return_value=([], 0))
            
            response = client.get("/api/v1/products")
            
            assert response.status_code == 200
            assert "items" in response.json()
            assert "total" in response.json()
    
    def test_get_product_by_id(self, client, sample_product):
        """Test getting product by ID endpoint."""
        with patch('app.api.v1.products.product_endpoints.get_product_service') as mock_service:
            mock_service.return_value.get_product_by_id = AsyncMock(return_value=sample_product)
            
            response = client.get("/api/v1/products/1")
            
            assert response.status_code == 200
            assert response.json()["name"] == "Test Product"
    
    def test_create_product_without_auth(self, client, sample_product_data):
        """Test creating product without authentication."""
        response = client.post("/api/v1/products", json=sample_product_data)
        
        assert response.status_code == 401
    
    def test_create_product_with_auth(self, client, sample_product_data, sample_product):
        """Test creating product with authentication."""
        with patch('app.dependencies.get_current_user') as mock_auth:
            with patch('app.api.v1.products.product_endpoints.get_product_service') as mock_service:
                mock_auth.return_value = {"user_id": "admin123", "role": "admin"}
                mock_service.return_value.create_product = AsyncMock(return_value=sample_product)
                
                response = client.post(
                    "/api/v1/products",
                    json=sample_product_data,
                    headers={"Authorization": "Bearer fake-token"}
                )
                
                assert response.status_code == 201
                assert response.json()["name"] == "Test Product"
    
    def test_update_price(self, client, sample_product):
        """Test updating product price."""
        with patch('app.dependencies.get_current_user') as mock_auth:
            with patch('app.api.v1.products.product_endpoints.get_product_service') as mock_service:
                mock_auth.return_value = {"user_id": "admin123", "role": "admin"}
                updated_product = sample_product.model_copy()
                updated_product.price = 149.99
                mock_service.return_value.update_price = AsyncMock(return_value=updated_product)
                
                response = client.patch(
                    "/api/v1/products/1/price",
                    json={"price": 149.99},
                    headers={"Authorization": "Bearer fake-token"}
                )
                
                assert response.status_code == 200
                assert response.json()["price"] == 149.99
    
    def test_delete_product(self, client):
        """Test deleting a product."""
        with patch('app.dependencies.get_current_user') as mock_auth:
            with patch('app.api.v1.products.product_endpoints.get_product_service') as mock_service:
                mock_auth.return_value = {"user_id": "admin123", "role": "admin"}
                mock_service.return_value.delete_product = AsyncMock()
                
                response = client.delete(
                    "/api/v1/products/1",
                    headers={"Authorization": "Bearer fake-token"}
                )
                
                assert response.status_code == 200
                assert "deleted successfully" in response.json()["message"]
    
    def test_get_products_with_filters(self, client):
        """Test getting products with filters."""
        with patch('app.api.v1.products.product_endpoints.get_product_service') as mock_service:
            mock_service.return_value.get_all_products = AsyncMock(return_value=([], 0))
            
            response = client.get(
                "/api/v1/products?product_type=HW&location=US&page=1&page_size=10"
            )
            
            assert response.status_code == 200
            assert response.json()["page"] == 1
            assert response.json()["page_size"] == 10
