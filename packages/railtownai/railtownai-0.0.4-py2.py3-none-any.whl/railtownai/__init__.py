#   -------------------------------------------------------------
#   Copyright (c) Railtown AI. All rights reserved.
#   Licensed under the MIT License. See LICENSE in project root for information.
#   -------------------------------------------------------------
"""Railtown AI Python SDK for tracking errors and exceptions in your Python applications"""
from __future__ import annotations
from pydantic import BaseModel, validator
import base64
import json
import requests
import datetime

railtown_api_key: str = None


class RailtownPayload(BaseModel):
    Message: str
    Level: str
    OrganizationId: str
    ProjectId: str
    EnvironmentId: str
    Runtime: str
    Exception: str
    TimeStamp: str
    Properties: dict

    @validator("Level")
    def level_must_be_info_error_warning_critical(cls, v):
        if v not in ["info", "error", "warning", "critical"]:
            raise ValueError("Level must be one of: info, error, warning, critical")
        return v


def init(token: str):
    global railtown_api_key
    railtown_api_key = token


def get_config() -> dict:
    try:
        global railtown_api_key

        if (railtown_api_key is None) or (railtown_api_key == ""):
            raise Exception("Invalid Railtown AI API Key: Ensure you call init(railtown_api_key)")

        token_base64_bytes = railtown_api_key.encode("ascii")
        token_decoded_bytes = base64.b64decode(token_base64_bytes)
        token_json = token_decoded_bytes.decode("ascii")
        jwt = json.loads(token_json)

        if "u" not in jwt:
            raise Exception("Invalid Railtown AI API Key: host is required")
        elif "o" not in jwt:
            raise Exception("Invalid Railtown AI API Key: organization_id is required")
        elif "p" not in jwt:
            raise Exception("Invalid Railtown AI API Key: project_id is required")
        elif "h" not in jwt:
            raise Exception("Invalid Railtown AI API Key: secret is required")
        elif "e" not in jwt:
            raise Exception("Invalid Railtown AI API Key: environment_id is required")

        return jwt
    except Exception as e:
        raise Exception("Invalid Railtown AI API Key: Ensure to copy it from your Railtown Project") from e


def log(error, *args, **kwargs):
    print(error, *args, **kwargs)
    print(get_full_stack_trace())

    config = get_config()
    stack_trace = get_full_stack_trace()

    payload = [
        {
            "Body": str(
                RailtownPayload(
                    Message=str(error),
                    Level="error",
                    Exception=stack_trace,
                    OrganizationId=config["o"],
                    ProjectId=config["p"],
                    EnvironmentId=config["e"],
                    Runtime="python",
                    TimeStamp=datetime.datetime.now().isoformat(),
                    Properties=kwargs,
                ).dict()
            ),
            "UserProperties": {
                "AuthenticationCode": config["h"],
                "ClientVersion": "Python-0.0.2",
                "Encoding": "utf-8",
                "ConnectionName": config["u"],
            },
        }
    ]

    requests.post(
        "https://" + config["u"],
        headers={"Content-Type": "application/json", "User-Agent": "railtown-py(python)"},
        json=payload,
    )


def get_full_stack_trace():
    import traceback, sys

    exc = sys.exc_info()[0]
    stack = traceback.extract_stack()[:-1]  # last one would be full_stack()
    if exc is not None:  # i.e. an exception is present
        del stack[-1]  # remove call of full_stack, the printed exception
        # will contain the caught exception caller instead
    trc = "Traceback (most recent call last):\n"
    stackstr = trc + "".join(traceback.format_list(stack))
    if exc is not None:
        stackstr += "  " + traceback.format_exc().lstrip(trc)
    return stackstr


__version__ = "0.0.4"
