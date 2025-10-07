
-- Independent master tables
-- ===================================

-- Stores menu sections like 'Appetizers', 'Main Courses', 'Beers', 'Wines'
CREATE TABLE menu_categories (
    category_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE,
    is_food BOOLEAN DEFAULT TRUE
);

-- Stores unique, reusable ingredients like 'Tomato', 'Beef', 'Cheese'
CREATE TABLE ingredients (
    ingredient_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE
);


-- Stores ingredient attributes like 'Vegetarian', 'Vegan', 'Gluten-Free'
CREATE TABLE attributes (
    attribute_id INT AUTO_INCREMENT PRIMARY KEY,
    attribute_name VARCHAR(100) NOT NULL UNIQUE
);


-- Dependent tables and link tables
-- ===================================

-- Stores the actual menu offerings like 'Classic Burger' or 'Craft Beer'
CREATE TABLE offerings (
    offering_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    price DECIMAL(10, 2) NOT NULL,
    category_id INT,
    recommended BOOLEAN NOT NULL DEFAULT FALSE,
    quantity INT NOT NULL DEFAULT 0,
    FOREIGN KEY (category_id) REFERENCES menu_categories(category_id) ON DELETE SET NULL
);

-- Many-to-many link between ingredients and their attributes
CREATE TABLE ingredient_attributes (
    ingredient_id INT NOT NULL,
    attribute_id INT NOT NULL,
    PRIMARY KEY (ingredient_id, attribute_id),
    FOREIGN KEY (ingredient_id) REFERENCES ingredients(ingredient_id) ON DELETE CASCADE,
    FOREIGN KEY (attribute_id) REFERENCES attributes(attribute_id) ON DELETE CASCADE
);

-- Links offerings to their ingredients and stores offering-specific rules
CREATE TABLE offering_ingredients (
    offering_id INT NOT NULL,
    ingredient_id INT NOT NULL,
    is_removable BOOLEAN DEFAULT TRUE,
    PRIMARY KEY (offering_id, ingredient_id),
    FOREIGN KEY (offering_id) REFERENCES offerings(offering_id) ON DELETE CASCADE,
    FOREIGN KEY (ingredient_id) REFERENCES ingredients(ingredient_id) ON DELETE CASCADE
);


-- Ordering system tables
-- ===================================

-- Stores each item within a customer's order
CREATE TABLE order_items (
    order_item_id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT NOT NULL,
    offering_id INT NOT NULL,
    special_instructions TEXT,
    order_status ENUM('pending', 'preparing', 'served', 'paid', 'cancelled') DEFAULT 'pending',
    sys_creation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    sys_update_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    quantity INT NOT NULL DEFAULT 1,
    INDEX(order_id),
    FOREIGN KEY (offering_id) REFERENCES offerings(offering_id)
);

-- Stores information about ingredients removed from an order item
CREATE TABLE order_item_modifications (
    modification_id INT AUTO_INCREMENT PRIMARY KEY,
    order_item_id INT NOT NULL,
    ingredient_id_to_remove INT NOT NULL,
    FOREIGN KEY (order_item_id) REFERENCES order_items(order_item_id) ON DELETE CASCADE,
    FOREIGN KEY (ingredient_id_to_remove) REFERENCES ingredients(ingredient_id) ON DELETE RESTRICT
);