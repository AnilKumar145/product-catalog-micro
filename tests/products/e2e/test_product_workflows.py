"""End-to-end tests for product workflows."""

import pytest
from unittest.mock import patch, AsyncMock


@pytest.mark.e2e
@pytest.mark.slow
class TestProductWorkflows:
    """Test complete product workflows."""
    
    def test_complete_product_lifecycle(self, client, sample_product_data, sample_product):
        """Test complete product lifecycle: create, read, update, delete."""
        with patch('app.dependencies.get_current_user') as mock_auth:
            with patch('app.api.v1.products.product_endpoints.get_product_service') as mock_service:
                mock_auth.return_value = {"user_id": "admin123", "role": "admin"}
                service = mock_service.return_value
                
                # Create product
                service.create_product = AsyncMock(return_value=sample_product)
                create_response = client.post(
                    "/api/v1/products",
                    json=sample_product_data,
                    headers={"Authorization": "Bearer fake-token"}
                )
                assert create_response.status_code == 201
                product_id = create_response.json()["id"]
                
                # Read product
                service.get_product_by_id = AsyncMock(return_value=sample_product)
                read_response = client.get(f"/api/v1/products/{product_id}")
                assert read_response.status_code == 200
                assert read_response.json()["name"] == "Test Product"
                
                # Update price
                updated_product = sample_product.model_copy()
                updated_product.price = 149.99
                service.update_price = AsyncMock(return_value=updated_product)
                update_response = client.patch(
                    f"/api/v1/products/{product_id}/price",
                    json={"price": 149.99},
                    headers={"Authorization": "Bearer fake-token"}
                )
                assert update_response.status_code == 200
                assert update_response.json()["price"] == 149.99
                
                # Delete product
                service.delete_product = AsyncMock()
                delete_response = client.delete(
                    f"/api/v1/products/{product_id}",
                    headers={"Authorization": "Bearer fake-token"}
                )
                assert delete_response.status_code == 200
    
    def test_product_search_and_filter_workflow(self, client, sample_product):
        """Test searching and filtering products."""
        with patch('app.api.v1.products.product_endpoints.get_product_service') as mock_service:
            service = mock_service.return_value
            
            # Search all products
            service.get_all_products = AsyncMock(return_value=([sample_product], 1))
            response = client.get("/api/v1/products")
            assert response.status_code == 200
            assert response.json()["total"] == 1
            
            # Filter by type
            service.get_all_products = AsyncMock(return_value=([sample_product], 1))
            response = client.get("/api/v1/products?product_type=HW")
            assert response.status_code == 200
            
            # Filter by location
            service.get_all_products = AsyncMock(return_value=([sample_product], 1))
            response = client.get("/api/v1/products?location=US")
            assert response.status_code == 200
            
            # Pagination
            service.get_all_products = AsyncMock(return_value=([sample_product], 1))
            response = client.get("/api/v1/products?page=1&page_size=10")
            assert response.status_code == 200
            assert response.json()["page"] == 1
    
    def test_category_and_unit_management(self, client):
        """Test adding categories and units."""
        with patch('app.dependencies.get_current_user') as mock_auth:
            with patch('app.api.v1.products.product_endpoints.get_product_service') as mock_service:
                mock_auth.return_value = {"user_id": "admin123", "role": "admin"}
                service = mock_service.return_value
                
                # Add category
                service.add_category = AsyncMock(return_value={"id": 1, "name": "Electronics"})
                response = client.post(
                    "/api/v1/products/categories?category=Electronics",
                    headers={"Authorization": "Bearer fake-token"}
                )
                assert response.status_code == 201
                assert "Electronics" in response.json()["message"]
                
                # Add unit
                service.add_unit = AsyncMock(return_value={"id": 1, "name": "Box"})
                response = client.post(
                    "/api/v1/products/units?unit=Box",
                    headers={"Authorization": "Bearer fake-token"}
                )
                assert response.status_code == 201
                assert "Box" in response.json()["message"]
