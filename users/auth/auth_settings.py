from authx import AuthX, AuthXConfig

config = AuthXConfig()
config.JWT_ALGORITHM = "HS512"
config.JWT_SECRET_KEY = "12201222Sajison1222!11QQqq!!T95E42012Artur"
config.JWT_TOKEN_LOCATION = ["cookies"]
config.JWT_COOKIE_CSRF_PROTECT = False


security = AuthX(config=config)