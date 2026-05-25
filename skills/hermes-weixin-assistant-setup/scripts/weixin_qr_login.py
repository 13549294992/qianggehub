#!/usr/bin/env python3
"""Generate a Weixin/iLink QR login for Hermes and save credentials locally.

This helper intentionally does not print tokens. It writes QR/status files to
the chosen output directory and saves confirmed credentials through Hermes'
own config helpers.
"""

from __future__ import annotations

import asyncio
import json
import os
import sys
import time
from pathlib import Path


HERMES_AGENT_DIR = os.environ.get(
    "HERMES_AGENT_DIR",
    r"C:\Users\Administrator\AppData\Local\hermes\hermes-agent",
)
sys.path.insert(0, HERMES_AGENT_DIR)

from hermes_constants import get_hermes_home  # noqa: E402
from hermes_cli.gateway import get_env_value, save_env_value  # noqa: E402
from gateway.platforms.weixin import (  # noqa: E402
    EP_GET_BOT_QR,
    EP_GET_QR_STATUS,
    ILINK_BASE_URL,
    QR_TIMEOUT_MS,
    _api_get,
    _make_ssl_connector,
    save_weixin_account,
)


async def main() -> int:
    import aiohttp
    import qrcode

    output_dir = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    qr_png = output_dir / "weixin_qr.png"
    qr_json = output_dir / "weixin_qr.json"
    status_json = output_dir / "weixin_status.json"
    result_json = output_dir / "weixin_result.json"

    def write_status(payload: dict) -> None:
        payload["updated_at"] = time.strftime("%Y-%m-%d %H:%M:%S")
        status_json.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    async with aiohttp.ClientSession(trust_env=True, connector=_make_ssl_connector()) as session:
        qr_resp = await _api_get(
            session,
            base_url=ILINK_BASE_URL,
            endpoint=f"{EP_GET_BOT_QR}?bot_type=3",
            timeout_ms=QR_TIMEOUT_MS,
        )

        qrcode_value = str(qr_resp.get("qrcode") or "")
        qrcode_url = str(qr_resp.get("qrcode_img_content") or "")
        if not qrcode_value:
            write_status({"status": "failed", "message": "QR response missing qrcode"})
            return 2

        qr_scan_data = qrcode_url if qrcode_url else qrcode_value
        img = qrcode.make(qr_scan_data)
        img.save(qr_png)
        qr_json.write_text(
            json.dumps(
                {
                    "qrcode_url": qrcode_url,
                    "qr_png": str(qr_png),
                    "started_at": time.strftime("%Y-%m-%d %H:%M:%S"),
                },
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )
        write_status({"status": "waiting_for_scan", "qr_png": str(qr_png)})

        deadline = time.monotonic() + 480
        current_base_url = ILINK_BASE_URL
        while time.monotonic() < deadline:
            try:
                status_resp = await _api_get(
                    session,
                    base_url=current_base_url,
                    endpoint=f"{EP_GET_QR_STATUS}?qrcode={qrcode_value}",
                    timeout_ms=QR_TIMEOUT_MS,
                )
            except Exception as exc:
                write_status({"status": "poll_error", "message": str(exc), "qr_png": str(qr_png)})
                await asyncio.sleep(1)
                continue

            status = str(status_resp.get("status") or "wait")
            if status == "wait":
                write_status({"status": "waiting_for_scan", "qr_png": str(qr_png)})
            elif status == "scaned":
                write_status({"status": "scanned_waiting_confirm", "qr_png": str(qr_png)})
            elif status == "scaned_but_redirect":
                redirect_host = str(status_resp.get("redirect_host") or "")
                if redirect_host:
                    current_base_url = f"https://{redirect_host}"
                write_status({"status": "scanned_redirecting", "qr_png": str(qr_png)})
            elif status == "expired":
                write_status({"status": "expired", "message": "QR expired. Restart login."})
                return 3
            elif status == "confirmed":
                account_id = str(status_resp.get("ilink_bot_id") or "")
                token = str(status_resp.get("bot_token") or "")
                base_url = str(status_resp.get("baseurl") or ILINK_BASE_URL)
                user_id = str(status_resp.get("ilink_user_id") or "")
                if not account_id or not token:
                    write_status({"status": "failed", "message": "Confirmed but missing account/token"})
                    return 4

                hermes_home = str(get_hermes_home())
                save_weixin_account(
                    hermes_home,
                    account_id=account_id,
                    token=token,
                    base_url=base_url,
                    user_id=user_id,
                )
                save_env_value("WEIXIN_ACCOUNT_ID", account_id)
                save_env_value("WEIXIN_TOKEN", token)
                save_env_value("WEIXIN_BASE_URL", base_url)
                save_env_value(
                    "WEIXIN_CDN_BASE_URL",
                    get_env_value("WEIXIN_CDN_BASE_URL") or "https://novac2c.cdn.weixin.qq.com/c2c",
                )
                save_env_value("WEIXIN_DM_POLICY", "allowlist")
                save_env_value("WEIXIN_ALLOW_ALL_USERS", "false")
                save_env_value("WEIXIN_ALLOWED_USERS", user_id)
                save_env_value("WEIXIN_GROUP_POLICY", "disabled")
                save_env_value("WEIXIN_GROUP_ALLOWED_USERS", "")
                if user_id:
                    save_env_value("WEIXIN_HOME_CHANNEL", user_id)

                result_json.write_text(
                    json.dumps(
                        {
                            "status": "confirmed",
                            "account_id": account_id,
                            "user_id": user_id,
                            "base_url": base_url,
                            "saved_to": str(Path(hermes_home) / ".env"),
                        },
                        ensure_ascii=False,
                        indent=2,
                    ),
                    encoding="utf-8",
                )
                write_status({"status": "confirmed", "account_id": account_id, "user_id": user_id})
                return 0

            await asyncio.sleep(1)

    write_status({"status": "timeout", "message": "Weixin login timed out"})
    return 5


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
