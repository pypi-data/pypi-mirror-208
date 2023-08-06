import os
RELEVANCE_AUTH_TOKEN = os.getenv("RELEVANCE_AUTH_TOKEN")
if not RELEVANCE_AUTH_TOKEN:
    raise KeyError("'RELEVANCE_AUTH_TOKEN' needs to be set as an environmental variable. This token can be found on https://cloud.relevanceai.com/sdk/api")