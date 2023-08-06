import json
import asyncio

from enum import Enum
from aioinsta import login
from aioinsta.exceptions import ChallengeError


class ChallengeChoice(Enum):
    SMS = 0
    EMAIL = 1


def manual_input_code(username: str, choice=None):
    code = None
    while True:
        code = input(f"Enter code (6 digits) for {username} ({choice}): ").strip()
        if code and code.isdigit():
            break
    return code


def manual_change_password(username: str):
    pwd = None
    while not pwd:
        pwd = input(f"Enter password for {username}: ").strip()
    return pwd


class ChallengeClient:
    def __init__(self, login_client: "login.Login"):
        self.login_client = login_client

    async def resolve_challenge(self, last_json: dict):
        challenge_url = last_json["challenge"]["api_path"]
        try:
            user_id, nonce_code = challenge_url.split("/")[2:4]
            challenge_context = last_json.get("challenge", {}).get("challenge_context")
            if not challenge_context:
                challenge_context = json.dumps(
                    {
                        "step_name": "",
                        "nonce_code": nonce_code,
                        "user_id": int(user_id),
                        "is_stateless": False,
                    }
                )
            params = {
                "guid": self.login_client.uuid,
                "device_id": self.login_client.android_device_id,
                "challenge_context": challenge_context,
            }
        except ValueError:
            params = {}
        response = await self.login_client.private_request(
            method="GET",
            path=challenge_url[1:],
            params=params,
        )
        return await self.challenge_resolve_simple(challenge_url)

    async def challenge_resolve_simple(self, challenge_url: str) -> bool:
        step_name = self.login_client.last_response.get("step_name", "")
        print(self.login_client.last_response)
        if step_name == "delta_login_review" or step_name == "scraping_warning":
            await self.login_client.private_request(
                method="POST",
                path=challenge_url,
                data={"choice": "0"}
            )
            return True
        elif step_name in ("verify_email", "select_verify_method"):
            if step_name == "select_verify_method":
                steps = self.login_client.last_response["step_data"].keys()
                challenge_url = challenge_url[1:]
                if "email" in steps:
                    await self.login_client.private_request(
                        method="POST",
                        path=challenge_url,
                        data={"choice": ChallengeChoice.EMAIL}
                    )
                elif "phone_number" in steps:
                    await self.login_client.private_request(
                        method="POST",
                        path=challenge_url,
                        data={"choice": ChallengeChoice.SMS}
                    )
                else:
                    raise ChallengeError(
                        f'ChallengeResolve: Choice "email" or "phone_number" (sms) not available to this account'
                    )
            wait_seconds = 5
            code = None
            attempt = 0
            for attempts in range(24):
                attempt += 1
                code = manual_input_code(self.login_client.username, ChallengeChoice.EMAIL)
                if code:
                    break
                await asyncio.sleep(wait_seconds)
            print(
                f'Code entered "{code}" for {self.login_client.username} ({attempt} attempts by {wait_seconds} seconds)'
            )
            await self.login_client.private_request(
                method="POST",
                path=challenge_url,
                data={"security_code": code}
            )
            # assert 'logged_in_user' in client.last_json
            assert self.login_client.last_response.get("action", "") == "close"
            assert self.login_client.last_response.get("status", "") == "ok"
            return True
        elif step_name == "":
            assert self.login_client.last_response.get("action", "") == "close"
            assert self.login_client.last_response.get("status", "") == "ok"
            return True
