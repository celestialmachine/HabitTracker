CREATE TABLE completions (
    completion_id INT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    habit_id INT NOT NUlL REFERENCES habits(habit_id),
    completion_date DATE NOT NULL DEFAULT CURRENT_DATE,
    UNIQUE (habit_id, completion_date)
);