# Troubleshooting

## Hermes Command Not Found

Use the absolute path:

```powershell
$hermes = 'C:\Users\Administrator\AppData\Local\hermes\hermes-agent\venv\Scripts\hermes.exe'
& $hermes --version
```

## Gateway Status Is Empty

Check process and logs:

```powershell
$skill = 'C:\Users\Administrator\.codex\skills\hermes-weixin-assistant-setup'
& "$skill\scripts\gateway.ps1" status
& "$skill\scripts\gateway.ps1" logs
```

Hermes may spawn nested `hermes.exe -> python.exe -> python.exe` processes. That can be normal.

## Discord Warning Appears

Warnings like `No bot token configured` for Discord are not necessarily a Weixin failure. Verify Weixin by sending a private WeChat message.

## Duplicate Gateway Replies

If two assistants respond, stop all gateway processes and restart one:

```powershell
$skill = 'C:\Users\Administrator\.codex\skills\hermes-weixin-assistant-setup'
& "$skill\scripts\gateway.ps1" stop
& "$skill\scripts\gateway.ps1" start
```

## QR Expired

Run the QR helper again and scan the new PNG. Do not reuse old QR images.

## Image Messages Behave Wrong

Check both:

- `%USERPROFILE%\.hermes\SOUL.md`
- Hermes image routing code/config, if the setup customized image-only prompts.

For business workflows, prefer skill rules over long `SOUL.md` prompts.

## WeChat Does Not Reply

Check:

1. Gateway is running.
2. Weixin credentials exist in `.hermes\.env`.
3. User or group is allowed by policy.
4. The message platform is not disabled.
5. Logs show Weixin connection, not only unrelated Discord warnings.
