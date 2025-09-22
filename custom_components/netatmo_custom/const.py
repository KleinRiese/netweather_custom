DOMAIN = "netatmo_custom"
CONF_CLIENT_ID = "client_id"
CONF_CLIENT_SECRET = "client_secret"
CONF_REFRESH_TOKEN = "refresh_token"

TOKEN_URL = "https://api.netatmo.com/oauth2/token"
STATIONS_URL = "https://api.netatmo.com/api/getstationsdata?get_favorites=true"

UPDATE_INTERVAL_SECONDS = 300  # 5 Minuten
PLATFORMS = ["sensor"]