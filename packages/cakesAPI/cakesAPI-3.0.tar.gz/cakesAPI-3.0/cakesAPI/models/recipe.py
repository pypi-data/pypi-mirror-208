class Recipe:
    def __init__(self, id, title, difficulty, portion, time, description, ingredients, method):
        self._id = id
        self._title = title
        self._difficulty = difficulty
        self._portion = portion
        self._time = time
        self._description = description
        self._ingredients = ingredients
        self._method = method

    def get_id(self):
        return self._id

    def get_title(self):
        return self._title

    def get_difficulty(self):
        return self._difficulty

    def get_portion(self):
        return self._portion

    def get_time(self):
        return self._time

    def get_description(self):
        return self._description

    def get_ingredients(self):
        return self._ingredients

    def get_method(self):
        return self._method
