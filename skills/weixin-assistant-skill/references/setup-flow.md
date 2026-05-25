# Setup Flow

This is the reusable flow for connecting Hermes Agent to personal WeChat through its Weixin/iLink platform.

## 1. Install Or Verify Hermes

Official Hermes install entry:

- Docs: https://www.hermes-ai.net/docs/installation/
- GitHub: https://github.com/NousResearch/hermes-agent

Windows native PowerShell installer:

```powershell
irm https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.ps1 | iex
```

In this workspace the working Hermes command has been:

```powershell
C:\Users\Administrator\AppData\Local\hermes\hermes-agent\venv\Scripts\hermes.exe
```

Verify:

```powershell
$hermes = 'C:\Users\Administrator\AppData\Local\hermes\hermes-agent\venv\Scripts\hermes.exe'
& $hermes -z "只回复 OK" --accept-hooks
```

Expected output: `OK`.

## 2. Configure Model And Home

Hermes home is usually:

```text
C:\Users\Administrator\.hermes
```

Typical model config used for this setup:

```yaml
model:
  provider: openai-codex
  default: gpt-5.5
agent:
  reasoning_effort: xhigh
terminal:
  backend: local
```

Do not print or commit auth files. If the model provider is not authenticated, run the provider's normal login/setup flow rather than copying tokens into chat.

## 3. Add Domain Skill And SOUL Rules

For a business-specific assistant, copy the relevant skill into Hermes, for example:

```text
C:\Users\Administrator\.hermes\skills\social-media\<skill-name>
```

Then add short behavioral rules to:

```text
C:\Users\Administrator\.hermes\SOUL.md
```

Keep `SOUL.md` high level. Put long methods, examples, compliance rules, and file paths inside the domain skill.

## 4. Login Weixin With QR

Use the bundled QR helper:

```powershell
$skill = 'C:\Users\Administrator\.codex\skills\weixin-assistant-skill'
$out = 'C:\Users\Administrator\Nutstore\1\强哥的AI知识库大脑\.runtime\weixin-login'
python "$skill\scripts\weixin_qr_login.py" "$out"
```

Open or display:

```text
<output-dir>\weixin_qr.png
```

Scan with WeChat and confirm on phone. The helper saves Weixin credentials into Hermes' local `.env`. It should not print the token.

Generated QR/status/result files are temporary and must not be committed.

## 5. Start Gateway

Use:

```powershell
$skill = 'C:\Users\Administrator\.codex\skills\weixin-assistant-skill'
& "$skill\scripts\gateway.ps1" restart
& "$skill\scripts\gateway.ps1" status
```

Manual equivalent:

```powershell
$hermes = 'C:\Users\Administrator\AppData\Local\hermes\hermes-agent\venv\Scripts\hermes.exe'
& $hermes gateway run --replace
```

For unattended operation, install as a scheduled task only after manual verification:

```powershell
& $hermes gateway install
```

## 6. Verify

Test in this order:

1. Private text message: ask it to reply `OK`.
2. Image-only message: confirm the desired routing behavior.
3. Business command: ask it to generate or collect material using the domain skill.
4. Check logs if it does not answer.

Keep groups disabled until private-message behavior is correct.

## 7. Reuse For Another WeChat Assistant

For a new assistant, keep the same Hermes/Weixin/Gateway layer and swap the business layer:

- 公众号助手: add article-writing and WeChat Official Account publishing skills.
- 朋友圈助手: add short-copy/material-library skills.
- 群素材采集助手: add classification, storage, and privacy-filtering rules.
- 客服助手: add FAQ, routing, and escalation rules.

The key is to separate:

- Transport: Hermes + Weixin + Gateway.
- Persona/rules: `SOUL.md`.
- Business workflow: domain skill.
- Storage: local folders, Feishu Base, or other knowledge base.
