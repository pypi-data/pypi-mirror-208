## Elefantolib for FastAPI

> **_NOTE:_**  Only for this library developers. After clone this repository you should run command:
> 

 ```console 
git config core.hooksPath .githooks
```


## Installation

<div class="termy">

```console
poetry add elefantolib-fastapi
```
</div>

## Example

### Prepare

* Add environmental variables

```
SECRET=
ALGORITHM=
ISSUER=
```
* Defaults:
    
    - SECRET - not set, this is required
    - ALGORITHM=HS256
    - ISSUER=Consumer

### Create it

* Create a file `main.py` with:

```Python
from elefantolib_fastapi.requests import Request
from elefantolib_fastapi.routes import APIRoute

from fastapi import FastAPI

app = FastAPI()

app.router.route_class = APIRoute


@app.get('/')
def index(request: Request):
    # TODO something
    response = request.pfm.services.some_service_name.get('path-to-endpoint')
    return response

```