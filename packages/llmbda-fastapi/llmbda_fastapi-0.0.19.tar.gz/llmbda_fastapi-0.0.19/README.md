# Llmbda FastAPI

## Add your fastapi endpoints to your Relevance Notebook for chaining.
1. Install:
```
pip install llmbda_fastapi
```

2. Set your Relevance Auth Token from cloud.relevanceai.com/sdk/api:
```
SET RELEVANCE_AUTH_TOKEN=xxx
```
or
```
export RELEVANCE_AUTH_TOKEN=xxx
```

3. Include these 2 lines of code:
```
PUBLIC_URL = "https://whereyourapiishosted.com/"

from fastapi import FastAPI
app = FastAPI()

from llmbda_fastapi import create_transformations
create_transformations(app.routes, PUBLIC_URL)
```

If you are working off a local computer you can use ngrok to create a public url:
```
pip install pyngrok
```

```
from fastapi import FastAPI
app = FastAPI()

#add this for ngrok
from pyngrok import ngrok
PUBLIC_URL = ngrok.connect(8000).public_url

#add this
from llmbda_fastapi import create_transformations
create_transformations(app.routes, PUBLIC_URL)
```

4. Add these options to your existing api endpoints, for example this is a endpoint to "Run code in your local environment"

```
from fastapi import APIRouter, Query
from pydantic import BaseModel
from llmbda_fastapi.frontend import input_components

router = APIRouter()

#Optionally specify frontend_component to make this input be displayed as a specific frontend component
class ExecuteCodeParams(BaseModel):
    code : str = Query(..., description="Code to run", frontend=input_components.LongText())
    #the name and description of this will be automatically picked up and displayed in the notebook

class ExecuteCodeResponseParams(BaseModel):
    results : str = Query(" ", description="Return whats printed by the code")

# This is the actual transformation
def evaluate_code(code):
    print("Executing code: " + code)
    output = eval(code)
    print(output)
    return {"results" : str(output)}

# This is the API endpoint for the transformation
# The name and description of this will be automatically picked up and displayed in the notebook. Make sure to set response_model and query parameters if they are required.
@router.post("/run_code", name="Run Code", description="Run Code Locally - Test", tags=["coding"], response_model=ExecuteCodeResponseParams)
def run_code_api(commons: ExecuteCodeParams):
    return evaluate_code(commons.code)
```