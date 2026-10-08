def validate_password(password: str) -> str:
    if not password.strip():
        raise ValueError('The password can not be empty')
    return password