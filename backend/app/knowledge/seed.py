KNOWLEDGE_BASE_SEED = [
    {
        "category": "VPN",
        "title": "VPN cannot connect",
        "content": (
            "Confirm your internet connection is stable, then disconnect and reconnect the VPN. "
            "Restart the VPN client, verify your MFA prompt is approved, and check that your system clock is accurate. "
            "If the issue continues, switch to the secondary gateway and retry."
        ),
        "keywords": "vpn,globalprotect,anyconnect,forticlient,connection,tunnel,mfa,gateway",
    },
    {
        "category": "VPN",
        "title": "VPN connected but internal sites unavailable",
        "content": (
            "Disconnect and reconnect the VPN, then flush DNS and retry the internal site. "
            "Confirm the site opens from a browser without cached credentials. "
            "If only one application fails, note the application name before escalation."
        ),
        "keywords": "vpn,internal,site,intranet,dns,portal,split tunnel",
    },
    {
        "category": "PASSWORD",
        "title": "Password reset and account unlock",
        "content": (
            "Use the self-service password portal to reset your password. "
            "Choose a new password that has not been used recently, then wait two minutes before signing in again. "
            "If your account is locked, wait fifteen minutes or request technician help."
        ),
        "keywords": "password,reset,forgot,locked,account,login,sign in,credentials",
    },
    {
        "category": "ACCESS",
        "title": "Access denied to company application",
        "content": (
            "Confirm the user can sign in to SSO and MFA before changing permissions. "
            "Ask which application, portal, or folder shows access denied and capture the exact message. "
            "Try signing out and back in, then test in a private browser window to rule out stale SSO cookies. "
            "If access is still denied, escalate with the app name, manager approval status, and required role or group."
        ),
        "keywords": "access,denied,permission,permissions,sso,mfa,portal,role,group",
    },
    {
        "category": "ACCESS",
        "title": "MFA prompt missing or authenticator unavailable",
        "content": (
            "Check whether the user changed phones or lost access to the authenticator app. "
            "Try the backup sign-in method if one is registered. "
            "Do not ask for MFA codes in chat. If no approved method is available, escalate for identity verification and MFA reset."
        ),
        "keywords": "mfa,authenticator,prompt,verification,backup,phone,access,login",
    },
    {
        "category": "WIFI",
        "title": "WiFi connection troubleshooting",
        "content": (
            "Turn WiFi off and back on, then reconnect to the company network. "
            "Forget the saved network profile if prompted credentials keep failing. "
            "Move closer to an access point and confirm other sites load before retrying business applications."
        ),
        "keywords": "wifi,wireless,network,internet,ssid,access point,connection",
    },
    {
        "category": "WIFI",
        "title": "WiFi connected but no internet",
        "content": (
            "Confirm whether other devices work on the same WiFi network. "
            "Forget and rejoin the network, then restart the device network adapter. "
            "If the device gets a self-assigned or 169.254 address, capture the IP details and escalate to network support."
        ),
        "keywords": "wifi,connected,no internet,dhcp,ip,address,wireless",
    },
    {
        "category": "NETWORK",
        "title": "Wired or office network outage triage",
        "content": (
            "Check whether the issue affects one device, one room, or multiple users. "
            "For ethernet, confirm the cable is seated and link lights are active. "
            "Try a known working port or cable if available. "
            "If multiple users or ports are affected, escalate with location, VLAN/port if known, and impact scope."
        ),
        "keywords": "network,ethernet,lan,outage,port,cable,multiple users,office",
    },
    {
        "category": "NETWORK",
        "title": "DNS or internal site resolution issue",
        "content": (
            "Confirm whether public websites work and whether only internal names fail. "
            "Reconnect VPN if internal names require VPN. "
            "Flush DNS, try the fully qualified domain name, and test in another browser. "
            "Escalate if multiple internal services fail or DNS errors continue."
        ),
        "keywords": "dns,internal,intranet,site,resolve,resolution,network,vpn",
    },
    {
        "category": "EMAIL",
        "title": "Email send or sync failures",
        "content": (
            "Refresh the mailbox and check whether webmail works. "
            "Restart the email client, confirm you are online, and remove large attachments if messages are stuck. "
            "If webmail works but the desktop client does not, rebuild the mail profile."
        ),
        "keywords": "email,outlook,gmail,mailbox,sync,send,receive,attachment,calendar",
    },
    {
        "category": "EMAIL",
        "title": "Outlook profile or calendar issue",
        "content": (
            "Check whether webmail works first. If webmail works, restart Outlook and verify the account is connected. "
            "Disable recently added plugins, then recreate the Outlook profile if sync or calendar errors continue. "
            "Escalate with mailbox address, webmail status, affected folder/calendar, and exact error."
        ),
        "keywords": "outlook,profile,calendar,mailbox,webmail,sync,plugin",
    },
    {
        "category": "DEVICE_PERFORMANCE",
        "title": "Slow device performance",
        "content": (
            "Restart the device, close unused applications, and confirm at least ten percent disk space is free. "
            "Install pending operating system updates outside active work hours. "
            "If performance remains poor, capture the application name and when the slowdown started."
        ),
        "keywords": "slow,performance,laptop,device,cpu,memory,disk,freeze,lag",
    },
    {
        "category": "DEVICE_PERFORMANCE",
        "title": "Laptop freezing or high resource usage",
        "content": (
            "Restart the laptop if it has not been restarted today. "
            "Open Task Manager or Activity Monitor and identify whether CPU, memory, or disk is saturated. "
            "Close unused browser tabs and large applications, then check free disk space. "
            "Escalate if the device freezes after restart or a business app repeatedly consumes high resources."
        ),
        "keywords": "laptop,freezing,hang,cpu,memory,disk,task manager,activity monitor",
    },
    {
        "category": "SOFTWARE",
        "title": "Software installation or update failure",
        "content": (
            "Confirm the app name, device OS, and whether the user has company software center access. "
            "Restart the device, then retry from the approved software portal instead of downloading from the web. "
            "Capture installer error codes and check available disk space. "
            "Escalate if admin approval, license assignment, or device management action is required."
        ),
        "keywords": "software,install,installation,update,software center,license,admin,error",
    },
    {
        "category": "SOFTWARE",
        "title": "Application crashes or will not open",
        "content": (
            "Restart the application and then the device. "
            "Check whether the issue affects only one user profile or everyone using the app. "
            "Open the app in safe mode if supported, disable recent plugins, and verify updates are installed. "
            "Escalate with app version, crash time, device OS, and any error report."
        ),
        "keywords": "app,application,crash,crashing,not opening,plugin,version,software",
    },
    {
        "category": "BROWSER",
        "title": "Browser page or company portal not loading",
        "content": (
            "Try a private or incognito window first. "
            "Clear cache and cookies for the affected site, then disable extensions temporarily. "
            "Test another approved browser and confirm whether other users can access the same page. "
            "Escalate with URL, browser name, screenshot, and exact browser error."
        ),
        "keywords": "browser,chrome,edge,firefox,safari,cache,cookies,portal,page,website",
    },
    {
        "category": "BROWSER",
        "title": "SSO loop or browser sign-in problem",
        "content": (
            "Sign out of all company tabs, close the browser, and reopen a private window. "
            "Clear cookies for the company identity provider and affected app. "
            "Confirm device time is correct and MFA can be completed. "
            "Escalate if the user loops between sign-in pages after cache and cookie cleanup."
        ),
        "keywords": "browser,sso,login,signin,cookies,cache,mfa,loop,identity",
    },
    {
        "category": "PRINTER",
        "title": "Printer offline or print queue stuck",
        "content": (
            "Confirm the printer name and whether other users can print to it. "
            "Check for paper, toner, jams, and whether the printer is online. "
            "Cancel stuck jobs, restart the print spooler or device, and retry a test page. "
            "Escalate with printer name, location, queue name, and error shown on the printer or computer."
        ),
        "keywords": "printer,offline,print,queue,spooler,paper,toner,jam",
    },
    {
        "category": "PRINTER",
        "title": "Scanner or secure print release issue",
        "content": (
            "Confirm whether printing works but scanning or secure release fails. "
            "Ask the user to sign out and back into the printer panel, then try a small test scan. "
            "Verify the destination email or folder is correct. "
            "Escalate with printer name, badge/login status, destination, and exact panel error."
        ),
        "keywords": "scanner,scan,secure print,badge,release,printer,email,folder",
    },
    {
        "category": "GENERAL",
        "title": "General IT triage",
        "content": (
            "Restart the affected application, confirm your network connection is working, and retry the action. "
            "Capture any exact error message and the time the issue started. "
            "If the same issue repeats, the ticket should include the app name, device, and screenshot details."
        ),
        "keywords": "issue,error,problem,application,app,system,help",
    },
]


