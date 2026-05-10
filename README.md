# leader-TCP_proxy_V1.1
feat: add packet manipulation and user-agent spoofing capability.

### 🛡️ Advanced Feature: Packet Manipulation (User-Agent Spoofing)
Unlike a simple TCP relay, this proxy now includes a dynamic **Request Handler** that demonstrates a real-world "Man-in-the-Middle" (MITM) attack. 

**How it works:**
The proxy scans every incoming packet from the client for specific patterns. In this update, it identifies the browser's identity (**User-Agent**) and replaces it on-the-fly before it reaches the remote server.

**Example Scenario:**
* **Original Request:** Sent from a Linux-based Firefox browser.
* **Intercepted & Modified:** The proxy swaps the Linux identity with an **iPhone (iOS 17)** signature.
* **Server-side Impact:** The remote server treats the connection as if it originated from a mobile device, which can bypass certain OS-specific restrictions or Web Application Firewalls (WAF).

> **Note:** This logic can be easily extended to modify passwords, inject scripts, or fuzz parameters for vulnerability research.
