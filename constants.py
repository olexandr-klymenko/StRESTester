PROJECT = 'StressTester'

URLS = 'urls'
USERS_NUMBER = 'users_number'
ITERATIONS_NUMBER = 'iterations_number'
WORKERS_NUMBER = 'workers_number'
MANDATORY_CONFIG_FIELDS = (URLS, USERS_NUMBER, ITERATIONS_NUMBER, WORKERS_NUMBER)

BLUEPRINTS_INFO = 'blueprints_info'
TEST_USER_NAME = 'st_user'
TEST_USER_PASSWORD = '123'

RETURN = 'return'
REPEAT = 'repeat'
CYCLES = 'cycles'

MAX_RETRY = 10
RETRY_DELAY = 1  # seconds
REST_REQUEST_TIMEOUT = 10  # sec

REQUEST_ARGS = ['url', 'method', 'data', 'params', 'headers']
SERIALIZABLE_ARGS = ['data', 'params', 'headers']

ST_CONFIG_PATH = 'ST_CONFIG_PATH'
