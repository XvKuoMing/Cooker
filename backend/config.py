import mysql.connector

def init_recipes_db():

    # Подключение к бд
    server_config = {
        'user': 'root',
        'password': '101',
        'host': 'localhost',
        'port': 3306,
    }

    conn = mysql.connector.connect(**server_config)
    cur = conn.cursor()

    # создание схемы
    cur.execute("""
    DROP DATABASE IF EXISTS cookbook
    """)

    cur.execute("""
    CREATE DATABASE IF NOT EXISTS cookbook
    """)

    cur.execute("""
    USE cookbook;
    """)

    cur.execute("""
    SET GLOBAL sql_mode=''
    """)

    cur.execute("""
    CREATE TABLE cookbook.recipes (
    id INT NOT NULL AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL UNIQUE,
    cuisine VARCHAR(100) DEFAULT NULL,
    dish VARCHAR(100) NOT NULL,
    description TEXT DEFAULT NULL,
    directions TEXT NOT NULL,
    PRIMARY KEY(id),
    INDEX idx_dishes (dish),
    INDEX idx_cuisines (cuisine)
    );
    """)

    cur.execute("""
    CREATE TABLE cookbook.ingredients (
    id INT NOT NULL AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    PRIMARY KEY(id)
    );
    """)

    cur.execute("""
    CREATE TABLE cookbook.units (
    id INT NOT NULL AUTO_INCREMENT,
    name VARCHAR(30) NOT NULL,
    PRIMARY KEY(id)
    );
    """)

    cur.execute("""
    CREATE TABLE cookbook.facts (
    id INT NOT NULL,
    recipe_id INT,
    ingredient_id INT NOT NULL,
    unit_id INT DEFAULT NULL,
    quantity DECIMAL(4, 2) DEFAULT NULL,
    FOREIGN KEY(recipe_id) REFERENCES cookbook.recipes(id) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY(ingredient_id) REFERENCES cookbook.ingredients(id) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY(unit_id) REFERENCES cookbook.units(id) ON DELETE CASCADE ON UPDATE CASCADE,
    INDEX idx_recipes (recipe_id)
    );
    """)

    # создадим триггеры и таблицу для архивацию удаленных данных
    cur.execute("""
    CREATE TABLE cookbook.recipes_archive (
    id INT NOT NULL AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL UNIQUE,
    cuisine VARCHAR(100) DEFAULT NULL,
    dish VARCHAR(100) NOT NULL,
    description TEXT DEFAULT NULL,
    directions TEXT NOT NULL,
    removed_on TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY(id)
    );
    """)

    cur.execute("""
    CREATE TRIGGER archive_recipes BEFORE DELETE
    ON cookbook.recipes
    FOR EACH ROW
        INSERT INTO
        cookbook.recipes_archive (name, cuisine, dish, description, directions)
        VALUES (OLD.name, OLD.cuisine, OLD.dish, OLD.description, OLD.directions)
    """)

    # создадим одну процедуру для вывода аналитического отчета архивной таблицы
    cur.execute("""
    CREATE PROCEDURE recipe_archive_analysis (
    )
    BEGIN
        SELECT
        removed_on AS date,
        cuisine,
        dish,
        name,
        COUNT(name) OVER(PARTITION BY cuisine) AS "recipe_count",
        COUNT(name) OVER(PARTITION BY dish) AS "dish_count"
        FROM cookbook.recipes_archive
        ORDER BY removed_on;
    END
    """)

    # connecting to db
    server_config['database'] = "cookbook"
    return server_config


