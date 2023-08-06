class Cake:
    def __init__(self, id, title, difficulty, image):
        self._id = id
        self._title = title
        self._difficulty = difficulty
        self.image = image

    def get_id(self):
        return self._id

    def get_title(self):
        return self._title

    def get_difficulty(self):
        return self._difficulty

    def get_image(self):
        return self.image
