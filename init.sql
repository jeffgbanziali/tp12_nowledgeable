SET NAMES utf8mb4;

CREATE TABLE IF NOT EXISTS clients (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL
);

INSERT INTO clients (name) VALUES
('Alice Martin'),
('Bob Durand'),
('Chloé Bernard');