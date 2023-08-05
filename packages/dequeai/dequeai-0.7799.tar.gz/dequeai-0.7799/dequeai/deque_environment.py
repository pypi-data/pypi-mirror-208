import os

AGENT_API_SERVICE_URL = 'https://apis.deque.app'
api_environment = os.getenv("DEQUE_API_ENVIRONMENT")
REDIS_URL = "redis://localhost:6379"
if api_environment is not None and api_environment.lower() == "staging":

    AGENT_API_SERVICE_URL = 'https://apis-staging.deque.app'


else:

    AGENT_API_SERVICE_URL = 'https://apis.deque.app'



