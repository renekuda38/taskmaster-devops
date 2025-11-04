CREATE TABLE tasks (
    id SERIAL PRIMARY KEY,
    task_name VARCHAR(100),
    creation_date DATE,
    done BOOLEAN DEFAULT FALSE,
    accomplish_time INT,
    topic_type VARCHAR(100)
);
