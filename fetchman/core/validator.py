#! /usr/bin/python3

import json
from typing import Optional, Any, Literal
from pydantic import BaseModel, HttpUrl, model_validator

HTTPMethods = Literal["GET", "POST", "PUT", "PATCH", "DELETE", "QUERY"]

supported_methods_list: list[str] = ["GET", "POST", "PUT", "PATCH", "DELETE", "QUERY"]
send_payload_methods_list: list[str] = ["POST", "PUT", "PATCH", "QUERY"]

class RequestModel(BaseModel):
    url: HttpUrl
    method: HTTPMethods
    payload: Optional[dict[str, Any]] = None
    headers: Optional[dict[str, str]] = None

    @model_validator(mode="after")
    def block_request_body_on_non_body_methods(self) -> "RequestModel":
        if self.payload and self.method not in supported_methods_list:
            raise ValueError(f"{self.method} is not supported by FetchMan")
        return self

def parse_raw_payload_data(raw_data: str) -> dict[str, Any]:
    try:
        parsed_data = json.loads(raw_data.strip())
        if not isinstance(parsed_data, dict):
            raise ValueError("Payload must be a JSON object")
        return parsed_data
    except json.JSONDecodeError as error:
        raise ValueError(f"Invalid JSON — {error}")

def validate_request(
    url: str,
    method: str,
    raw_payload: Optional[str] = None,
    headers: Optional[dict[str, str]] = None,
) -> RequestModel:
    parsed_payload_data = parse_raw_payload_data(raw_payload) if raw_payload and raw_payload.strip() else None
    return RequestModel(url=url, method=method.upper(), payload=parsed_payload_data, headers=headers)

def supported_methods() -> list[str]:
    return supported_methods_list


def send_payload_methods() -> list[str]:
    return send_payload_methods_list

