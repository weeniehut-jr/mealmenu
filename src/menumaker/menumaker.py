import re
import json
import pathlib
import calendar
import random
from io import StringIO

MealMenu = []

ingredient_match = re.compile('(?>\]\s*)(\w.*$)')
optional_ingredient_match = re.compile('(?>\)\s*)(\w.*$)')
heading_markers_match = re.compile('^(#*)\s*(\w.*)')
meal_match_c = re.compile('\*\*(.*?)\*\*')

day_format = '## {day}\n\n'
mealtime_format = '### {mealtime}\n\n'

class MealEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Meal):
            return obj.__dict__
        if isinstance(obj, MealPlan):
            return obj.daily_plans
        return super().default(obj)

class MealPlan:
    def __init__(self):
        mealtimes = ['lunch', 'dinner']
        self.daily_plans = {}
        for day in calendar.day_name:
            self.daily_plans[day] = {mealtime: random.choice([meal for meal in MealMenu if meal.mealtime == mealtime]) for mealtime in mealtimes}
    def to_markdown(self):
        markdown_builder = StringIO()
        for day, obj in self.daily_plans.items():
            markdown_builder.write(day_format.format(day=day))
            for mealtime, meal in obj.items():
                markdown_builder.write(mealtime_format.format(mealtime=mealtime))
                markdown_builder.write(meal.to_markdown())
                markdown_builder.write("\n\n")
        return markdown_builder.getvalue()


class Meal:
    def __init__(self, name, mealtime, ingredients, optional_ingredients,
                 style):
        self.name = name
        self.mealtime = mealtime
        self.ingredients = ingredients
        self.optional_ingredients = optional_ingredients
        self.style = style

    def to_markdown(self):
        ingredients_markdown = "\n".join([f'- [ ] {ingredient}' for ingredient in self.ingredients])
        optional_ingredients_markdown = "\n".join([f'- [ ] (optional) {ingredient}' for ingredient in self.optional_ingredients])
        return f"""**{self.name}:**
Style: {self.style}
Ingredients:
{ingredients_markdown}
{optional_ingredients_markdown}"""

    @staticmethod
    def from_readme(f, name, mealtime, style):
        ingredients = []
        optional_ingredients = []

        while True:
            line = f.readline()
            if line == '' or line == '\n':
                break

        
            opt_ingr_match = optional_ingredient_match.search(line)
            if opt_ingr_match != None:
                optional_ingredients.append(opt_ingr_match.group(1))
            ingr_match = ingredient_match.search(line)
            if ingr_match != None:
                ingredients.append(ingr_match.group(1))
        return Meal(name, mealtime, ingredients, optional_ingredients, style)


def load_readme(path):
    with open(path, 'r') as f:
        mealtime = None
        style = None
        while True:
            line = f.readline()
            if line == '':
                break

            heading_match = heading_markers_match.match(line)
            meal_match = meal_match_c.match(line)

            if heading_match != None:
                num_markers = len(heading_match.group(1))
                heading = heading_match.group(2).lower()
                if num_markers == 2:
                    mealtime = heading
                if num_markers == 3:
                    style = heading
            elif meal_match != None:
                name = meal_match.group(1)
                meal = Meal.from_readme(f, name, mealtime, style)
                MealMenu.append(meal)

if __name__ == "__main__":
    random.seed()
    path = pathlib.Path('/Users/mcox59/devel/mealmenu/README.md')
    load_readme(path)
    # for meal in MealMenu:
    #     print(meal.to_json())
    
    mealplan = MealPlan()

    print(mealplan.to_markdown())





