---
name: weixin-assistant-skill
description: 微信助手skill：Build or reproduce a Hermes Agent personal WeChat assistant/ClawBot connection. Use when the user asks to调用微信助手skill, 接入微信, 扫码登录微信助手, 搭建公众号助手/朋友圈助手/私域群素材采集助手, configure Hermes Gateway/iLink/Weixin, or reuse the previous Hermes-to-WeChat setup flow for another assistant.
---

# 微信助手 Skill

## Purpose

Use this skill to turn a business idea into a reusable WeChat assistant powered by Hermes Agent. It covers:

- Installing or verifying Hermes Agent.
- Logging in to personal WeChat through the Hermes Weixin/iLink platform.
- Starting and verifying Hermes Gateway.
- Adding domain-specific skills and `SOUL.md` rules.
- Reusing the same flow for朋友圈助手、公众号助手、群素材采集助手 or other private-domain assistants.

Do not expose or commit tokens, QR screenshots, `.env`, OAuth files, logs with secrets, or WeChat account IDs.

## Default Workflow

1. Read `references/setup-flow.md` for the end-to-end setup sequence.
2. Use `scripts/weixin_qr_login.py` to generate a QR code when a fresh WeChat login is needed.
3. Use `scripts/gateway.ps1 status|restart|logs` to operate the Hermes Gateway on Windows.
4. Read `references/config-and-safety.md` before changing allowlists, group access, or committing files.
5. Read `references/troubleshooting.md` when messages are not received, QR login fails, or Gateway appears stuck.

## Assistant Build Pattern

For each new WeChat assistant:

1. Define the assistant's job in one sentence, for example `公众号选题助手`, `朋友圈素材助手`, or `微信群素材采集助手`.
2. Create or install the domain skill that does the real work.
3. Add short WeChat-facing rules to `%USERPROFILE%\.hermes\SOUL.md`.
4. If the assistant should receive images, define whether image-only messages should wait for user confirmation or trigger immediate processing.
5. Keep WeChat output short. Long setup analysis belongs in local notes, not chat replies.
6. Verify with a simple private-message test before enabling group access.

## Reuse Checklist

- Hermes command works: `hermes -z "只回复 OK" --accept-hooks`.
- Weixin account is logged in and `.hermes\.env` contains Weixin values.
- Gateway status is running.
- The target WeChat user or group is allowed by policy.
- The assistant replies correctly to text, images, and the target business command.
- Secrets and generated QR/status files are excluded from Git.
