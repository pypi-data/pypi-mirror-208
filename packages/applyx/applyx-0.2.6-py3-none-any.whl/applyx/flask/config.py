# coding=utf-8

SERVER_NAME = None
SECRET_KEY = "you-never-guess"
REQUEST_LOG_FORMAT = "[{time:YYYY-MM-DD HH:mm:ss,SSS}][{level}][{process},{thread}][{extra[mdc]}] {message}"

JSON_AS_ASCII = False
JSON_SORT_KEYS = True
JSONIFY_PRETTYPRINT_REGULAR = True
JSONIFY_MIMETYPE = "application/json"

ENABLE_GZIP = False
ENABLE_CORS = False
CORS_WHITELIST_DOMAINS = ["*"]
ACCESS_CONTROL_MAX_AGE = 60

STATIC_DIR = "./static"
TEMPLATE_FOLDER = "templates"

SESSION_COOKIE_NAME = "sessionid"
SESSION_COOKIE_DOMAIN = None
SESSION_COOKIE_HTTPONLY = True  # access denied from js
SESSION_COOKIE_SECURE = False  # visible only for https
PERMANENT_SESSION_LIFETIME = 60 * 60 * 24 * 30  # expire after 30 days

# # https://pythonhosted.org/Flask-Session/
# SESSION_TYPE = 'redis'
# SESSION_REDIS_ALIAS = 'session'
# SESSION_KEY_PREFIX = 'session:'
# SESSION_PERMANENT = True
# SESSION_USE_SIGNER = False
