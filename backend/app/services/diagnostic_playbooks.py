from dataclasses import dataclass


@dataclass(frozen=True)
class DiagnosticField:
    key: str
    label: str
    question: str


@dataclass(frozen=True)
class DiagnosticPlaybook:
    category: str
    required_fields: tuple[DiagnosticField, ...]
    escalation_hint: str


PLAYBOOKS: dict[str, DiagnosticPlaybook] = {
    "VPN": DiagnosticPlaybook(
        category="VPN",
        required_fields=(
            DiagnosticField("device_os", "Device OS", "Which device and OS are you using, such as Windows laptop or macOS?"),
            DiagnosticField("internet_working", "Internet works without VPN", "Can you browse normal websites without the VPN connected?"),
            DiagnosticField("mfa_prompt", "MFA prompt status", "Do you receive an MFA prompt when connecting?"),
            DiagnosticField("error_message", "Exact error", "What exact VPN error message or code do you see?"),
        ),
        escalation_hint="Check VPN authentication, MFA registration, gateway health, and account lock state.",
    ),
    "PASSWORD": DiagnosticPlaybook(
        category="PASSWORD",
        required_fields=(
            DiagnosticField("account_locked", "Account lock state", "Does the message say your account is locked?"),
            DiagnosticField("reset_attempted", "Password reset attempted", "Have you already tried the self-service password reset portal?"),
            DiagnosticField("mfa_available", "MFA availability", "Can you access your MFA method or authenticator app?"),
            DiagnosticField("error_message", "Exact error", "What exact sign-in error do you see?"),
        ),
        escalation_hint="Check account lock state, identity provider logs, and MFA registration.",
    ),
    "ACCESS": DiagnosticPlaybook(
        category="ACCESS",
        required_fields=(
            DiagnosticField("affected_app", "Affected app", "Which application or company service are you trying to access?"),
            DiagnosticField("account_locked", "Account lock state", "Does the message say your account is locked or access is denied?"),
            DiagnosticField("mfa_available", "MFA availability", "Can you access your MFA method or authenticator app?"),
            DiagnosticField("error_message", "Exact error", "What exact access or permission error do you see?"),
        ),
        escalation_hint="Check entitlement, group membership, identity provider logs, and MFA registration.",
    ),
    "WIFI": DiagnosticPlaybook(
        category="WIFI",
        required_fields=(
            DiagnosticField("device_os", "Device OS", "Which device and OS are affected?"),
            DiagnosticField("network_name", "Network name", "Which WiFi network are you trying to join?"),
            DiagnosticField("other_devices_working", "Other devices", "Are other devices working on the same WiFi network?"),
            DiagnosticField("error_message", "Exact error", "What exact connection error do you see?"),
        ),
        escalation_hint="Check wireless profile, access point health, DHCP, and device network adapter state.",
    ),
    "NETWORK": DiagnosticPlaybook(
        category="NETWORK",
        required_fields=(
            DiagnosticField("connection_type", "Connection type", "Are you on WiFi, ethernet, VPN, or mobile hotspot?"),
            DiagnosticField("scope", "Issue scope", "Are all websites down or only company/internal services?"),
            DiagnosticField("other_users_affected", "Other users affected", "Are other people or devices having the same network issue?"),
            DiagnosticField("error_message", "Exact error", "What exact network or browser error do you see?"),
        ),
        escalation_hint="Check DNS, DHCP, local network adapter, internet reachability, and service status.",
    ),
    "EMAIL": DiagnosticPlaybook(
        category="EMAIL",
        required_fields=(
            DiagnosticField("email_client", "Email client", "Are you using Outlook, Gmail, Apple Mail, or webmail?"),
            DiagnosticField("webmail_works", "Webmail status", "Does webmail work in a browser?"),
            DiagnosticField("send_receive_scope", "Send or receive scope", "Is the issue with sending, receiving, sync, calendar, or attachments?"),
            DiagnosticField("error_message", "Exact error", "What exact email error message do you see?"),
        ),
        escalation_hint="Check mailbox service health, client profile state, authentication, and message queue errors.",
    ),
    "DEVICE_PERFORMANCE": DiagnosticPlaybook(
        category="DEVICE_PERFORMANCE",
        required_fields=(
            DiagnosticField("device_os", "Device OS", "Which device and OS are running slowly?"),
            DiagnosticField("affected_app", "Affected app", "Is the whole device slow or only a specific application?"),
            DiagnosticField("restart_done", "Restart completed", "Have you restarted the device since the slowdown started?"),
            DiagnosticField("when_started", "Start time", "When did the slowdown start?"),
        ),
        escalation_hint="Check startup load, disk capacity, CPU, memory, recent updates, and affected application health.",
    ),
    "SOFTWARE": DiagnosticPlaybook(
        category="SOFTWARE",
        required_fields=(
            DiagnosticField("affected_app", "Affected app", "Which software or application is affected?"),
            DiagnosticField("device_os", "Device OS", "Which device and OS are you using?"),
            DiagnosticField("recent_change", "Recent change", "Did this start after an install, update, or password change?"),
            DiagnosticField("error_message", "Exact error", "What exact error message do you see?"),
        ),
        escalation_hint="Check install state, license, update history, app logs, and permissions.",
    ),
    "BROWSER": DiagnosticPlaybook(
        category="BROWSER",
        required_fields=(
            DiagnosticField("browser", "Browser", "Which browser are you using, such as Chrome, Edge, Firefox, or Safari?"),
            DiagnosticField("affected_site", "Affected site", "Which website or company portal is affected?"),
            DiagnosticField("cache_cleared", "Cache cleared", "Have you tried a private window or clearing cache for that site?"),
            DiagnosticField("error_message", "Exact error", "What exact browser error do you see?"),
        ),
        escalation_hint="Check browser cache, extensions, proxy, SSO cookies, and website availability.",
    ),
    "PRINTER": DiagnosticPlaybook(
        category="PRINTER",
        required_fields=(
            DiagnosticField("printer_name", "Printer name", "Which printer or queue are you using?"),
            DiagnosticField("device_os", "Device OS", "Which device and OS are you printing from?"),
            DiagnosticField("network_connection", "Network connection", "Are you on the office network or VPN?"),
            DiagnosticField("error_message", "Exact error", "What exact print or scanner error do you see?"),
        ),
        escalation_hint="Check print queue, printer online state, driver, paper/toner, and network reachability.",
    ),
    "GENERAL": DiagnosticPlaybook(
        category="GENERAL",
        required_fields=(
            DiagnosticField("affected_app", "Affected app", "Which application, device, or service is affected?"),
            DiagnosticField("error_message", "Exact error", "What exact error message do you see?"),
            DiagnosticField("business_impact", "Business impact", "Is this blocking your work or affecting multiple people?"),
        ),
        escalation_hint="Review the affected service, user impact, and exact error before assigning.",
    ),
}


def get_playbook(category: str | None) -> DiagnosticPlaybook:
    return PLAYBOOKS.get(category or "GENERAL", PLAYBOOKS["GENERAL"])
