import secrets
import string


def base62(n_char: int) -> str:
    """Like nanoid without hyphen and underscore."""
    alphabet = string.digits + string.ascii_letters.swapcase()
    id = "".join(secrets.choice(alphabet) for i in range(n_char))
    return id


def secret() -> str:
    """Password or secret: 40 base62."""
    return base62(n_char=40)
