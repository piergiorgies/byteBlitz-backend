from datetime import timedelta
from datetime import datetime, timezone
from jose import jwt

SECRET_KEY = "9dc3c57a404979e84bc959b66c5f4ac134490ad58f602800cad268c01457dc9d"
ALGORITHM = "HS256"


def _create_access_token(data: dict = None, expires_delta: timedelta = None):
    # data is the payload of the token
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    
    return jwt.encode(to_encode, key=SECRET_KEY, algorithm=ALGORITHM)

def get_tokens(user_id, username, user_type):
    # Generate access token
    access_token_expire = timedelta(minutes=60)

    data = {
        "user_id": user_id,
        "sub": username,
        "user_type": user_type
    }

    access_token = _create_access_token(data=data, expires_delta=access_token_expire)

    return {
        "access_token": access_token
    }

admin_headers = {
    'Authorization': 'Bearer ' + get_tokens(2, 'admin', 'admin')["access_token"],
    'Content-Type': 'application/json'
}

user_headers = {
    'Authorization': 'Bearer ' + get_tokens(3, 'user', 'user')["access_token"],
    'Content-Type': 'application/json'
}

base_url = 'http://localhost:9000/'