def _rich_entry(
    *,
    category: str,
    title: str,
    subcategory: str,
    summary: str,
    causes: str,
    steps: list[str],
    escalate: str,
    keywords: str,
) -> dict:
    numbered_steps = " ".join(f"{index}. {step}" for index, step in enumerate(steps, start=1))
    return {
        "category": category,
        "title": title,
        "content": (
            f"Subcategory: {subcategory}. "
            f"Summary: {summary} "
            f"Likely causes: {causes} "
            f"Resolution steps: {numbered_steps} "
            f"Escalate when: {escalate}"
        ),
        "keywords": keywords,
    }


KNOWLEDGE_BASE_SEED.extend(
    [
        _rich_entry(
            category="ACCESS",
            title="Invalid credentials during SSO login",
            subcategory="Login / SSO",
            summary="User can reach the sign-in page but receives an invalid username or password message.",
            causes="mistyped password, stale saved browser credentials, wrong account format, expired password, or identity provider sync delay.",
            steps=[
                "Confirm the user is signing in with the company email address, not an alias or personal account.",
                "Ask the user to type the password manually instead of using saved browser credentials.",
                "Try a private browser window to rule out stale SSO cookies.",
                "If password expiry is suspected, use the self-service password reset portal and wait two minutes before retrying.",
            ],
            escalate="the account remains blocked after reset, identity verification is needed, or the exact error mentions disabled account or directory sync.",
            keywords="login,logging in,sign in,signin,sso,invalid credentials,wrong password,credentials,identity provider,company portal",
        ),
        _rich_entry(
            category="ACCESS",
            title="Account locked after failed sign-in attempts",
            subcategory="Account lockout",
            summary="User is locked out after too many failed login attempts.",
            causes="repeated wrong password attempts, saved credentials on another device, expired password, or automated retries from an email client.",
            steps=[
                "Stop repeated sign-in attempts for fifteen minutes to avoid extending the lockout.",
                "Check whether Outlook, mobile mail, VPN, or another saved app is retrying with an old password.",
                "Reset the password from the approved portal if the user does not know the current password.",
                "Retry sign-in once from a private browser window after the lockout window or reset completes.",
            ],
            escalate="the account is still locked after the wait period, the user has urgent business impact, or MFA/identity verification is required.",
            keywords="account locked,locked out,too many attempts,login,sign in,password,unlock,access,blocked",
        ),
        _rich_entry(
            category="ACCESS",
            title="MFA code or authenticator approval fails",
            subcategory="MFA",
            summary="User can enter credentials but cannot complete MFA verification.",
            causes="changed phone, incorrect time on device, expired push notification, blocked authenticator app, missing backup method, or MFA fatigue protection.",
            steps=[
                "Confirm the user is using an approved MFA method and never ask them to share a code in chat.",
                "Ask the user to approve the most recent prompt and reject any unexpected prompts.",
                "Check device time and network connectivity on the phone.",
                "Try a registered backup method if available.",
            ],
            escalate="no registered MFA method works, the user changed phones, or there are suspicious/unexpected MFA prompts.",
            keywords="mfa,authenticator,code not working,verification code,push notification,approval,login,sso,access",
        ),
        _rich_entry(
            category="ACCESS",
            title="Password expired during login",
            subcategory="Password expiry",
            summary="User is prompted that the password is expired or must be changed before accessing services.",
            causes="password age policy, account recovery reset, or forced rotation after security review.",
            steps=[
                "Direct the user to the approved password change page.",
                "Use a password that has not been used recently and meets policy requirements.",
                "Sign out of browser, VPN, email, and mobile apps after the change.",
                "Update saved passwords in Outlook, phone mail, VPN, and browser password manager.",
            ],
            escalate="the password change page fails, the user cannot complete MFA, or critical access is blocked.",
            keywords="password expired,change password,password policy,login,sso,credentials,reset,expired",
        ),
        _rich_entry(
            category="ACCESS",
            title="Access denied because role or permission is missing",
            subcategory="Entitlement",
            summary="User can sign in but cannot open a specific app, page, folder, or workflow.",
            causes="missing group membership, license not assigned, manager approval pending, incorrect role, or stale SSO token.",
            steps=[
                "Capture the application name, URL, and exact access denied message.",
                "Ask whether access worked previously or this is a new request.",
                "Sign out and back in, then retry in a private browser window.",
                "Confirm manager approval or role request has been completed before changing permissions.",
            ],
            escalate="group/license changes are required, payroll/HR data is affected, or access is blocking time-sensitive work.",
            keywords="access denied,permission denied,role,group,license,entitlement,internal portal,hr system,payroll,403,forbidden",
        ),
        _rich_entry(
            category="PASSWORD",
            title="Forgot password self-service reset",
            subcategory="Password reset",
            summary="User forgot the password and needs to regain access through the approved reset process.",
            causes="forgotten password, expired password, or old saved credentials after a recent change.",
            steps=[
                "Open the approved self-service password reset portal.",
                "Verify identity using the registered MFA or backup method.",
                "Create a new password that has not been used recently.",
                "Wait two minutes, then sign in again from a private browser window.",
            ],
            escalate="the user cannot pass MFA, the account is disabled, or the reset portal reports identity verification failure.",
            keywords="forgot password,password reset,self service reset,reset portal,credentials,login,sign in",
        ),
        _rich_entry(
            category="PASSWORD",
            title="Password reset email or link not received",
            subcategory="Reset delivery",
            summary="User requested a reset but did not receive the reset link or verification email.",
            causes="email filtering, wrong recovery email, delayed message delivery, mailbox rule, or reset service throttling.",
            steps=[
                "Confirm the user requested the reset from the approved company portal.",
                "Check junk, quarantine, focused inbox, and email rules.",
                "Wait five minutes before requesting another link to avoid throttling.",
                "Try the alternate recovery method if one is registered.",
            ],
            escalate="no recovery method is available, recovery email is wrong, or the user is locked out of all mailbox access.",
            keywords="reset link not received,password reset email,verification email,junk,spam,recovery email,forgot password",
        ),
        _rich_entry(
            category="PASSWORD",
            title="Password reset blocked by MFA issue",
            subcategory="Reset with MFA",
            summary="User knows they need a password reset but cannot complete MFA verification.",
            causes="new phone, lost authenticator, no backup method, expired MFA registration, or blocked verification prompts.",
            steps=[
                "Do not ask for MFA codes in chat.",
                "Ask whether any backup method is registered, such as phone call or security key.",
                "Have the user try reset from a trusted device/network if allowed.",
                "Collect impact, device, and contact details for identity verification.",
            ],
            escalate="MFA reset or identity verification is required.",
            keywords="password reset,mfa blocked,authenticator lost,new phone,verification,backup method,identity verification",
        ),
        _rich_entry(
            category="VPN",
            title="VPN certificate or trust error",
            subcategory="Certificate",
            summary="VPN client fails because a certificate is expired, missing, or not trusted.",
            causes="expired device certificate, unmanaged device, incorrect system time, SSL inspection, or stale VPN profile.",
            steps=[
                "Check the device date and time are correct.",
                "Restart the VPN client and retry from a trusted network.",
                "Confirm the device is company-managed and recently checked in to device management.",
                "Capture the exact certificate or trust error shown by the VPN client.",
            ],
            escalate="certificate renewal, device compliance remediation, or VPN profile reinstall is required.",
            keywords="vpn,certificate,cert,trust,ssl,tls,expired certificate,globalprotect,anyconnect,forticlient",
        ),
        _rich_entry(
            category="VPN",
            title="VPN disconnects every few minutes",
            subcategory="Intermittent VPN",
            summary="VPN connects successfully but drops repeatedly during work.",
            causes="unstable internet, laptop sleep settings, weak WiFi, captive portal, firewall timeout, or overloaded gateway.",
            steps=[
                "Confirm normal internet remains stable when VPN is disconnected.",
                "Move closer to the router or switch to a wired network if available.",
                "Disable sleep or power saving temporarily while testing.",
                "Try the secondary VPN gateway and note the disconnect time.",
            ],
            escalate="disconnects continue on multiple networks or several users report the same VPN gateway problem.",
            keywords="vpn,disconnecting,drops,intermittent,frequent disconnect,unstable,gateway,globalprotect,anyconnect",
        ),
        _rich_entry(
            category="VPN",
            title="VPN is slow for file shares or internal apps",
            subcategory="VPN performance",
            summary="User can connect to VPN but internal apps or file shares are very slow.",
            causes="poor home internet, overloaded VPN gateway, large file transfer, DNS latency, split tunnel issue, or endpoint resource pressure.",
            steps=[
                "Confirm public websites are normal outside VPN.",
                "Close video calls or large downloads while testing the VPN app.",
                "Reconnect to the closest or secondary VPN gateway.",
                "Try one internal app at a time and note whether all internal services are slow or only one.",
            ],
            escalate="multiple users are affected, business-critical apps are unusable, or only one internal service is consistently slow.",
            keywords="vpn slow,slow vpn,file share,internal app,latency,performance,gateway,split tunnel",
        ),
        _rich_entry(
            category="VPN",
            title="VPN connected but DNS names do not resolve",
            subcategory="VPN DNS",
            summary="VPN shows connected but internal hostnames, intranet, or file share names fail.",
            causes="DNS cache, split DNS issue, wrong gateway, stale VPN route, or internal DNS outage.",
            steps=[
                "Disconnect and reconnect VPN.",
                "Flush DNS or restart the device if the user is comfortable doing so.",
                "Try the full internal URL or fully qualified domain name.",
                "Test another internal site to determine whether one service or all internal DNS is affected.",
            ],
            escalate="all internal names fail after reconnect or multiple users report the same internal DNS issue.",
            keywords="vpn,dns,internal site,hostname,intranet,file share,connected but not working,resolve",
        ),
        _rich_entry(
            category="WIFI",
            title="No WiFi networks visible",
            subcategory="Wireless adapter",
            summary="Device does not show any available WiFi networks.",
            causes="WiFi disabled, airplane mode, driver issue, disabled adapter, OS update problem, or hardware failure.",
            steps=[
                "Confirm WiFi is enabled and airplane mode is off.",
                "Restart the device network adapter or reboot the device.",
                "Check whether other devices can see nearby networks.",
                "If this is Linux or Ubuntu, confirm the wireless adapter is detected after restart.",
            ],
            escalate="no networks appear after reboot or the wireless adapter is missing from device settings.",
            keywords="wifi,wi-fi,no networks visible,wireless adapter,ubuntu,linux,airplane mode,driver",
        ),
        _rich_entry(
            category="WIFI",
            title="Captive portal or guest WiFi sign-in issue",
            subcategory="Captive portal",
            summary="User connects to guest/public WiFi but cannot complete the portal sign-in.",
            causes="blocked captive portal popup, stale DNS, browser cache, VPN already connected, or expired guest session.",
            steps=[
                "Disconnect VPN before joining the guest WiFi.",
                "Open a browser and visit a plain HTTP test page to trigger the portal.",
                "Try a private browser window or another browser.",
                "Forget the guest network and reconnect to restart the portal flow.",
            ],
            escalate="the portal is down for multiple users or business access depends on the network.",
            keywords="wifi,captive portal,guest wifi,public wifi,portal sign in,no internet,hotel,airport",
        ),
        _rich_entry(
            category="WIFI",
            title="Device has self-assigned or invalid IP address",
            subcategory="DHCP",
            summary="WiFi connects but the device receives a 169.254 address or cannot get a valid IP.",
            causes="DHCP failure, exhausted address pool, bad wireless profile, VLAN issue, or local adapter problem.",
            steps=[
                "Forget and rejoin the WiFi network.",
                "Restart WiFi or reboot the device.",
                "Check whether other devices on the same network get a valid IP address.",
                "Capture the current IP address, gateway, and network name if available.",
            ],
            escalate="multiple devices receive invalid IP addresses or the company WiFi DHCP scope may be impacted.",
            keywords="wifi,no internet,dhcp,ip address,169.254,self assigned,invalid ip,connected no internet",
        ),
        _rich_entry(
            category="NETWORK",
            title="Internet slow only on office laptop",
            subcategory="Endpoint network performance",
            summary="Network feels slow on the company laptop while other devices or personal devices work normally.",
            causes="VPN always on, proxy issue, browser extension, high CPU, weak WiFi adapter signal, or endpoint security scan.",
            steps=[
                "Confirm whether the issue happens on WiFi, ethernet, and mobile hotspot.",
                "Pause large sync clients or downloads during testing.",
                "Try another browser and one approved business app.",
                "Check whether CPU or disk is saturated while the network feels slow.",
            ],
            escalate="performance remains poor across networks or endpoint security/proxy inspection appears to be blocking traffic.",
            keywords="slow internet,office laptop,network slow,proxy,endpoint,wifi,ethernet,browser,performance",
        ),
        _rich_entry(
            category="EMAIL",
            title="Not receiving new emails",
            subcategory="Mail delivery",
            summary="User is not receiving expected messages in mailbox.",
            causes="mailbox rule, focused inbox, quarantine, sender typo, mailbox full, sync delay, or service incident.",
            steps=[
                "Check webmail to separate mailbox delivery from desktop client sync.",
                "Search all folders, including junk, quarantine, focused/other inbox, and deleted items.",
                "Confirm sender address and approximate send time.",
                "Check mailbox storage quota and remove old large messages if full.",
            ],
            escalate="messages are missing in webmail, multiple users are affected, or mail flow tracing is required.",
            keywords="not receiving emails,email missing,mail delivery,quarantine,junk,focused inbox,mailbox full,outlook,webmail",
        ),
        _rich_entry(
            category="EMAIL",
            title="Cannot send email",
            subcategory="Mail send failure",
            summary="User can open mailbox but outgoing messages fail or stay in outbox.",
            causes="oversized attachment, offline client, mailbox quota, invalid recipient, cached credentials, or send limit.",
            steps=[
                "Check whether webmail can send a small test message.",
                "Remove large attachments and retry with a cloud link if possible.",
                "Confirm the recipient address is valid.",
                "Restart the mail client and verify it is not in offline mode.",
            ],
            escalate="webmail also cannot send, the mailbox is blocked, or delivery errors mention policy/quarantine.",
            keywords="cannot send mail,email send failed,outbox,attachment,mailbox full,outlook,webmail,recipient",
        ),
        _rich_entry(
            category="EMAIL",
            title="Mailbox full or quota exceeded",
            subcategory="Mailbox quota",
            summary="User receives quota warnings or cannot send/receive due to mailbox size.",
            causes="large attachments, old mailbox folders, retention gaps, or deleted items not emptied.",
            steps=[
                "Check mailbox quota in webmail or account settings.",
                "Sort by largest messages and remove or archive old attachments.",
                "Empty deleted items if company policy allows.",
                "Retry sending and receiving after quota updates.",
            ],
            escalate="quota does not update, retention/legal hold rules apply, or additional archive licensing is needed.",
            keywords="mailbox full,quota exceeded,email quota,cannot send,cannot receive,outlook,archive,storage",
        ),
        _rich_entry(
            category="EMAIL",
            title="Mobile email setup or sync issue",
            subcategory="Mobile mail",
            summary="Email works on desktop or webmail but not on the phone/tablet.",
            causes="old password, missing device compliance, blocked mail app, MFA registration, or stale mobile profile.",
            steps=[
                "Confirm webmail works from a browser.",
                "Use the approved mobile mail app and sign in with company credentials.",
                "Complete MFA and device compliance prompts.",
                "Remove and re-add the account if sync remains stuck.",
            ],
            escalate="device compliance fails, MFA is unavailable, or the device needs mobile management remediation.",
            keywords="mobile mail,phone email,ios,android,outlook mobile,email sync,mfa,device compliance",
        ),
        _rich_entry(
            category="DEVICE_PERFORMANCE",
            title="Slow startup on company laptop",
            subcategory="Startup performance",
            summary="Laptop takes a long time to boot or become usable after sign-in.",
            causes="too many startup apps, pending updates, encrypted disk checks, low storage, or endpoint security scan.",
            steps=[
                "Restart once and allow pending updates to finish.",
                "Close unnecessary startup applications.",
                "Confirm at least ten percent disk space is free.",
                "Note whether the slowdown happens before login, after login, or only when opening a specific app.",
            ],
            escalate="startup remains unusable after updates and free disk cleanup or disk health warnings appear.",
            keywords="slow startup,laptop slow,boot slow,startup apps,updates,disk,performance",
        ),
        _rich_entry(
            category="DEVICE_PERFORMANCE",
            title="High CPU or memory usage",
            subcategory="Resource usage",
            summary="Device is slow, fans are loud, or apps freeze because CPU or memory is saturated.",
            causes="browser tabs, video meeting app, sync client, endpoint scan, memory leak, or outdated app.",
            steps=[
                "Open Task Manager or Activity Monitor and identify the top CPU/memory process.",
                "Close unused browser tabs and heavy apps.",
                "Restart the affected app, then the device if usage stays high.",
                "Install pending app or OS updates outside active work hours.",
            ],
            escalate="a business app repeatedly consumes high resources or the device freezes after restart.",
            keywords="high cpu,high memory,task manager,activity monitor,fan loud,laptop slow,freezing,performance",
        ),
        _rich_entry(
            category="DEVICE_PERFORMANCE",
            title="Low disk storage on laptop",
            subcategory="Storage",
            summary="Device warns that storage is low or apps fail because disk space is nearly full.",
            causes="large downloads, cached Teams/Outlook data, old installers, local sync folders, or logs.",
            steps=[
                "Check free disk space and target at least ten percent free.",
                "Delete approved temporary files and old installers.",
                "Move business documents to the approved cloud drive instead of local downloads.",
                "Empty recycle bin if allowed by policy.",
            ],
            escalate="disk remains full after cleanup or business data migration/retention guidance is needed.",
            keywords="low storage,disk full,no space,laptop slow,storage,downloads,temp files,onedrive",
        ),
        _rich_entry(
            category="DEVICE_PERFORMANCE",
            title="Laptop overheating or battery drains quickly",
            subcategory="Hardware health",
            summary="Laptop becomes hot, fan runs constantly, or battery drains faster than expected.",
            causes="high CPU workload, blocked vents, old battery, docking issue, charger problem, or background scan.",
            steps=[
                "Check for high CPU usage and close heavy apps.",
                "Use the approved charger and avoid blocked vents.",
                "Restart after pending updates complete.",
                "Compare behavior on battery and plugged in.",
            ],
            escalate="battery health warnings appear, the laptop shuts down unexpectedly, or overheating continues after workload is reduced.",
            keywords="overheating,battery drain,fan,laptop hot,charger,power,battery issue,performance",
        ),
        _rich_entry(
            category="BROWSER",
            title="Internal website not opening",
            subcategory="Internal web access",
            summary="A company intranet or internal web app does not load.",
            causes="VPN not connected, DNS cache, browser cache, SSO session issue, certificate warning, or app outage.",
            steps=[
                "Confirm whether the site requires VPN or office network.",
                "Try a private browser window.",
                "Clear cache and cookies for the affected site only.",
                "Test another approved browser and capture the exact URL/error.",
            ],
            escalate="the site fails for multiple users, certificate warnings appear, or access is time-sensitive.",
            keywords="internal website,intranet,company portal,site not opening,browser,vpn,dns,cache,cookies",
        ),
        _rich_entry(
            category="BROWSER",
            title="Browser certificate warning on company site",
            subcategory="Certificate warning",
            summary="Browser warns that a site is not private, certificate expired, or connection is not secure.",
            causes="expired certificate, SSL inspection issue, wrong system time, captive portal, or malicious redirect.",
            steps=[
                "Do not bypass the warning for company apps.",
                "Check system date and time.",
                "Try the official bookmarked URL in a private browser window.",
                "Capture the certificate warning text and affected URL.",
            ],
            escalate="certificate is expired, the warning appears on a company app, or suspicious redirect is suspected.",
            keywords="certificate warning,not private,ssl,tls,browser,company site,expired certificate,security",
        ),
        _rich_entry(
            category="BROWSER",
            title="Browser compatibility issue with enterprise app",
            subcategory="Compatibility",
            summary="A web app opens in one browser but fails or displays incorrectly in another.",
            causes="unsupported browser, old browser version, extension conflict, blocked third-party cookies, or compatibility mode.",
            steps=[
                "Try the app in the company-recommended browser.",
                "Update the browser if allowed.",
                "Disable extensions temporarily or test in private mode.",
                "Allow required cookies only for the trusted company app if policy permits.",
            ],
            escalate="the app is business-critical or vendor/browser compatibility needs admin configuration.",
            keywords="browser compatibility,chrome,edge,firefox,safari,extension,cookies,web app,not loading",
        ),
        _rich_entry(
            category="SOFTWARE",
            title="Application install failed from software center",
            subcategory="Software install",
            summary="Approved app installation fails from the company software portal.",
            causes="missing license, device not compliant, insufficient disk, pending reboot, or failed package deployment.",
            steps=[
                "Confirm the app is being installed from the approved software portal.",
                "Restart the device if a reboot is pending.",
                "Check free disk space and network connection.",
                "Capture the installer error code and app name.",
            ],
            escalate="license assignment, admin approval, or device management remediation is required.",
            keywords="install failed,software center,company portal,application install,error code,license,device compliance",
        ),
        _rich_entry(
            category="SOFTWARE",
            title="Application permission denied on launch",
            subcategory="App permissions",
            summary="Application opens or installs but denies access when launched.",
            causes="missing app role, license not assigned, local permission issue, expired session, or wrong account.",
            steps=[
                "Confirm the user is signed in with the company account.",
                "Sign out and back into the application.",
                "Try the app in a private browser if it has a web version.",
                "Capture the app name, version, and permission error.",
            ],
            escalate="license or role assignment is needed, or the app stores regulated/business-critical data.",
            keywords="permission denied,app access,license,role,software,application,launch,access denied",
        ),
        _rich_entry(
            category="SOFTWARE",
            title="App version mismatch or update required",
            subcategory="Version management",
            summary="Application fails because the installed version is outdated or incompatible.",
            causes="missed update, stale installer, unsupported OS version, or server/client version mismatch.",
            steps=[
                "Check the installed app version.",
                "Install updates from the approved software portal.",
                "Restart the app and device after updating.",
                "Confirm the OS version meets the app requirement.",
            ],
            escalate="the software portal does not offer the required version or the device cannot meet OS requirements.",
            keywords="version mismatch,update required,outdated app,software update,application version,install",
        ),
        _rich_entry(
            category="PRINTER",
            title="Printer driver missing or wrong printer selected",
            subcategory="Printer driver",
            summary="User cannot print because the printer is missing, unavailable, or using the wrong driver.",
            causes="driver not installed, printer queue removed, wrong default printer, network change, or print server issue.",
            steps=[
                "Confirm the printer name and location.",
                "Select the correct company printer queue.",
                "Restart the app and retry a small test page.",
                "If available, reinstall the printer from the approved printer portal.",
            ],
            escalate="the printer queue is missing for multiple users or driver installation requires admin/device management action.",
            keywords="printer driver,missing printer,default printer,print queue,printer portal,cannot print",
        ),
        _rich_entry(
            category="PRINTER",
            title="Print queue stuck on device",
            subcategory="Print queue",
            summary="Documents stay in the local print queue and never print.",
            causes="stuck print job, offline printer, driver crash, paper/jam alert, or print spooler issue.",
            steps=[
                "Cancel stuck jobs and retry one small test page.",
                "Check whether the printer display shows paper, toner, jam, or offline status.",
                "Restart the app and the printer if allowed.",
                "Try another printer to separate device and printer queue issues.",
            ],
            escalate="jobs are stuck for multiple users or the print server queue is blocked.",
            keywords="print queue stuck,spooler,printer offline,cannot print,stuck job,paper jam,toner",
        ),
        _rich_entry(
            category="PRINTER",
            title="Cannot scan to email or folder",
            subcategory="Scanning",
            summary="Printer can print but scanning to email or a shared folder fails.",
            causes="wrong destination, badge/login issue, mailbox policy, SMB folder permission, or scanner address book problem.",
            steps=[
                "Confirm printing works to the same device.",
                "Sign out and back into the printer panel.",
                "Verify the destination email or shared folder path.",
                "Try a small one-page scan and capture the panel error.",
            ],
            escalate="folder permissions, scanner address book, or mail relay configuration must be changed.",
            keywords="scan to email,scanner,secure print,badge,folder,printer panel,cannot scan",
        ),
        _rich_entry(
            category="GENERAL",
            title="Shared drive or network folder not accessible",
            subcategory="File access",
            summary="User cannot open a mapped drive, shared folder, or department file path.",
            causes="VPN disconnected, missing group permission, stale mapped drive, DNS issue, or file server outage.",
            steps=[
                "Confirm VPN or office network is connected if the drive is internal.",
                "Try the full folder path instead of a stale mapped drive.",
                "Ask whether other users in the same team can access the folder.",
                "Capture the exact path and error message.",
            ],
            escalate="permission changes or file server checks are required.",
            keywords="shared drive,network folder,file share,mapped drive,permission,path,folder access,vpn",
        ),
        _rich_entry(
            category="GENERAL",
            title="Company portal does not load",
            subcategory="Company portal",
            summary="Employee portal, service catalog, or company homepage does not open.",
            causes="browser cache, SSO loop, VPN requirement, service outage, proxy issue, or stale session.",
            steps=[
                "Try a private browser window.",
                "Clear cookies for the company portal only.",
                "Check whether VPN or office network is required.",
                "Try another approved browser and capture the exact URL/error.",
            ],
            escalate="the portal is unavailable for multiple users or a business-critical request is blocked.",
            keywords="company portal,service catalog,employee portal,not loading,sso,browser,cache,vpn",
        ),
        _rich_entry(
            category="GENERAL",
            title="HR system login issue",
            subcategory="HR application",
            summary="User cannot access the HR system for employee profile, time off, or onboarding tasks.",
            causes="missing HR role, stale SSO session, MFA issue, browser cache, or HR system outage.",
            steps=[
                "Confirm the user can sign in to SSO generally.",
                "Try the HR system from a private browser window.",
                "Capture whether the error is login failure, access denied, or page not loading.",
                "Confirm whether the user is a new hire or recently changed roles.",
            ],
            escalate="role assignment or HR data access needs approval, or payroll/time-sensitive work is blocked.",
            keywords="hr system,hr portal,workday,employee profile,time off,onboarding,login,access denied",
        ),
        _rich_entry(
            category="GENERAL",
            title="Payroll portal access issue",
            subcategory="Payroll",
            summary="User cannot access payroll, payslip, timesheet, or compensation portal.",
            causes="missing payroll role, SSO/MFA issue, browser session problem, or payroll app outage.",
            steps=[
                "Confirm SSO and MFA work for other apps.",
                "Try the payroll portal in a private browser window.",
                "Capture the exact error and whether access worked previously.",
                "Ask whether this is blocking a payroll cutoff or time submission deadline.",
            ],
            escalate="payroll deadline, access denied, or role/group change is required.",
            keywords="payroll,payslip,timesheet,compensation,access blocked,portal,login,urgent,cannot work",
        ),
        _rich_entry(
            category="GENERAL",
            title="Video meeting app audio or join issue",
            subcategory="Meeting app",
            summary="User cannot join, hear audio, use microphone/camera, or launch a video meeting app.",
            causes="browser permission, app update required, wrong audio device, network block, or stale meeting plugin.",
            steps=[
                "Confirm whether the issue is joining, audio, camera, or screen sharing.",
                "Restart the meeting app and browser.",
                "Check microphone/camera permissions and selected audio device.",
                "Try the web version or another approved browser.",
            ],
            escalate="multiple users cannot join the same meeting or device permissions cannot be fixed by the user.",
            keywords="teams,zoom,video meeting,audio,microphone,camera,screen share,meeting app,join meeting",
        ),
    ]
)
