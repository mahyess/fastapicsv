## FastAPI CSV Middleware

This is a simple middleware for FastAPI that allows you to upload CSV files and parse them into a list of dictionaries.

I've explained a bit more in [this blog post here](https://blog.zephyrr.me/using-csv-middleware-in-fastapi/).

### Installation

```bash
pip install fast-csv-middleware
```

### Usage

```python
from fastapi import FastAPI
from fastapicsv import CSVMiddleware

app = FastAPI()

app.add_middleware(CSVMiddleware)
```

### Testing

#### Request Body

Use `Content-Type=text/csv` in request headers when sending `csv` text in request body.

#### Response Body

Use `Accept=text/csv` in request headers to receive `csv` text in response body.
