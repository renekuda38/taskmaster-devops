CREATE TABLE tasks (
    id SERIAL PRIMARY KEY,
    task_name VARCHAR(100) NOT NULL,
    task_desc VARCHAR(100),
    creation_date DATE DEFAULT CURRENT_DATE,
    accomplish_time INT,
    done BOOLEAN DEFAULT FALSE
);
