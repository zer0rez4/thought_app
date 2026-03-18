class User():
    def __init__(self, user_id: int, user_email: str, hashed_password: str) -> None:
        self.user_id = user_id
        self.user_email = user_email
        self.hashed_password = hashed_password
        self.is_active = True