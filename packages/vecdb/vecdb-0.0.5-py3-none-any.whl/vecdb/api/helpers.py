from vecdb import types


def process_token(token: str) -> types.Credentials:
    return types.Credentials(*token.split(":"))
