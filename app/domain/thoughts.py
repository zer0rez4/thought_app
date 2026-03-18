class Thoughts():
    def __init__(self, thought_id: int, text: str, author: str, is_public: bool) -> None:
        self.thought_id = thought_id
        self.text = text
        self.author = author
        self.is_public = is_public

        