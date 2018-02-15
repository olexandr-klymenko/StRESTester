PROJECT = 'StRESTester'

NAME = 'name'
URLS = 'urls'
ITERATIONS_NUMBER = 'iterations_number'
WORKERS_NUMBER = 'workers_number'
MANDATORY_CONFIG_FIELDS = (URLS,
                           ITERATIONS_NUMBER,
                           WORKERS_NUMBER)

BLUEPRINTS_INFO = 'blueprints_info'
TEST_USER_NAME = 'st_user'
TEST_USER_PASSWORD = '123'

REST = 'rest'
RETURN = 'return'
IGNORE_ERRORS = 'ignore_errors'
REPEAT = 'repeat'
CYCLES = 'cycles'
SKIP_METRIC = 'skip_metric'

MAX_RETRY = 100
RETRY_DELAY = 1  # seconds
DEFAULT_REST_REQUEST_TIMEOUT = 1  # sec

REQUEST_ARGS = ['url', 'method', 'data', 'params', 'headers']
SERIALIZABLE_ARGS = ['data', 'params', 'headers']

ST_CONFIG_PATH = 'ST_CONFIG_PATH'
