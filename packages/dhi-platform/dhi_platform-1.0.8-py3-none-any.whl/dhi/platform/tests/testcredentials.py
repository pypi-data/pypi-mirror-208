from dhi.platform.authentication import ApiKeyIdentity, InteractiveIdentity
import os

TEST_ENVIRONMENT = os.environ.get("TESTENVIRONMENTTARGET", "prod")

TEST_CUSTOMER_ID = None # "TODO: provide valid customer id"

TEST_API_KEY = os.environ.get("OPENAPIKEY") # "TODO: provide valid api key"

if TEST_API_KEY is None:
    TEST_IDENTITY = InteractiveIdentity(environment=TEST_ENVIRONMENT)
else:
    TEST_IDENTITY = ApiKeyIdentity(customer_id=TEST_CUSTOMER_ID, apikey=TEST_API_KEY, environment=TEST_ENVIRONMENT)
