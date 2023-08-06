# from . import Word


class IDGenerator:
    __instance = None

    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = object.__new__(cls)
            cls.__instance.id = 0
        return cls.__instance

    def generate_id(self):
        id_value = self.id
        self.id += 1
        return id_value


def get_average_character_height(words) -> float:
    """Get the average size of a list of words."""
    if not words:
        return 0
    heights = [word.bounding_box.get_height() for word in words]
    return sum(heights) / len(heights)


def get_average_character_width(words) -> float:
    if not words:
        return 0
    avg_char_widths = [
        word.bounding_box.get_width() / len(word) for word in words
    ]
    return sum(avg_char_widths) / len(avg_char_widths)
