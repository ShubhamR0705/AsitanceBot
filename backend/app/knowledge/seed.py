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
