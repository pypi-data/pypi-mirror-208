from typing import Dict, Any

import requests
import platform
import time
import sys

from cyclone.session import SessionManager
from posthog import Posthog

# production
# CYCLONE_BACKEND_URL = "https://ceaseless-caribou-99.convex.site/postUsage"

# dev, tonyyang's dev server
# without convexproxy
#CYCLONE_BACKEND_URL = "https://unwieldy-mule-395.convex.site/postUsage"
# with convexproxy
CYCLONE_BACKEND_URL = "https://convexproxy.usecyclone.dev/postUsage"

POSTHOG_HOST_URL = "https://ph.usecyclone.dev"
PROJECT_KEY = "phc_Belh475IYfPoF9bke7r9ReO3m7WIa21C5ftRvD10Pvs"

class CycloneClient:
    """
    {
        "version": <integer>, // rqeuired, protocol version
        "client": "SDK client identifier string", // optional
        "api_key": "public_api_key", // required for auth
        "project_id": "public project id", // required for auth
        "platform_type": "string", // required. "cli", "dev-server", "doc", "web", etc
        "timestamp": <unix_timestamp>, // optional, integer
        "metadata": { // everything here is optional
            "source": "string",
            "session_id": "string", // session cookie, dev server run attempt
            "user_id": "string", // link sessions with a shared user id
            "cli_command" :"string",
            "exception": "string",
        }
    }
    """

    def __init__(self, api_key, project_id, session_manager: SessionManager):
        self.session_manager = session_manager
        self.posthog = Posthog(api_key=PROJECT_KEY, project_api_key=PROJECT_KEY, host=POSTHOG_HOST_URL)
        self.posthog.debug = True
        self.json_template = {
            "version": 1,
            "client": "python_client_v0.1",
            "api_key": api_key,
            "project_id": project_id,
            "platform_type": "cli",
        }
        self.metadata_template = {
            "os": platform.platform(),
            "session_id": session_manager.get_session_id(),
            "machine_id": session_manager.get_machine_id(),
        }

    def _send_json(self, json: Dict[str, Any], timeout=0.5):
        try:
            source = json["metadata"]["source"]
        except KeyError:
            source = "unknown"

        if source == "os_signal":
            event_name = "os signal received"
        elif source == "argv":
            event_name = "argv recorded"
        else:
            event_name = source + " captured"

        # posthog.capture mutates the json passed in, so we make a copy before passing in
        posthog_json = dict(json)
        self.posthog.capture(self.session_manager.get_machine_id(), event_name, posthog_json)

        requests.post(CYCLONE_BACKEND_URL, json=json, timeout=timeout)

    def _get_payload_template(self):
        # make a copy
        json = dict(self.json_template)
        # we use millisceond timestamp
        json["timestamp"] = time.time() * 1000

        metadata = dict(self.metadata_template)
        if self.session_manager.get_custom_tracking_id() is not None:
            metadata["custom_tracking_id"] = self.session_manager.get_custom_tracking_id()

        json["metadata"] = metadata
        return json

    def send_cli(self, data: str, source_name: str):
        json = self._get_payload_template()
        metadata = json["metadata"]

        metadata["source"] = source_name
        metadata["data"] = data

        self._send_json(json)

    def send_argv(self):
        json = self._get_payload_template()
        metadata = json["metadata"]

        metadata["source"] = "argv"
        metadata["argv"] = sys.argv

        self._send_json(json)

    def send_signal(self, signal: str):
        json = self._get_payload_template()
        metadata = json["metadata"]

        metadata["source"] = "os_signal"
        metadata["signal"] = signal

        self._send_json(json)
