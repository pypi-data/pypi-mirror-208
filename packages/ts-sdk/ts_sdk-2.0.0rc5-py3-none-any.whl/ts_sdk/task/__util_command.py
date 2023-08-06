import time
from datetime import datetime, timedelta, timezone

import requests
import simplejson as json

from ts_sdk.task.__util_adapters import (
    CommunicationFormat,
    select_versioned_value,
)
from ts_sdk.task.__util_adapters.endpoint_adapter import get_public_endpoint


def get_command_url():
    return select_versioned_value(
        {
            CommunicationFormat.V0: lambda: get_public_endpoint("COMMAND_ENDPOINT")
            + "/internal",
            CommunicationFormat.V1: lambda: get_public_endpoint("KERNEL_ENDPOINT")
            + "/v1/commands",
        }
    )()


def run_command(context_data, org_slug, target_id, action, metadata, payload, ttl_sec):
    if org_slug is None:
        raise Exception("Param org_slug is missing")
    if target_id is None:
        raise Exception("Param target_id is missing")
    if action is None:
        raise Exception("Param action is missing")
    if payload is None:
        raise Exception("Param payload is missing")
    if ttl_sec < 300 or ttl_sec > 900:
        raise Exception("Param ttl_sec must be between 300 and 900 seconds")

    if metadata is None:
        metadata = {}

    metadata["workflowId"] = context_data.get("workflowId")
    metadata["pipelineId"] = context_data.get("pipelineId")
    metadata["taskId"] = context_data.get("taskId")

    url = get_command_url()
    date_now = datetime.now(timezone.utc) + timedelta(0, ttl_sec)

    command_create_payload = {
        "targetId": target_id,
        "action": action,
        "metadata": metadata,
        "expiresAt": date_now.isoformat(),
        "payload": payload,
    }

    headers = {"x-org-slug": org_slug, "Content-Type": "application/json"}

    response = requests.post(
        url,
        headers=headers,
        data=json.dumps(command_create_payload),
        verify=False,
    )
    if response.status_code == 200:
        print("Command successfully created")
        r = json.loads(response.text)
        command_id = r.get("id")

        command_url = get_command_url() + "/" + command_id
        command_headers = {"x-org-slug": org_slug}

        time_elapsed = 0
        while time_elapsed <= ttl_sec:
            time.sleep(1)
            time_elapsed += 1
            command_response = requests.get(
                command_url, headers=command_headers, verify=False
            )
            print("Polling for command status")
            if command_response.status_code == 200:
                command = json.loads(command_response.text)
                command_status = command.get("status")
                print("Current command status: " + command_status)
                if command_status == "SUCCESS":
                    return command.get("responseBody")
                elif (
                    command_status == "CREATED"
                    or command_status == "PENDING"
                    or command_status == "PROCESSING"
                ):
                    continue
                else:
                    raise Exception(command.get("responseBody"))

        if time_elapsed >= ttl_sec:
            print("TTL for command has expired")
            raise Exception("Command TTL has expired")
    else:
        print("Error creating command: " + response.text)
        raise Exception(response.text)

    return response
