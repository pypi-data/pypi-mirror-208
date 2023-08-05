# PeachPayments Partner Pydantic Library

## Overview

**PeachPayments Partner Pydantic Library** is a platform-agnostic Python package to help Payment Service Providers in integrating with PeachPayments. This library provides functionality to validate request and response data using Pydantic Python library.

**Source Code**: <https://gitlab.com/peachpayments/peach-partner-pydantic/>

* * *

### Key terms

| Term                     | Definition                                                                                                         |
| ------------------------ | ------------------------------------------------------------------------------------------------------------------ |
| Partner API              | A service provided by Peach Payments to enable Payment Service Providers to become available on the Peach Platform |
| Payment Service Provider | A payment service provider who integrates with the Partner API                                                     |
| Outbound API call        | API calls sent from Partner API to the Payment Service Provider                                                    |
| Inbound API call         | API calls sent from Payment Service Provider to Partner API                                                        |

## Usage

Package requires Python 3.9+

### Installation

```sh
# pip
$ pip3 install peachpayments-partner-pydantic
```

```sh
# poetry
$ poetry add peachpayments-partner-pydantic
```

### Field validation

**Scenario:** Payment Service Provider written in FastAPI receives a debit request from PeachPayments.

```python
# ... imports
from peachpayments_partner_pydantic.schemas import DebitRequest, DebitResponse

@router.post(
    "/v1/debit",
    response_model=schemas.DebitResponse,
)
def debit_request(
    *, debit_in: schemas.DebitRequest
) -> Any:
    # Store the transaction
    transaction = Transaction.create_from_debit(debit_in)
    # Validate the debit response
    debit_response = DebitResponse(**transaction.to_debit_response_fields())
    return debit_response.dict()
```

### Translating exception to PeachPayments error response

**Scenario:** Payment Service Provider written in FastAPI receives a request with a validation error from PeachPayments.

#### 1. Write validation exception handler

```python
# app/exception_handlers.py
from fastapi import Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from peachpayments_partner_pydantic.exception_handlers import exception_to_response

async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=exception_to_response(exc))
```

#### 2. Connect it to the application

```python
# app/main.py
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from app.exception_handlers import validation_exception_handler

application = FastAPI(
    exception_handlers={RequestValidationError: validation_exception_handler},
)
```
