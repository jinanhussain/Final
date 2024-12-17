from builtins import bool, int, str
from pathlib import Path
from pydantic import Field, AnyUrl, DirectoryPath
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # General settings
    debug: bool = Field(default=False, description="Enable debug mode for development")
    max_login_attempts: int = Field(default=3, description="Maximum allowed login attempts before lockout")

    # Server configuration
    server_base_url: AnyUrl = Field(default="http://localhost", description="Base URL of the server")
    server_download_folder: str = Field(default="downloads", description="Folder for storing downloaded files")

    # Security and Authentication
    secret_key: str = Field(..., description="Secret key for encryption")  # Required
    algorithm: str = Field(default="HS256", description="JWT algorithm for encoding tokens")
    jwt_secret_key: str = Field(default="a_very_secret_key", description="JWT secret key for signing")
    jwt_algorithm: str = Field(default="HS256", description="JWT algorithm")
    access_token_expire_minutes: int = Field(default=15, description="Access token expiration time in minutes")
    refresh_token_expire_minutes: int = Field(default=1440, description="Refresh token expiration time in minutes")

    # Default admin credentials
    admin_user: str = Field(default="admin", description="Default admin username")
    admin_password: str = Field(default="secret", description="Default admin password")

    # Database Configuration
    database_url: str = Field(..., description="Database connection URL")  # Required
    postgres_user: str = Field(default="user", description="PostgreSQL username")
    postgres_password: str = Field(default="password", description="PostgreSQL password")
    postgres_server: str = Field(default="localhost", description="PostgreSQL server address")
    postgres_port: int = Field(default=5432, description="PostgreSQL port")
    postgres_db: str = Field(default="myappdb", description="PostgreSQL database name")

    # Email Configuration (Mailtrap)
    smtp_server: str = Field(default="smtp.mailtrap.io", description="SMTP server for sending emails")
    smtp_port: int = Field(default=2525, description="SMTP server port")
    smtp_username: str = Field(..., description="SMTP username")  # Required
    smtp_password: str = Field(..., description="SMTP password")  # Required
    send_real_mail: bool = Field(default=False, description="Send real emails or use mock emails")

    # Discord Configuration (Optional)
    discord_bot_token: str = Field(default="NONE", description="Discord bot token")
    discord_channel_id: int = Field(default=1234567890, description="Discord channel ID for notifications")

    # OpenAI Key Configuration (Optional)
    openai_api_key: str = Field(default="NONE", description="OpenAI API Key for AI integration")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

# Instantiate the settings object
settings = Settings()
