# Pilot Scenario Simulation

These 50 scenarios reflect the expected behavior after the final pilot-readiness pass. They cover greetings, small talk, irrelevant prompts, empty/random input, frustrated users, mixed greeting plus issue input, vague issues, typo-heavy issues, urgent cases, security-sensitive cases, and enterprise IT categories.

| # | User query | Detected intent type | Chatbot interpretation | Confidence score | Clarification asked | KB articles used | Response generated | Correctness evaluation | Escalation decision | System verdict |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | hi | GREETING | Greeting only | 0.95 | No | None | Greet user and ask them to describe the IT issue | Correctly avoids support workflow | No | Pass |
| 2 | hello | GREETING | Greeting only | 0.95 | No | None | Greet user and ask them to describe the IT issue | Correctly avoids support workflow | No | Pass |
| 3 | hey there | GREETING | Greeting only | 0.95 | No | None | Greet user and ask them to describe the IT issue | Correctly handles casual opener | No | Pass |
| 4 | good morning | GREETING | Greeting only | 0.95 | No | None | Greet user and ask for support details | Correctly handles business greeting | No | Pass |
| 5 | how are you | SMALL_TALK | Small talk | 0.90 | No | None | Short reply and redirect to IT support | Correctly keeps conversation scoped | No | Pass |
| 6 | what can you do | SMALL_TALK | Capability question | 0.90 | No | None | Explain supported IT issues briefly | Correctly answers without pretending broad capability | No | Pass |
| 7 | who are you | SMALL_TALK | Bot identity question | 0.90 | No | None | Explain IT support assistant role | Correctly sets expectations | No | Pass |
| 8 | thanks | SMALL_TALK | Courtesy message | 0.90 | No | None | Short acknowledgement and support redirect | Correctly avoids unnecessary KB lookup | No | Pass |
| 9 | tell me a joke | IRRELEVANT | Out-of-scope request | 0.90 | No | None | Polite refusal and redirect to IT support | Correctly refuses non-IT request | No | Pass |
| 10 | what is the weather | IRRELEVANT | Out-of-scope request | 0.90 | No | None | Polite refusal and redirect to IT support | Correctly refuses non-IT request | No | Pass |
| 11 | who is president | IRRELEVANT | Out-of-scope request | 0.90 | No | None | Polite refusal and redirect to IT support | Correctly refuses knowledge question | No | Pass |
| 12 | give me a recipe | IRRELEVANT | Out-of-scope request | 0.90 | No | None | Polite refusal and redirect to IT support | Correctly refuses consumer request | No | Pass |
| 13 | asdf | EMPTY | Random or insufficient text | 0.82 | Yes | None | Ask user to describe the issue in one sentence | Correctly asks for usable input | No | Pass |
| 14 | empty message | EMPTY | No usable content | 0.99 | Yes | None | Ask user to enter the issue details | Correctly handles blank API input | No | Pass |
| 15 | this is useless | ABUSIVE | Frustration without issue context | 0.86 | Yes | None | Calm response and ask for the actual issue | Correctly de-escalates without creating empty ticket | No | Pass |
| 16 | connect me to human | ABUSIVE | Handoff request without issue context | 0.86 | Yes | None | Ask for issue context before ticket handoff | Correctly avoids technician-empty ticket | No | Pass |
| 17 | give me a technician | ABUSIVE | Handoff request without issue context | 0.86 | Yes | None | Ask for issue context before ticket handoff | Correctly asks for minimum context | No | Pass |
| 18 | hi vpn not working | SUPPORT_REQUEST | VPN connection issue | 0.79 | Yes | VPN KB after required slots | Triage question, then grounded VPN steps | Correctly ignores greeting and processes issue | No | Pass |
| 19 | hello my outlook is stuck | SUPPORT_REQUEST | Email or Outlook sync issue | 0.79 | Yes | Email KB after required slots | Triage question, then grounded Outlook steps | Correctly processes mixed greeting and issue | No | Pass |
| 20 | vpn conection not wrking | SUPPORT_REQUEST | Typo-heavy VPN issue | 0.71 | Yes | VPN KB | Ask device/error details, then VPN steps | Correctly tolerates spelling mistakes | No | Pass |
| 21 | outlok not syncng | SUPPORT_REQUEST | Typo-heavy email issue | 0.71 | Yes | Email KB | Ask client/webmail/error details, then email steps | Correctly maps typo to email category | No | Pass |
| 22 | password not taking | SUPPORT_REQUEST | Password or sign-in issue | 0.79 | Yes | Password/access KB | Ask lockout/MFA/error details | Correctly treats vague phrasing as access problem | No | Pass |
| 23 | account locked | SUPPORT_REQUEST | Account lockout | 0.79 | No | None | Create human handoff context | Correctly triggers deterministic escalation | Yes | Pass |
| 24 | wifi keeps dropping | SUPPORT_REQUEST | Wi-Fi instability | 0.71 | Yes | Wi-Fi KB | Ask device/network/scope details | Correctly asks for minimal missing details | No | Pass |
| 25 | internet is there but company apps are not opening | SUPPORT_REQUEST | Internal apps or VPN access issue | 0.87 | Yes | VPN/network KB | Clarify VPN/app/error, then grounded steps | Correctly recognizes enterprise access pattern | No | Pass |
| 26 | laptop hangs again and again | SUPPORT_REQUEST | Device performance issue | 0.79 | Yes | Performance KB | Ask OS/app/start-time details, then safe steps | Correctly avoids generic answer | No | Pass |
| 27 | system slow and outlook also not opening | SUPPORT_REQUEST | Compound performance and email issue | 0.87 | Yes | Performance and email KB | Ask primary impact, then targeted first path | Correctly detects mixed issue | No | Pass |
| 28 | printer offline | SUPPORT_REQUEST | Printer availability issue | 0.71 | Yes | Printer KB | Ask printer name/queue/error details | Correctly routes to endpoint support category | No | Pass |
| 29 | print queue stuck | SUPPORT_REQUEST | Print queue issue | 0.79 | Yes | Printer queue KB | Provide grounded queue/spooler troubleshooting | Correctly uses printer KB | No | Pass |
| 30 | browser not loading payroll portal | SUPPORT_REQUEST | Browser or access issue for payroll portal | 0.87 | Yes | Browser/access KB | Ask browser/site/error details | Correctly detects business-critical app context | Conditional | Pass |
| 31 | chrome keeps looping on login | SUPPORT_REQUEST | Browser SSO loop | 0.79 | Yes | Browser SSO KB | Suggest cache/private window/MFA path from KB | Correctly handles common SSO issue | No | Pass |
| 32 | software install failed | SUPPORT_REQUEST | Software install issue | 0.79 | Yes | Software install KB | Ask app/OS/error details, then approved steps | Correctly handles endpoint software issue | No | Pass |
| 33 | Teams app crashed | SUPPORT_REQUEST | Application crash | 0.71 | Yes | Software crash KB | Ask version/error and suggest restart/update steps | Correctly maps app crash to software category | No | Pass |
| 34 | access denied to HR portal | SUPPORT_REQUEST | Permission or access issue | 0.87 | Yes | Access KB | Ask portal/account/error details | Correctly avoids password-only assumption | No | Pass |
| 35 | payroll access blocked | SUPPORT_REQUEST | High-impact access issue | 0.79 | No | None | Escalate with payroll and blocked metadata | Correctly treats business-impact access as urgent | Yes | Pass |
| 36 | ethernet not working | SUPPORT_REQUEST | Wired network issue | 0.79 | Yes | Network KB | Ask cable/port/scope details | Correctly routes to network team category | No | Pass |
| 37 | dns issue with intranet | SUPPORT_REQUEST | Internal DNS issue | 0.79 | Yes | DNS/internal site KB | Ask VPN/FQDN/scope details | Correctly handles network infrastructure symptom | No | Pass |
| 38 | security issue malware popup | SUPPORT_REQUEST | Security-sensitive endpoint issue | 0.87 | No | None | Immediate escalation with security reason | Correctly avoids self-service unsafe steps | Yes | Pass |
| 39 | my laptop was stolen | SUPPORT_REQUEST | Security and asset-loss incident | 0.71 | No | None | Immediate escalation with security reason | Correctly avoids normal troubleshooting | Yes | Pass |
| 40 | CEO cannot login | SUPPORT_REQUEST | Critical executive access issue | 0.79 | No | None | Immediate escalation with critical impact | Correctly prioritizes executive blocker | Yes | Pass |
| 41 | all users cannot access email | SUPPORT_REQUEST | Multi-user email outage | 0.79 | No | None | Escalate as likely outage | Correctly avoids one-user troubleshooting | Yes | Pass |
| 42 | cannot work since morning | SUPPORT_REQUEST | Vague but urgent work blocker | 0.71 | No | None | Escalate or ask one context question if no prior details | Correctly detects severe business impact | Yes | Pass |
| 43 | app says license expired | SUPPORT_REQUEST | Software license issue | 0.79 | Yes | Software install/license KB | Ask app/license/error details | Correctly targets software entitlement path | No | Pass |
| 44 | scanner cannot send to email | SUPPORT_REQUEST | Scanner/email destination issue | 0.79 | Yes | Printer scanner KB | Ask device/destination/error details | Correctly uses printer/scanner KB | No | Pass |
| 45 | office login problem | SUPPORT_REQUEST | Password, SSO, or access issue | 0.79 | Yes | Password/access KB | Ask lockout/MFA/error details | Correctly asks clarification before steps | No | Pass |
| 46 | company portal says 403 | SUPPORT_REQUEST | Portal permission issue | 0.71 | Yes | Access/browser KB | Ask portal/account/error details | Correctly maps 403 to access path | No | Pass |
| 47 | websites work but internal site fails | SUPPORT_REQUEST | Internal DNS or VPN issue | 0.79 | Yes | DNS/VPN KB | Ask VPN/FQDN/network details | Correctly distinguishes public internet from internal access | No | Pass |
| 48 | mfa prompt not coming | SUPPORT_REQUEST | MFA delivery issue | 0.79 | Yes | MFA/access KB | Ask method/device/recent change details | Correctly avoids password reset-only response | No | Pass |
| 49 | mail attachment stuck | SUPPORT_REQUEST | Email attachment issue | 0.79 | Yes | Email KB | Ask app/file size/webmail details | Correctly uses email troubleshooting path | No | Pass |
| 50 | this is useless vpn still broken | SUPPORT_REQUEST | Frustrated VPN issue with support context | 0.79 | Yes | VPN KB or prior KB metadata | Continue support or escalate if previous attempts failed | Correctly treats frustration plus issue as support, not just abuse | Conditional | Pass |

Key correctness checks:

- Non-support messages do not trigger KB retrieval or false resolved/not-resolved prompts.
- Mixed greeting plus issue is routed into the support workflow.
- Security, payroll, lockout, stolen device, and executive blocker language escalate deterministically.
- KB answers remain grounded in approved article content.
- Repeated issue context is retained for technician handoff.
