import jwt


def extract_id(access_token: str):
    session_payload = jwt.decode(
        access_token, algorithms="HS256", options={"verify_signature": False}
    )
    id = session_payload["sub"]
    return id
