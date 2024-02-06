import csv
import io
import json

from fastapi import HTTPException, Request, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import PlainTextResponse


class CSVMiddleware(BaseHTTPMiddleware):
    nested_separator = "."

    def __init__(self, app, dispatch=None, nested_separator=".", **kwargs):
        super().__init__(app, dispatch)
        self.nested_separator = nested_separator

    async def dispatch(self, request: Request, call_next):
        if "text/csv" in request.headers.get("Content-Type", ""):
            try:
                # Read CSV data from request body
                csv_data = await request.body()
                csv_text = csv_data.decode("utf-8")

                # Convert CSV to JSON
                json_data = self.csv_to_json(csv_text)
                request._body = json_data.encode()

                headers = request.headers.mutablecopy()
                headers.__setitem__("content-type", "application/json")
                headers.__setitem__("content-length", f"{len(json_data)}")

                request._headers = headers
                request.scope.update(headers=request.headers.raw)
            except Exception as e:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
                )

        response = await call_next(request)

        if "text/csv" in request.headers.get("Accept", ""):
            response_body = b""
            async for chunk in response.body_iterator:
                response_body += chunk
            content = self.json_to_csv(response_body.decode()).encode()
            headers = dict(response.headers)
            headers.update({"content-length": str(len(content))})
            headers.update({"Content-Type": "text/csv"})
            return PlainTextResponse(
                content=content,
                status_code=response.status_code,
                headers=headers,
                media_type="text/csv",
            )

        return response

    @staticmethod
    def csv_to_json(csv_text: str) -> str:
        # Assuming CSV has header row
        csv_reader = csv.DictReader(io.StringIO(csv_text))
        body = list(csv_reader)
        if len(body) == 1:
            body = body[0]
        return json.dumps(body)

    def flatten_list_of_dicts(self, data):
        def flatten_dict(d, parent_key=""):
            items = []
            for k, v in d.items():
                new_key = f"{parent_key}{self.nested_separator}{k}" if parent_key else k
                if isinstance(v, dict):
                    items.extend(flatten_dict(v, new_key).items())
                else:
                    items.append((new_key, v))
            return dict(items)

        if isinstance(data, dict):
            data = [data]
        return [flatten_dict(d) for d in data]

    def json_to_csv(self, json_text: str) -> str:
        if not json_text:
            return ""
        body = json.loads(json_text)
        if not body:
            return ""

        body = self.flatten_list_of_dicts(body)

        output = io.StringIO()
        headers = list(dict.fromkeys(k for b in body for k in b.keys()))
        writer = csv.DictWriter(
            output, quoting=csv.QUOTE_NONNUMERIC, fieldnames=headers
        )
        writer.writeheader()
        writer.writerows(body)

        return output.getvalue()
