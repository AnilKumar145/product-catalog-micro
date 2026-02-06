-- Database initialization script for Catalog Service

-- Create products table
CREATE TABLE IF NOT EXISTS products (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    category VARCHAR(100) NOT NULL,
    unit VARCHAR(50) NOT NULL,
    business_unit VARCHAR(100) NOT NULL,
    location VARCHAR(100) NOT NULL,
    price DECIMAL(10, 2) NOT NULL CHECK (price > 0),
    product_type VARCHAR(2) NOT NULL CHECK (product_type IN ('HW', 'SW')),
    is_available BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Create categories table
CREATE TABLE IF NOT EXISTS categories (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Create units table
CREATE TABLE IF NOT EXISTS units (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_products_type ON products(product_type);
CREATE INDEX IF NOT EXISTS idx_products_business_unit ON products(business_unit);
CREATE INDEX IF NOT EXISTS idx_products_location ON products(location);
CREATE INDEX IF NOT EXISTS idx_products_category ON products(category);
CREATE INDEX IF NOT EXISTS idx_products_available ON products(is_available);

-- Insert sample categories
INSERT INTO categories (name) VALUES 
    ('Servers'),
    ('Storage'),
    ('Networking'),
    ('Software Licenses'),
    ('Cloud Services')
ON CONFLICT (name) DO NOTHING;

-- Insert sample units
INSERT INTO units (name) VALUES 
    ('Unit'),
    ('License'),
    ('Subscription'),
    ('Device'),
    ('Server')
ON CONFLICT (name) DO NOTHING;

-- Insert sample products
INSERT INTO products (name, description, category, unit, business_unit, location, price, product_type, is_available) VALUES
    ('Dell PowerEdge R740', 'Enterprise server with dual processors', 'Servers', 'Server', 'Infrastructure', 'US', 5999.99, 'HW', true),
    ('Cisco Catalyst 9300', '48-port network switch', 'Networking', 'Device', 'Networking', 'EU', 8500.00, 'HW', true),
    ('Microsoft SQL Server License', 'Enterprise database license', 'Software Licenses', 'License', 'Software', 'US', 14999.00, 'SW', true),
    ('VMware vSphere Standard', 'Virtualization platform', 'Software Licenses', 'License', 'Infrastructure', 'APAC', 995.00, 'SW', true),
    ('NetApp FAS2750', 'Hybrid storage system', 'Storage', 'Unit', 'Storage', 'US', 25000.00, 'HW', true)
ON CONFLICT DO NOTHING;
