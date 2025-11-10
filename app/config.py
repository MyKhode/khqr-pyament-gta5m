from pydantic import BaseSettings


class Settings(BaseSettings):
    BAKONG_DEV_TOKEN: str
    BAKONG_MERCHANT_NAME: str = "Example Merchant"
    BAKONG_MERCHANT_CITY: str = "Phnom Penh"
    BAKONG_APP_NAME: str = "Example App"
    BAKONG_APP_ICON_URL: str = "https://example.com/icon.png"
    BAKONG_CALLBACK_URL: str = "example.com/callback"
    BAKONG_PHONE_NUMBER: str = "+85512345678"
    BAKONG_DEFAULT_CURRENCY: str = "USD"

    class Config:
        env_file = ".env"


settings = Settings()
