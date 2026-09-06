PRAGMA foreign_keys = ON;

-- Menu categories
INSERT INTO menu_categories (name, sort_order)
VALUES
    ('Starters', 1),
    ('Main Course', 2),
    ('Desserts', 3),
    ('Beverages', 4);

-- Menu items
INSERT INTO menu_items
    (category_id, name, description, price_cents, available)
VALUES
    (1, 'Paneer Tikka', 'Grilled cottage cheese with spices', 25000, 1),
    (1, 'Veg Spring Rolls', 'Crispy vegetable spring rolls', 18000, 1),
    (2, 'Veg Biryani', 'Fragrant rice with vegetables and spices', 30000, 1),
    (2, 'Paneer Butter Masala', 'Paneer cooked in creamy tomato gravy', 32000, 1),
    (3, 'Gulab Jamun', 'Traditional Indian sweet', 12000, 1),
    (3, 'Ice Cream', 'Vanilla ice cream', 10000, 1),
    (4, 'Fresh Lime Soda', 'Refreshing lime soda', 8000, 1),
    (4, 'Masala Tea', 'Indian spiced tea', 6000, 1);

-- Dining tables
INSERT INTO dining_tables (label, seats, active)
VALUES
    ('T1', 2, 1),
    ('T2', 4, 1),
    ('T3', 4, 1),
    ('T4', 6, 1),
    ('T5', 8, 1);

-- Seed customer
INSERT INTO customers (name, email, phone)
VALUES
    ('Test Customer', 'test@example.com', '9999999999');