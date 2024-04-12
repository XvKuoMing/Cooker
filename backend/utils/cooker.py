"""a bunch of sql-queries for building recipe analytics"""
from typing import Dict, Optional, Tuple, Union
import mysql.connector

class Cooker:

    def __init__(self, server_config: Dict[str, Union[str, int]]):
        self.config = server_config
        self.conn = mysql.connector.connect(**self.config)
        self.cursor = self.conn.cursor(dictionary=True)

    def set_basic_units(self, unit: str):
        self.cursor.execute(f"""
        INSERT INTO cookbook.units(name) VALUES("{unit}")
        """)

    def create_recipe(self, name: str,
                      description: Optional[str],
                      cuisine: Optional[str],
                      dish: str,
                      ingredients: Dict[str, Tuple[str, Union[int, float]]],
                      directions: str):

        self.cursor.execute(f"""
                INSERT INTO cookbook.recipes(name, dish, directions, description, cuisine) VALUES ("{name}", "{dish}", "{directions}", "{description}", "{cuisine}")
                """)
        recipe_id = self.cursor.lastrowid

        for ingredient, u2q in ingredients.items():
            unit, quantity = u2q
            self.cursor.execute(f"""
            SELECT id FROM cookbook.ingredients WHERE name="{ingredient}"
            """)
            if self.cursor.fetchone() is None:
                self.cursor.execute(f"""
                INSERT INTO cookbook.ingredients(name) VALUES ("{ingredient}")
                """)
                ingredient_id = self.cursor.lastrowid
                try:
                    self.cursor.execute(f"""
                    SELECT id FROM cookbook.units WHERE name="{unit}"
                    """)
                    unit_id = self.cursor.fetchone()['id']
                except TypeError:
                    self.set_basic_units(unit)
                    unit_id = self.cursor.lastrowid

                self.cursor.execute(f"""
                INSERT INTO cookbook.facts(recipe_id, ingredient_id, unit_id, quantity) VALUES({recipe_id}, {ingredient_id}, "{unit_id}", "{quantity}")
                """)
        self.conn.commit()

    def update_facts(self,
                     recipe_name: str,
                     ingredient_name: str,
                     unit: str,
                     quantity: float):

        self.cursor.execute(f"""
        UPDATE cookbook.facts
        SET 
        unit_id=(SELECT id FROM cookbook.units WHERE name="{unit}"),
        quantity={quantity}
        WHERE 
        recipe_id=(SELECT id FROM cookbook.recipes WHERE name="{recipe_name}"),
        ingredient_id=(SELECT id FROM cookbook.ingredients WHERE name="{ingredient_name}")
        """)
        self.conn.commit()

    def update_recipes_directions(self, recipe_name: str, new_directions: str):
        self.cursor.execute(f"""
        UPDATE cookbook.recipes
        SET directions="{new_directions}"
        WHERE name="{recipe_name}"
        """)
        self.conn.commit()

    def delete_recipe(self, recipe_name: str):
        self.cursor.execute(f"""
        DELETE FROM cookbook.recipes
        WHERE name="{recipe_name}"
        """)
        self.conn.commit()

    def ingredient_involvement(self, ingredient_name: str):
        """given ingredient name, counts in how many recipes it's involved"""
        self.cursor.execute(f"""
        SELECT COUNT(recipe_id) AS count_recipes
        FROM cookbook.facts
        GROUP BY ingredient_id
        HAVING ingredient_id=(SELECT id FROM cookbook.ingredients WHERE name="{ingredient_name}")
        """)
        return self.cursor.fetchall()

    def full_table_for_recipe(self, recipe_name: str):
        """given recipe, returns all info"""
        self.cursor.execute("""
        SELECT 
        cookbook.recipes.name AS recipe,
        cookbook.recipes.dish AS dish,
        cookbook.ingredients.name AS ingredient,
        cookbook.units.name AS unit,
        cookbook.facts.quantity AS quantity,
        cookbook.recipes.directions AS directions
        FROM 
        cookbook.recipes,
        cookbook.ingredients,
        cookbook.units,
        cookbook.facts
        WHERE
        cookbook.facts.recipe_id=cookbook.recipes.id
        AND
        cookbook.facts.ingredient_id=cookbook.ingredients.id
        AND
        cookbook.facts.unit_id=cookbook.units.id
        """)
        return self.cursor.fetchall()

    def show_all_ingredients(self):
        """list all ingredients and recipe it is involved"""
        self.cursor.execute(f"""
        WITH ingr2recipe_id AS
            (SELECT 
            cookbook.ingredients.name AS ingredient,
            cookbook.facts.recipe_id AS recipe_id 
            FROM cookbook.ingredients
            JOIN cookbook.facts
            ON cookbook.ingredients.id=cookbook.facts.ingredient_id)
        SELECT
        ingredient,
        cookbook.recipes.name AS recipe, 
        COUNT(cookbook.recipes.name) OVER(PARTITION BY ingredient) AS count_recipes
        FROM ingr2recipe_id 
        LEFT JOIN cookbook.recipes 
        ON ingr2recipe_id.recipe_id=cookbook.recipes.id
        ORDER BY count_recipes
        """)

        return self.cursor.fetchall()

    def recipe_analysis(self):
        self.cursor.execute("""
        CALL recipe_archive_analysis()
        """)
        return self.cursor.fetchall()









