"""Product repository for database operations."""

from typing import List, Optional
from datetime import datetime
from app.infrastructure.database.connection import Database
from app.models.products import Product
from app.exceptions.products import ProductNotFoundException

# Fallback in-memory products
FALLBACK_PRODUCTS = [
    Product(
        id=1,
        name="Dell PowerEdge R740",
        description="Enterprise server with dual processors",
        category="Servers",
        unit="Server",
        business_unit="Infrastructure",
        location="US",
        price=5999.99,
        product_type="HW",
        is_available=True,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    ),
    Product(
        id=2,
        name="Microsoft Windows Server 2022",
        description="Enterprise operating system license",
        category="Operating Systems",
        unit="License",
        business_unit="Software",
        location="Global",
        price=999.99,
        product_type="SW",
        is_available=True,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    ),
    Product(
        id=3,
        name="Cisco Catalyst 9300",
        description="48-port network switch",
        category="Networking",
        unit="Switch",
        business_unit="Infrastructure",
        location="EU",
        price=8500.00,
        product_type="HW",
        is_available=True,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    ),
    Product(
        id=4,
        name="VMware vSphere Enterprise",
        description="Virtualization platform license",
        category="Virtualization",
        unit="License",
        business_unit="Software",
        location="Global",
        price=4500.00,
        product_type="SW",
        is_available=True,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    ),
    Product(
        id=5,
        name="HP ProLiant DL380 Gen10",
        description="Rack server with redundant power supply",
        category="Servers",
        unit="Server",
        business_unit="Infrastructure",
        location="APAC",
        price=6500.00,
        product_type="HW",
        is_available=True,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
]


class ProductRepository:
    """Repository for product data access."""
    
    def __init__(self, db: Database):
        self.db = db
    
    async def get_all(
        self,
        product_type: Optional[str] = None,
        business_unit: Optional[str] = None,
        location: Optional[str] = None,
        category: Optional[str] = None,
        sort_by: str = "id",
        page: int = 1,
        page_size: int = 50
    ) -> tuple[List[Product], int]:
        """Get all products with filters and pagination."""
        conditions = ["1=1"]
        params = []
        param_count = 1
        
        if product_type:
            conditions.append(f"product_type = ${param_count}")
            params.append(product_type)
            param_count += 1
        
        if business_unit:
            conditions.append(f"business_unit = ${param_count}")
            params.append(business_unit)
            param_count += 1
        
        if location:
            conditions.append(f"location = ${param_count}")
            params.append(location)
            param_count += 1
        
        if category:
            conditions.append(f"category = ${param_count}")
            params.append(category)
            param_count += 1
        
        where_clause = " AND ".join(conditions)
        
        count_query = f"SELECT COUNT(*) FROM products WHERE {where_clause}"
        total = await self.db.fetch_one(count_query, *params)
        
        # Fallback to in-memory data if DB unavailable
        if total is None:
            filtered = FALLBACK_PRODUCTS
            if product_type:
                filtered = [p for p in filtered if p.product_type == product_type]
            if business_unit:
                filtered = [p for p in filtered if p.business_unit == business_unit]
            if location:
                filtered = [p for p in filtered if p.location == location]
            if category:
                filtered = [p for p in filtered if p.category == category]
            return filtered, len(filtered)
        
        offset = (page - 1) * page_size
        query = f"""
            SELECT * FROM products 
            WHERE {where_clause}
            ORDER BY {sort_by}
            LIMIT ${param_count} OFFSET ${param_count + 1}
        """
        params.extend([page_size, offset])
        
        rows = await self.db.fetch_all(query, *params)
        products = [Product(**{k: v for k, v in row.items()}) for row in rows]
        
        return products, total['count']
    
    async def get_by_id(self, product_id: int) -> Product:
        """Get product by ID."""
        query = "SELECT * FROM products WHERE id = $1"
        row = await self.db.fetch_one(query, product_id)
        
        if not row:
            raise ProductNotFoundException(product_id)
        
        return Product(**{k: v for k, v in row.items()})
    
    async def create(self, product: Product) -> Product:
        """Create a new product."""
        query = """
            INSERT INTO products (name, description, category, unit, business_unit, 
                                location, price, product_type, is_available)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
            RETURNING *
        """
        row = await self.db.fetch_one(
            query,
            product.name,
            product.description,
            product.category,
            product.unit,
            product.business_unit,
            product.location,
            product.price,
            product.product_type,
            product.is_available
        )
        return Product(**{k: v for k, v in row.items()})
    
    async def update_price(self, product_id: int, price: float) -> Product:
        """Update product price."""
        query = """
            UPDATE products 
            SET price = $1, updated_at = NOW()
            WHERE id = $2
            RETURNING *
        """
        row = await self.db.fetch_one(query, price, product_id)
        
        if not row:
            raise ProductNotFoundException(product_id)
        
        return Product(**{k: v for k, v in row.items()})
    
    async def update_availability(self, product_id: int, is_available: bool) -> Product:
        """Update product availability."""
        query = """
            UPDATE products 
            SET is_available = $1, updated_at = NOW()
            WHERE id = $2
            RETURNING *
        """
        row = await self.db.fetch_one(query, is_available, product_id)
        
        if not row:
            raise ProductNotFoundException(product_id)
        
        return Product(**{k: v for k, v in row.items()})
    
    async def delete(self, product_id: int) -> None:
        """Delete a product."""
        query = "DELETE FROM products WHERE id = $1 RETURNING id"
        row = await self.db.fetch_one(query, product_id)
        
        if not row:
            raise ProductNotFoundException(product_id)
    
    async def add_category(self, category: str) -> dict:
        """Add a new category."""
        query = "INSERT INTO categories (name) VALUES ($1) RETURNING *"
        row = await self.db.fetch_one(query, category)
        return dict(row)
    
    async def add_unit(self, unit: str) -> dict:
        """Add a new unit."""
        query = "INSERT INTO units (name) VALUES ($1) RETURNING *"
        row = await self.db.fetch_one(query, unit)
        return dict(row)
