import os
import psycopg2

DB_PARAMS = {
    "dbname": "postgres",
    "user": "postgres",
    r"password": os.getenv("DB_PASSWORD", ""),
    "host": "localhost",
    "port": "5432",
}


class MealPlannerChef:
    def __init__(self):
        self._init_db()

    def _get_connection(self):
        return psycopg2.connect(**DB_PARAMS)

    def _init_db(self):
        conn = self._get_connection()
        c = conn.cursor()
        c.execute("""CREATE TABLE IF NOT EXISTS pantry
                     (id SERIAL PRIMARY KEY, 
                      ingredient TEXT UNIQUE, 
                      quantity TEXT)""")
        conn.commit()
        conn.close()

    def update_pantry(self, ingredient, quantity):
        conn = self._get_connection()
        c = conn.cursor()
        c.execute(
            """INSERT INTO pantry (ingredient, quantity) 
                     VALUES (%s, %s) 
                     ON CONFLICT (ingredient) 
                     DO UPDATE SET quantity = EXCLUDED.quantity""",
            (ingredient, quantity),
        )
        conn.commit()
        conn.close()
        return f"Pantry updated: {ingredient} ({quantity})"

    def get_pantry_items(self):
        conn = self._get_connection()
        c = conn.cursor()
        c.execute("SELECT ingredient, quantity FROM pantry")
        items = c.fetchall()
        conn.close()

        if not items:
            return "Your pantry is empty."
        return "Current Pantry Items:\n" + "\n".join(
            [f"- {i[0]} ({i[1]})" for i in items]
        )

    def suggest_recipe(self):
        # In a real scenario, this would call an LLM with the pantry items to generate a recipe.
        pantry_items = self.get_pantry_items()
        if "empty" in pantry_items:
            return "I cannot suggest a recipe because your pantry is empty."

        # Mock LLM response
        prompt = f"Given these ingredients:\n{pantry_items}\nSuggest a simple meal."
        # Call enterprise_llm_gateway or similar...
        return "Based on your pantry, I suggest making a 'Kitchen Sink Stir Fry'. You'll need to chop whatever vegetables you have and fry them with some oil and soy sauce."

    def process_intent(self, intent_data):
        action = intent_data.get("action", "")
        if action == "update_pantry":
            ingredient = intent_data.get("ingredient", "")
            quantity = intent_data.get("quantity", "")
            return self.update_pantry(ingredient, quantity)
        elif action == "get_pantry":
            return self.get_pantry_items()
        elif action == "suggest_recipe":
            return self.suggest_recipe()
        else:
            return "Unknown meal planner action."


if __name__ == "__main__":
    import sys
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")

    engine = MealPlannerChef()
    print("Meal Planner Chef Engine Ready")
