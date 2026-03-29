class Thoughts():
    def __init__(self, thought_id: int, text: str, author_id: int, is_public: bool) -> None:
        self.thought_id = thought_id
        self.text = text
        self.author_id = author_id
        self.is_public = is_public

        