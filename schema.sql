CREATE DATABASE IF NOT EXISTS rentease;
USE rentease;

CREATE TABLE IF NOT EXISTS users (
   id INT PRIMARY KEY AUTO_INCREMENT,
   full_name VARCHAR(100),
   email VARCHAR(100) UNIQUE,
   password_hash VARCHAR(255),
   user_type ENUM('owner', 'renter'),
   created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS items (
   id INT PRIMARY KEY AUTO_INCREMENT,
   owner_id INT,
   title VARCHAR(150),
   description TEXT,
   category VARCHAR(50),
   price_per_day DECIMAL(10,2),
   product_price DECIMAL(10,2) NOT NULL DEFAULT 0,
   image_url VARCHAR(255),
   is_available BOOLEAN DEFAULT TRUE,
   created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
   FOREIGN KEY (owner_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS rental_requests (
   id INT PRIMARY KEY AUTO_INCREMENT,
   item_id INT,
   renter_id INT,
   start_date DATE,
   end_date DATE,
   total_days INT,
   total_amount DECIMAL(10,2),
   security_deposit DECIMAL(10,2) DEFAULT 0,
   rent_amount DECIMAL(10,2) DEFAULT 0,
   grand_total DECIMAL(10,2) DEFAULT 0,
   deposit_status ENUM('held','refunded','partially_deducted','fully_deducted') DEFAULT 'held',
   deposit_deduction DECIMAL(10,2) DEFAULT 0,
   deposit_refund DECIMAL(10,2) DEFAULT 0,
   deduction_reason TEXT,
   status ENUM('pending', 'accepted', 'rejected') DEFAULT 'pending',
   created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
   FOREIGN KEY (item_id) REFERENCES items(id) ON DELETE CASCADE,
   FOREIGN KEY (renter_id) REFERENCES users(id) ON DELETE CASCADE
);