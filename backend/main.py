from config import init_recipes_db
from utils.cooker import Cooker
from pprint import pprint
from utils.dumping import make_dump

cooker = Cooker(init_recipes_db())
print("Sucessfull start")


recipe_name = "sushi"
ingredients = {'japanese rice': ("kg", .3),
               'rice vinegar': ("tbsp", .5),
               'salmon': ("kg", 0.1)
               }

cooker.create_recipe(
    name=recipe_name,
    description="very simple recipe for traditional japanese dish - sushi",
    dish="sushi maki",
    cuisine="japanese",
    directions="1 steam rice 2 make balls out of it 3 put raw salmon on it",
    ingredients=ingredients
)

pprint(
    cooker.full_table_for_recipe(recipe_name=recipe_name)
)

pprint(cooker.ingredient_involvement(ingredient_name="salmon"))

pprint(
    cooker.show_all_ingredients()
)


cooker.delete_recipe(recipe_name=recipe_name)

pprint(
    cooker.recipe_analysis()
)

make_dump()



