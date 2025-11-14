
CREATE OR REPLACE TABLE your_dataset.customer_transactions (
    customer_id STRING,
    transaction_date DATE,
    amount FLOAT64
);

INSERT INTO your_dataset.customer_transactions (customer_id, transaction_date, amount) VALUES
('customer1', '2023-01-15', 100.50),
('customer2', '2023-01-16', 75.20),
('customer1', '2023-02-10', 50.00),
('customer3', '2023-02-12', 200.00),
('customer2', '2023-03-05', 120.00),
('customer1', '2023-04-20', 80.75),
('customer4', '2023-04-22', 150.00),
('customer3', '2023-05-18', 60.50),
('customer2', '2023-06-10', 90.00),
('customer4', '2023-07-15', 220.00),
('customer1', '2023-08-01', 110.25),
('customer5', '2023-08-05', 300.00),
('customer2', '2023-09-12', 40.00),
('customer3', '2023-10-20', 180.00),
('customer5', '2023-11-15', 250.00),
('customer1', '2023-12-01', 95.00);
