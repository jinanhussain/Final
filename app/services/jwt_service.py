# app/services/jwt_service.py
from builtins import dict, str
import jwt
from datetime import datetime, timedelta
from settings.config import settings

# Function to create access token
def create_access_token(*, data: dict, expires_delta: timedelta = None):
    """
    Generate a JWT access token.

    Args:
        data (dict): Payload to encode in the JWT.
        expires_delta (timedelta): Expiration time for the token. Defaults to config settings.

    Returns:
        str: Encoded JWT token.
    """
    to_encode = data.copy()

    # Ensure role is in uppercase for consistency
    if 'role' in to_encode:
        to_encode['role'] = to_encode['role'].upper()

    # Set expiration
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=settings.access_token_expire_minutes))
    to_encode.update({"exp": expire})

    # Encode the JWT
    encoded_jwt = jwt.encode(to_encode, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)
    return encoded_jwt

# Function to create refresh token
def create_refresh_token(*, data: dict, expires_delta: timedelta = None):
    """
    Generate a JWT refresh token.

    Args:
        data (dict): Payload to encode in the JWT.
        expires_delta (timedelta): Expiration time for the refresh token.

    Returns:
        str: Encoded JWT refresh token.
    """
    to_encode = data.copy()

    # Set expiration
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=settings.refresh_token_expire_minutes))
    to_encode.update({"exp": expire})

    # Encode the JWT
    encoded_jwt = jwt.encode(to_encode, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)
    return encoded_jwt

# Function to decode token
def decode_token(token: str):
    """
    Decode a JWT token.

    Args:
        token (str): The JWT token to decode.

    Returns:
        dict: Decoded payload if the token is valid.
        None: If the token is invalid or expired.
    """
    try:
        decoded = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
        return decoded
    except jwt.ExpiredSignatureError:
        print("Token has expired.")
        return None
    except jwt.InvalidTokenError:
        print("Token is invalid.")
        return None
