Email sender spoofing: how it works, how to prevent it, and how to test safely

Purpose
- This document explains email sender spoofing at a practical level, what attacker infrastructure is needed, and how to prevent it with modern controls (SPF, DKIM, DMARC, TLS, ARC, etc.).
- A lab-only simulator script (`spoof.py`) is provided to help defenders understand the mechanics in a safe environment. It refuses to send to the public Internet and only works with a local debug SMTP server.

What is sender spoofing?
- Email has two key identities:
  - Envelope sender (SMTP MAIL FROM / return-path): used for bounce handling and SPF.
  - Header sender (`From:`): displayed to users and used for DMARC alignment with DKIM/SPF.
- Classic spoofing forges the visible `From:` and/or the envelope sender, then delivers mail directly to the recipient’s MX servers or via a misconfigured relay.

Typical attacker architectures
- Direct-to-MX delivery
  - Use DNS MX lookup for victim domain → open TCP 25 → speak SMTP → set `MAIL FROM:<attacker>` and `From: CEO <ceo@victim.com>` → deliver.
  - Works only when the recipient’s side doesn’t enforce DMARC or the message passes via a forwarder that breaks alignment.
- Open relay or misconfigured MTA
  - Abuse an SMTP server that relays without authentication or has permissive rules.
  - Increasingly rare but still found in legacy systems/IOT. Strongly blocked by outbound port 25 egress filtering.
- Compromised or abused legitimate sender
  - Real account at the victim or trusted partner sends legit-authenticated mail. DKIM/SPF/DMARC pass, making it hard to filter. This is BEC (Business Email Compromise) territory.
- Third-party sending services without strict verification
  - Services that allow setting arbitrary `From:` without enforcing domain ownership.

How prevention works
- Publish and enforce authentication
  - SPF: Publish a complete record covering all legitimate outbound sources, end with `-all` (hard fail). Example: `v=spf1 ip4:203.0.113.0/24 include:spf.sender.example -all`.
  - DKIM: Sign all outbound mail with a sufficiently long key (RSA 2048 or Ed25519). Rotate keys regularly; disable weak/old selectors.
  - DMARC: Enforce alignment and policy. Start at `p=none` with monitoring, then move to `p=quarantine` → `p=reject`. Add `rua` aggregate reports and optionally `ruf` forensic reports.
    - Example: `v=DMARC1; p=reject; sp=reject; adkim=s; aspf=s; rua=mailto:dmarc-agg@example.com; fo=1`.
- Handles and forwarding
  - Implement ARC on forwarders and mailing lists; ensure SRS for forwarders that rewrite envelope sender so SPF can survive.
  - Align subdomain policy with `sp=` tag in DMARC. Block cousin/lookalike domains with brand monitoring and inbound rules.
- Inbound policy and UX
  - Treat DMARC-aligned pass as strong signal; quarantine or reject fails. Annotate external mail (e.g., add banner for `From:` outside your domain).
  - Normalize display in clients to show the real address, not just display name. Warn on mismatched display name vs. domain.
  - Enforce TLS for SMTP (MTA-STS + TLS-RPT) to prevent downgrade/mitm.
- Outbound hygiene
  - No open relay. Require SMTP AUTH with strong credentials and MFA where possible. Rate-limit and monitor.
  - Block direct egress to TCP/25 from user subnets; only MTAs should reach the Internet on 25.

Why spoofing still sometimes lands
- Missing or lax DMARC policy (p=none or not aligned).
- Forwarders that break DKIM and don’t use ARC/SRS.
- Recipient systems that check SPF/DKIM but do not enforce DMARC alignment (treating a pass without alignment as sufficient).
- UI tricks: lookalike domains, unicode homographs, display-name abuse.

Safe lab testing
1) Start a local debug SMTP server (does not deliver to the Internet):
   - Install: `pip install aiosmtpd`
   - Run: `python -m aiosmtpd -n -l localhost:1025`
   - The server will print any received messages to stdout.
2) Use the included simulator to craft a message with a forged `From:`:
   - Example:
     - `python mailspoof/spoof.py --from "CEO <ceo@example.com>" --envelope-from bounce@example.com --to user@example.com --subject "Quarterly Update" --body "This is a lab-only test."`
   - The script enforces:
     - SMTP host must be `localhost` or `127.0.0.1`.
     - All addresses must use reserved lab domains: `example.com`, `example.org`, `example.net`, or TLD `.test`.
     - You can also run in dry-run to print the MIME and SMTP transaction without sending: add `--dry-run`.

How a simple Python spoofing script would work (conceptual)
- Resolve recipient domain’s MX records (e.g., with `dns.resolver`).
- Connect to the MX on TCP 25 and speak SMTP:
  - `HELO`/`EHLO`
  - `MAIL FROM:<envelope@attacker>`
  - `RCPT TO:<victim@domain>`
  - `DATA` → send headers including a forged `From:` → end with `\r\n.\r\n`
  - `QUIT`
- If the recipient’s domain does not enforce DMARC reject/quarantine and nothing else blocks it, the message may be accepted. This is why DMARC enforcement plus alignment matters.

What to look for in headers (receiver side)
- `Authentication-Results:` shows SPF/DKIM/DMARC results and alignment.
- `Return-Path:` is set by the receiver from the SMTP envelope sender.
- Misalignment examples:
  - `From: CEO <ceo@victim.com>` but `Return-Path: bounce@random-attacker.tld` and DKIM signing domain not aligned → DMARC fail.

Checklist for defenders
- Publish SPF covering all senders; end with `-all`.
- DKIM-sign everywhere; rotate keys.
- DMARC with `p=reject` (after ramp-up) and strict alignment `aspf=s adkim=s`.
- Enforce inbound DMARC policy; quarantine/reject fails.
- Deploy MTA-STS and TLS-RPT; monitor for downgrade attempts.
- Annotate external mail; flag mismatched display names.
- Implement ARC/SRS for forwarders and lists; prefer providers that do.
- Block outbound TCP/25 from user networks.
- Monitor DMARC aggregate reports and tune continuously.

Legal and ethical use
- Only perform spoofing tests against systems and domains you own or have written authorization to test. Unauthorized spoofing can be illegal and harmful.
- The included script is intentionally restricted to a local lab environment to prevent misuse.


