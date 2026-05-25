# Config And Safety

## Files That May Contain Secrets

Never commit:

- `%USERPROFILE%\.hermes\.env`
- `%USERPROFILE%\.hermes\auth.json`
- `%USERPROFILE%\.codex\auth.json`
- `weixin_qr.png`
- `weixin_qr.json`
- `weixin_status.json`
- `weixin_result.json`
- Gateway logs if they include tokens or user IDs

## Weixin Policy Defaults

Start conservative:

```text
WEIXIN_DM_POLICY=allowlist
WEIXIN_ALLOW_ALL_USERS=false
WEIXIN_ALLOWED_USERS=<your_user_id>
WEIXIN_GROUP_POLICY=disabled
WEIXIN_GROUP_ALLOWED_USERS=
```

Only enable group access after private chat has been tested.

## Group Access

When collecting group material, define:

- Which groups are allowed.
- Which material types can be collected.
- Whether images/videos should be saved raw.
- What privacy must be removed: avatar, nickname, phone, QR code, payment code, private chat content.
- Whether the assistant should reply inside the group or only collect silently.

## Git Safety

Before committing:

```powershell
git status --short
git diff -- . ':!*.png' ':!*.jpg' ':!*.json' ':!*.log'
```

If a file might contain a token or QR login data, do not commit it.

## Output Safety

WeChat chat replies should be short. For setup work, summarize:

- What changed.
- Whether Gateway is running.
- What the user should test.

Do not paste long logs into WeChat.
