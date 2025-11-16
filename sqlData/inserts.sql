SET FOREIGN_KEY_CHECKS = 0;

-- 2. Truncate Tables (Order doesn't matter much now, but keeping a logical order is good practice)

-- Linking/Child Tables
TRUNCATE TABLE offering_ingredients;
TRUNCATE TABLE ingredient_attributes;

-- Parent/Master Tables
TRUNCATE TABLE offerings;
TRUNCATE TABLE ingredients;
TRUNCATE TABLE attributes;
TRUNCATE TABLE menu_categories;
TRUNCATE TABLE faq;

-- 3. Re-enable Foreign Key Checks
-- Always re-enable checks to maintain data integrity for future operations.
SET FOREIGN_KEY_CHECKS = 1;


-- =================================================================
-- 1. MASTER DATA: Categories, Attributes, and Unique Ingredients
-- =================================================================

-- 1A. INSERT INTO menu_categories
-- Food Categories
INSERT INTO menu_categories (name, is_food) VALUES
('Antipasti', TRUE),        -- Appetizers
('Primi', TRUE),            -- First Courses (Pasta/Risotto)
('Secondi', TRUE),          -- Second Courses (Meat/Fish)
('Contorni', TRUE),         -- Side Dishes
('Pizze', TRUE),            -- Pizzas
('Dolci', TRUE);             -- Desserts

-- Drink Categories
INSERT INTO menu_categories (name, is_food) VALUES
('Acque Minerali', FALSE),  -- Mineral Waters
('Bevande Analcoliche', FALSE), -- Soft Drinks
('Birre', FALSE),           -- Beers
('Aperitivi', FALSE),       -- Aperitifs
('Vini Bianchi', FALSE),    -- White Wines
('Vini Rossi', FALSE),      -- Red Wines
('Spumanti', FALSE),        -- Sparkling Wines
('Caffetteria', FALSE),     -- Coffee
('Digestivi e Amari', FALSE);-- Digestifs & Bitters

-- 1B. INSERT INTO attributes
INSERT INTO attributes (attribute_name) VALUES
('Vegetarian'), ('Vegan'), ('Gluten'), ('Pork'), ('Beef'),
('Poultry'), ('Fish'), ('Seafood'), ('Dairy'), ('Nuts'), ('Alcohol');

-- 1C. INSERT INTO ingredients (Master List)
INSERT INTO ingredients (ingredient_id, name) VALUES
(1, 'Artisan Bread'), (2, 'Tomato'), (3, 'Garlic'), (4, 'Basil'), (5, 'Extra Virgin Olive Oil'),
(6, 'Burrata'), (7, 'Prosciutto di Parma'), (8, 'Arugula'), (9, 'Balsamic Glaze'), (10, 'Beef Carpaccio'),
(11, 'Parmigiano Reggiano'), (12, 'Lemon'), (13, 'Capers'), (14, 'Spaghetti'), (15, 'Guanciale'),
(16, 'Egg Yolk'), (17, 'Pecorino Romano'), (18, 'Black Pepper'), (19, 'Penne'), (20, 'Chili Flakes'),
(21, 'Parsley'), (22, 'Arborio Rice'), (23, 'Porcini Mushrooms'), (24, 'Vegetable Broth'), (25, 'White Wine'),
(26, 'Onion'), (27, 'Butter'), (28, 'Lasagna Sheets'), (29, 'Beef Mince'), (30, 'Pork Mince'),
(31, 'Béchamel Sauce'), (32, 'Pine Nuts'), (33, 'Potatoes'), (34, 'Rosemary'), (35, 'Veal Shank'),
(36, 'Gremolata'), (37, 'Saffron'), (38, 'Chicken Breast'), (39, 'Mushroom Cream Sauce'), (40, 'Sea Bass'),
(41, 'Cherry Tomatoes'), (42, 'Black Olives'), (43, 'Pizza Dough'), (44, 'San Marzano Tomatoes'), (45, 'Mozzarella'),
(46, 'Spicy Salami'), (47, 'Gorgonzola'), (48, 'Speck'), (49, 'Walnuts'), (50, 'Anchovies'),
(51, 'Oregano'), (52, 'Ladyfingers'), (53, 'Espresso Coffee'), (54, 'Mascarpone'), (55, 'Cocoa Powder'),
(56, 'Panna Cotta Cream'), (57, 'Berry Coulis'), (58, 'Ricotta Cheese'), (59, 'Candied Orange Peel'), (60, 'Pistachio'),
(61, 'Mineral Water'), (62, 'Cola'), (63, 'Orange Soda'), (64, 'Lemon Soda'), (65, 'Peach Iced Tea'),
(66, 'Lemon Iced Tea'), (67, 'Peroni Nastro Azzurro'), (68, 'Moretti'), (69, 'Ichnusa'), (70, 'Aperol'),
(71, 'Prosecco'), (72, 'Soda Water'), (73, 'Campari'), (74, 'Sweet Vermouth'), (75, 'Gin'),
(76, 'Orange Slice'), (77, 'Pinot Grigio Grapes'), (78, 'Chardonnay Grapes'), (79, 'Sauvignon Blanc Grapes'), (80, 'Chianti Grapes'),
(81, 'Barbera Grapes'), (82, 'Nero d''Avola Grapes'), (83, 'Glera Grapes'), (84, 'Coffee Beans'), (85, 'Milk'),
(86, 'Limoncello'), (87, 'Grappa'), (88, 'Amaro Montenegro'), (89, 'Fernet-Branca'), (90, 'Cynar'),
(91, 'Eggplant'), (92, 'Zucchini'), (93, 'Bell Peppers'),
(94, 'Fresh Herbs'), (95, 'Sea Salt'), (96, 'Carrot'), (97, 'Artichoke Hearts');

-- =================================================================
-- 2. LINKING DATA: Connecting Ingredients to their Attributes
-- =================================================================

INSERT INTO ingredient_attributes (ingredient_id, attribute_id) VALUES
-- Breads, Grains, etc (Gluten)
(1, 3), (14, 3), (19, 3), (28, 3), (43, 3), (52, 3),
-- Meats
(7, 4), (10, 5), (15, 4), (29, 5), (30, 4), (35, 5), (38, 6), (46, 4), (48, 4),
-- Dairy
(6, 9), (11, 9), (17, 9), (27, 9), (31, 9), (45, 9), (47, 9), (54, 9), (56, 9), (58, 9), (85, 9),
-- Nuts
(32, 10), (49, 10), (60, 10),
-- Fish/Seafood
(40, 7), (50, 7),
-- Vegetarian (base ingredients)
(1, 1), (2, 1), (3, 1), (4, 1), (5, 1), (6, 1), (8, 1), (9, 1), (11, 1), (12, 1), (13, 1),
(14, 1), (16, 1), (17, 1), (18, 1), (19, 1), (20, 1), (21, 1), (22, 1), (23, 1), (24, 1),
(25, 1), (26, 1), (27, 1), (28, 1), (31, 1), (32, 1), (33, 1), (34, 1), (37, 1), (41, 1),
(42, 1), (43, 1), (44, 1), (45, 1), (47, 1), (49, 1), (51, 1), (52, 1), (53, 1), (54, 1),
(55, 1), (56, 1), (57, 1), (58, 1), (59, 1), (60, 1), (84, 1), (85, 1), (91, 1), (92, 1), (93, 1), (94, 1), (95, 1), (96, 1), (97, 1),
-- Vegan (a subset of vegetarian)
(2, 2), (3, 2), (4, 2), (5, 2), (8, 2), (9, 2), (12, 2), (13, 2), (20, 2), (21, 2), (22, 2),
(23, 2), (24, 2), (26, 2), (32, 2), (33, 2), (34, 2), (41, 2), (42, 2), (44, 2), (49, 2),
(51, 2), (53, 2), (55, 2), (57, 2), (59, 2), (60, 2), (84, 2), (91, 2), (92, 2), (93, 2), (94, 2), (95, 2), (96, 2), (97, 2),
-- Alcohol
(25, 11), (70, 11), (71, 11), (73, 11), (74, 11), (75, 11), (77, 11), (78, 11), (79, 11),
(80, 11), (81, 11), (82, 11), (83, 11), (86, 11), (87, 11), (88, 11), (89, 11), (90, 11);


-- =================================================================
-- 3. MENU OFFERINGS & THEIR INGREDIENTS
-- =================================================================

-- 3A. ANTIPASTI (Category ID: 1)
-- -----------------------------------------------------------------
INSERT INTO offerings (offering_id, name, description, price, category_id, quantity, recommended) VALUES
(1, 'Bruschetta al Pomodoro', 'Toasted artisan bread with fresh tomatoes, garlic, basil, and a drizzle of extra virgin olive oil.', 8.00, 1, 100, FALSE),
(2, 'Burrata con Prosciutto di Parma', 'Creamy burrata cheese served with 24-month aged Parma ham, arugula, and a balsamic glaze.', 15.00, 1, 100, FALSE),
(3, 'Carpaccio di Manzo', 'Thinly sliced raw beef, topped with arugula, shaved Parmigiano Reggiano, capers, and a lemon-oil dressing.', 14.00, 1, 150, TRUE);

INSERT INTO offering_ingredients (offering_id, ingredient_id, is_removable) VALUES
-- Bruschetta
(1, 1, FALSE), (1, 2, FALSE), (1, 3, FALSE), (1, 4, TRUE), (1, 5, FALSE),
-- Burrata
(2, 6, FALSE), (2, 7, FALSE), (2, 8, TRUE), (2, 9, TRUE),
-- Carpaccio
(3, 10, FALSE), (3, 8, TRUE), (3, 11, TRUE), (3, 12, FALSE), (3, 13, TRUE);


-- 3B. PRIMI (Category ID: 2)
-- -----------------------------------------------------------------
INSERT INTO offerings (offering_id, name, description, price, category_id, quantity, recommended) VALUES
(4, 'Spaghetti alla Carbonara', 'A Roman classic with crispy guanciale, rich egg yolk, Pecorino Romano cheese, and black pepper.', 15.00, 2, 100, FALSE),
(5, 'Penne all''Arrabbiata', 'Penne pasta in a fiery tomato and garlic sauce, finished with fresh parsley.', 12.00, 2, 100, FALSE),
(6, 'Risotto ai Funghi Porcini', 'Creamy Arborio rice risotto with savory porcini mushrooms, white wine, and Parmigiano.', 16.00, 2, 150, TRUE),
(7, 'Lasagne alla Bolognese', 'Layers of fresh pasta with a rich beef and pork ragù, béchamel sauce, and baked with Parmigiano.', 14.00, 2, 100, FALSE),
(8, 'Trofie al Pesto', 'Traditional Ligurian pasta with a fresh basil pesto, pine nuts, and Parmigiano Reggiano.', 13.00, 2, 100, FALSE);

INSERT INTO offering_ingredients (offering_id, ingredient_id, is_removable) VALUES
-- Carbonara
(4, 14, FALSE), (4, 15, FALSE), (4, 16, FALSE), (4, 17, TRUE), (4, 18, TRUE),
-- Arrabbiata
(5, 19, FALSE), (5, 2, FALSE), (5, 3, FALSE), (5, 20, TRUE), (5, 21, TRUE),
-- Risotto
(6, 22, FALSE), (6, 23, FALSE), (6, 24, FALSE), (6, 25, FALSE), (6, 26, FALSE), (6, 27, FALSE), (6, 11, TRUE),
-- Lasagne
(7, 28, FALSE), (7, 29, FALSE), (7, 30, FALSE), (7, 2, FALSE), (7, 31, FALSE), (7, 11, FALSE),
-- Pesto
(8, 14, FALSE), (8, 4, FALSE), (8, 32, FALSE), (8, 11, TRUE), (8, 3, FALSE);


-- 3C. SECONDI (Category ID: 3)
-- -----------------------------------------------------------------
INSERT INTO offerings (offering_id, name, description, price, category_id, quantity, recommended) VALUES
(9, 'Osso Buco alla Milanese', 'Slow-cooked veal shank in a white wine and vegetable broth, served with traditional gremolata.', 28.00, 3, 150, TRUE),
(10, 'Tagliata di Manzo', 'Sliced grilled beef steak served over a bed of arugula, topped with cherry tomatoes and shaved Parmigiano.', 25.00, 3, 100, FALSE),
(11, 'Pollo ai Funghi', 'Pan-seared chicken breast in a creamy mushroom and white wine sauce.', 19.00, 3, 100, FALSE),
(12, 'Spigola al Forno', 'Oven-baked sea bass with cherry tomatoes, black olives, capers, and fresh herbs.', 24.00, 3, 100, FALSE);

INSERT INTO offering_ingredients (offering_id, ingredient_id, is_removable) VALUES
-- Osso Buco
(9, 35, FALSE), (9, 25, FALSE), (9, 24, FALSE), (9, 36, TRUE), (9, 26, FALSE),
-- Tagliata
(10, 10, FALSE), (10, 8, TRUE), (10, 41, TRUE), (10, 11, TRUE),
-- Pollo ai Funghi
(11, 38, FALSE), (11, 39, FALSE), (11, 23, FALSE), (11, 25, FALSE),
-- Spigola
(12, 40, FALSE), (12, 41, TRUE), (12, 42, TRUE), (12, 13, TRUE), (12, 94, TRUE);


-- 3D. CONTORNI (Category ID: 4)
-- -----------------------------------------------------------------
INSERT INTO offerings (offering_id, name, description, price, category_id, quantity, recommended) VALUES
(13, 'Patate al Forno', 'Oven-roasted potatoes with rosemary, garlic, and sea salt.', 6.00, 4, 150, TRUE),
(14, 'Insalata Mista', 'A mixed green salad with tomatoes, carrots, and a simple vinaigrette.', 5.00, 4, 100, FALSE),
(15, 'Verdure Grigliate', 'A selection of seasonal grilled vegetables, including eggplant, zucchini, and bell peppers.', 7.00, 4, 100, FALSE);

INSERT INTO offering_ingredients (offering_id, ingredient_id, is_removable) VALUES
-- Patate
(13, 33, FALSE), (13, 34, TRUE), (13, 3, TRUE), (13, 5, FALSE), (13, 95, TRUE),
-- Insalata
(14, 8, FALSE), (14, 2, TRUE), (14, 5, FALSE), (14, 96, TRUE),
-- Verdure
(15, 91, FALSE), (15, 92, FALSE), (15, 93, FALSE);


-- 3E. PIZZE (Category ID: 5)
-- -----------------------------------------------------------------
INSERT INTO offerings (offering_id, name, description, price, category_id, quantity, recommended) VALUES
(16, 'Margherita', 'The classic: San Marzano tomatoes, fresh mozzarella, basil, and extra virgin olive oil.', 9.00, 5, 100, FALSE),
(17, 'Diavola', 'A spicy favorite with San Marzano tomatoes, mozzarella, and spicy salami.', 11.00, 5, 100, FALSE),
(18, 'Quattro Formaggi', 'A rich blend of four cheeses: mozzarella, gorgonzola, Parmigiano, and Pecorino.', 12.00, 5, 100, FALSE),
(19, 'Capricciosa', 'A feast of toppings including tomatoes, mozzarella, ham, mushrooms, artichokes, and olives.', 13.00, 5, 100, TRUE),
(20, 'Gorgonzola, Speck e Noci', 'White pizza with mozzarella, gorgonzola cheese, smoked speck, and walnuts.', 14.00, 5, 100, FALSE),
(21, 'Napoli', 'A taste of Naples with San Marzano tomatoes, mozzarella, anchovies, and oregano.', 10.00, 5, 100, FALSE);

INSERT INTO offering_ingredients (offering_id, ingredient_id, is_removable) VALUES
-- Margherita
(16, 43, FALSE), (16, 44, FALSE), (16, 45, FALSE), (16, 4, TRUE), (16, 5, FALSE),
-- Diavola
(17, 43, FALSE), (17, 44, FALSE), (17, 45, FALSE), (17, 46, FALSE),
-- Quattro Formaggi
(18, 43, FALSE), (18, 45, FALSE), (18, 47, FALSE), (18, 11, FALSE), (18, 17, FALSE),
-- Capricciosa
(19, 43, FALSE), (19, 44, FALSE), (19, 45, FALSE), (19, 7, TRUE), (19, 23, TRUE), (19, 42, TRUE), (19, 97, TRUE),
-- Gorgonzola, Speck e Noci
(20, 43, FALSE), (20, 45, FALSE), (20, 47, FALSE), (20, 48, TRUE), (20, 49, TRUE),
-- Napoli
(21, 43, FALSE), (21, 44, FALSE), (21, 45, FALSE), (21, 50, TRUE), (21, 51, TRUE);


-- 3F. DOLCI (Category ID: 6)
-- -----------------------------------------------------------------
INSERT INTO offerings (offering_id, name, description, price, category_id, quantity, recommended) VALUES
(22, 'Tiramisù', 'The classic Italian dessert with layers of coffee-soaked ladyfingers and creamy mascarpone.', 7.00, 6, 100, TRUE),
(23, 'Panna Cotta', 'A silky smooth cooked cream dessert, served with a seasonal berry coulis.', 6.00, 6, 100, FALSE),
(24, 'Cannoli Siciliani', 'Crispy pastry tubes filled with a sweet, creamy ricotta and pistachio filling.', 8.00, 6, 100, FALSE);

INSERT INTO offering_ingredients (offering_id, ingredient_id, is_removable) VALUES
-- Tiramisù
(22, 52, FALSE), (22, 53, FALSE), (22, 54, FALSE), (22, 16, FALSE), (22, 55, TRUE),
-- Panna Cotta
(23, 56, FALSE), (23, 57, TRUE),
-- Cannoli
(24, 28, FALSE), (24, 58, FALSE), (24, 59, TRUE), (24, 60, TRUE);


-- 3G. DRINKS (Category IDs: 7-15)
-- -----------------------------------------------------------------
INSERT INTO offerings (offering_id, name, description, price, category_id, quantity, recommended) VALUES
-- Acque Minerali (7)
(25, 'Acqua Naturale 75cl', 'Still mineral water.', 3.00, 7, 100, FALSE),
(26, 'Acqua Frizzante 75cl', 'Sparkling mineral water.', 3.00, 7, 100, FALSE),
-- Bevande Analcoliche (8)
(27, 'Coca-Cola', 'Classic Coca-Cola.', 3.50, 8, 100, FALSE),
(28, 'Coca-Cola Zero', 'Zero sugar Coca-Cola.', 3.50, 8, 100, FALSE),
(29, 'Aranciata', 'Italian orange soda.', 3.50, 8, 150, TRUE),
(30, 'Limonata', 'Italian lemon soda.', 3.50, 8, 100, FALSE),
(31, 'Tè alla Pesca', 'Peach iced tea.', 3.50, 8, 100, FALSE),
(32, 'Tè al Limone', 'Lemon iced tea.', 3.50, 8, 100, FALSE),
-- Birre (9)
(33, 'Peroni Nastro Azzurro', 'Classic Italian lager, 33cl bottle.', 5.00, 9, 100, FALSE),
(34, 'Moretti', 'A quality beer made in the traditional way, 33cl bottle.', 5.00, 9, 100, FALSE),
(35, 'Ichnusa Non Filtrata', 'Unfiltered Sardinian lager, 33cl bottle.', 6.00, 9, 100, FALSE),
-- Aperitivi (10)
(36, 'Aperol Spritz', 'Aperol, Prosecco, and a splash of soda.', 8.00, 10, 100, FALSE),
(37, 'Campari Spritz', 'Campari, Prosecco, and a splash of soda.', 8.00, 10, 100, FALSE),
(38, 'Negroni', 'A perfect balance of Campari, sweet vermouth, and gin.', 9.00, 10, 100, FALSE),
-- Vini Bianchi (11) - Bottle
(39, 'Pinot Grigio', 'Dry and crisp white wine from Veneto.', 22.00, 11, 150, TRUE),
(40, 'Chardonnay', 'Fruity and full-bodied white wine from Trentino.', 25.00, 11, 100, FALSE),
(41, 'Sauvignon Blanc', 'Aromatic white wine from Friuli.', 28.00, 11, 100, FALSE),
-- Vini Rossi (12) - Bottle
(42, 'Chianti Classico', 'Classic Tuscan red, robust and fruity.', 26.00, 12, 100, FALSE),
(43, 'Barbera d''Asti', 'Medium-bodied red from Piedmont.', 24.00, 12, 100, FALSE),
(44, 'Nero d''Avola', 'Full-bodied and spicy red from Sicily.', 28.00, 12, 100, FALSE),
-- Spumanti (13) - Bottle
(45, 'Prosecco DOC Treviso', 'Extra dry sparkling wine, perfect for celebrating.', 25.00, 13, 100, FALSE),
-- Caffetteria (14)
(46, 'Espresso', 'A single shot of rich Italian coffee.', 1.50, 14, 100, FALSE),
(47, 'Espresso Macchiato', 'Espresso "stained" with a drop of frothy milk.', 1.80, 14, 100, FALSE),
(48, 'Cappuccino', 'Espresso with steamed milk foam.', 2.50, 14, 100, FALSE),
(49, 'Caffè Latte', 'Espresso with a larger amount of steamed milk.', 3.00, 14, 100, FALSE),
(50, 'Caffè Corretto', 'Espresso "corrected" with a shot of grappa or sambuca.', 3.50, 14, 100, FALSE),
-- Digestivi e Amari (15)
(51, 'Limoncello', 'Sweet and fragrant lemon liqueur from Southern Italy.', 5.00, 15, 100, FALSE),
(52, 'Grappa', 'Fragrant, grape-based pomace brandy.', 6.00, 15, 100, FALSE),
(53, 'Amaro Montenegro', 'A classic bittersweet liqueur with notes of orange peel and vanilla.', 5.00, 15, 100, FALSE),
(54, 'Fernet-Branca', 'Aromatic and intensely bitter herbal liqueur.', 5.00, 15, 100, FALSE),
(55, 'Cynar', 'An artichoke-based bittersweet liqueur.', 5.00, 15, 100, FALSE);

INSERT INTO offering_ingredients (offering_id, ingredient_id, is_removable) VALUES
-- Water
(25, 61, FALSE), (26, 61, FALSE),
-- Soft Drinks
(27, 62, FALSE), (28, 62, FALSE), (29, 63, FALSE), (30, 64, FALSE), (31, 65, FALSE), (32, 66, FALSE),
-- Beers
(33, 67, FALSE), (34, 68, FALSE), (35, 69, FALSE),
-- Aperitivi
(36, 70, FALSE), (36, 71, FALSE), (36, 72, TRUE), (36, 76, TRUE),
(37, 73, FALSE), (37, 71, FALSE), (37, 72, TRUE), (37, 76, TRUE),
(38, 73, FALSE), (38, 74, FALSE), (38, 75, FALSE), (38, 76, TRUE),
-- Wines
(39, 77, FALSE), (40, 78, FALSE), (41, 79, FALSE), (42, 80, FALSE), (43, 81, FALSE), (44, 82, FALSE),
-- Spumanti
(45, 83, FALSE),
-- Coffee
(46, 84, FALSE), (47, 84, FALSE), (47, 85, TRUE), (48, 84, FALSE), (48, 85, FALSE),
(49, 84, FALSE), (49, 85, FALSE), (50, 84, FALSE), (50, 87, FALSE),
-- Digestivi
(51, 86, FALSE), (52, 87, FALSE), (53, 88, FALSE), (54, 89, FALSE), (55, 90, FALSE);



INSERT INTO FAQ (`key`, `value`) VALUES
('working_hours', 'We are open Monday to Sunday, from 11:00 AM to 1:00 AM.'),
('location', 'You can find us at 123 Pasta Lane, Rome, Italy. Buon appetito!'),
('phone_number', 'Feel free to call us at +39 012 345 6789 for any inquiries or reservations.'),
('email', 'You can reach us via email at ciao@ourrestaurant.it.'),
('website', 'Visit our website at www.ourrestaurant.it for our full menu and online reservations.'),
('make_reservation', 'You can book a table through our website, by calling us at +39 012 345 6789, or directly through this chat!'),
('cancel_reservation', 'To cancel a reservation, please call us at least 3 hours in advance.'),
('private_dining', 'Yes, we have a private room that can accommodate up to 20 guests. Please email us at events@ourrestaurant.it for details.'),
('walk_ins', 'Walk-ins are always welcome! However, we recommend making a reservation, especially on weekends, to avoid disappointment.'),
('menu_link', 'You can view our full menu here: www.ourrestaurant.it/menu'),
('kids_menu', 'No dedicated kids menu.'),
('nut_allergy', 'Our kitchen handles nuts. Please inform your server of any allergies so we can take extra precautions.'),
('dairy_allergy', 'We can prepare many dishes without dairy. Please speak to your server for recommendations.'),
('takeaway', 'We don''t provide takeaway service.'),
('delivery_services', 'We don''t provide delivery service.'),
('parking', 'There is paid street parking available nearby and a public parking garage two blocks away.'),
('wifi', 'Yes, we offer complimentary Wi-Fi for our guests. The password is "mangiamangia".'),
('accessibility', 'Our restaurant is fully wheelchair accessible, including our restrooms.'),
('payment_methods', 'We accept cash, Visa, MasterCard, and American Express.'),
('credit_cards_accepted', 'We accept all major credit cards, including Visa, MasterCard, and American Express.'),
('gift_cards', 'Yes, gift cards are available for purchase at the restaurant. They make a perfect gift!'),
('happy_hour', 'Join us for Aperitivo Hour from 4:00 PM to 6:00 PM on weekdays for special prices on drinks and appetizers.'),
('live_music', 'We have live acoustic music every Friday and Saturday evening from 8:00 PM.'),
('special_events', 'Follow us on our social media channels to stay updated on special events like wine tasting nights and holiday menus.'),
('birthday_offer', 'Celebrating a birthday? Let us know when you book, and we''ll treat the birthday person to a complimentary dessert!'),
('anniversary_package', 'We can help make your anniversary special with a complimentary glass of prosecco. Please mention the occasion when you book.'),
('about_us', 'We are a family-owned restaurant dedicated to serving authentic Italian cuisine made with love and the freshest ingredients.'),
('chef_name', 'Our kitchen is led by the talented Chef Giovanni Rossi, who brings recipes from his hometown of Naples.'),
('restaurant_story', 'Our family opened this restaurant in 1995 with a dream of sharing our nonna''s recipes with the community.'),
('dress_code', 'Our dress code is smart casual. We want you to be comfortable!'),
('pet_policy', 'We welcome well-behaved dogs on our outdoor patio area.'),
('corkage_fee', 'We have a curated wine list, but if you wish to bring your own bottle, our corkage fee is €15.'),
('cake_policy', 'You are welcome to bring your own celebration cake.'),
('lost_and_found', 'If you believe you''ve left something behind, please call us at +39 012 345 6789 and we will check for you.'),
('greeting', 'Ciao! Welcome to our restaurant. How can I help you today?'),
('help', 'You can ask me about our hours, menu, reservations, or location. Just type your question!'),
('human_agent', 'If you need to speak with a person, please call the restaurant directly at +39 012 345 6789.'),
('thank_you', 'You are most welcome! Is there anything else I can help you with?'),
('goodbye', 'Grazie and arriveci! We hope to see you soon.');
