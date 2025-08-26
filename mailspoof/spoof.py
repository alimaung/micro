#!/usr/bin/env python3
"""
Lab-only email spoofing simulator.

This script demonstrates the mechanics of forging the header From and the SMTP
envelope sender in a controlled environment. It is intentionally restricted:

- It only connects to localhost (127.0.0.1) on a user-specified port (default 1025).
- It only accepts addresses in reserved example domains (example.com/.org/.net)
  or the .test TLD.
- It supports a dry-run mode that prints the composed MIME message and the
  intended SMTP transaction without sending.

Intended use: run with a local debug SMTP server, e.g.:
  python -m aiosmtpd -n -l localhost:1025

Legal/Ethical: Do not use this to target external systems or real recipients.
"""

from __future__ import annotations

import argparse
import ipaddress
import re
import smtplib
import sys
from email.message import EmailMessage
from typing import Iterable


RESERVED_DOMAIN_PATTERN = re.compile(
    r"(^|@)([^@>]+@)?((example\.com)|(example\.org)|(example\.net)|([^.@\s]+\.test))$",
    re.IGNORECASE,
)


def is_localhost(host: str) -> bool:
    try:
        # Allow literal IPv4/IPv6 localhost and hostname 'localhost'
        if host.lower() == "localhost":
            return True
        ip = ipaddress.ip_address(host)
        return ip.is_loopback
    except ValueError:
        # Not an IP, only allow hostname 'localhost'
        return host.lower() == "localhost"


def validate_lab_address(addr: str) -> None:
    # Minimal sanity check for RFC5322-like mailbox and domain policy
    if not addr or "@" not in addr:
        raise ValueError(f"Invalid email address: {addr}")
    # Extract domain part (handles simple display name cases like 'Name <a@b>')
    candidate = addr
    m = re.search(r"<([^>]+)>", addr)
    if m:
        candidate = m.group(1)
    domain = candidate.split("@")[-1].strip()
    if not RESERVED_DOMAIN_PATTERN.search(domain):
        raise ValueError(
            "Address must use a reserved lab domain: example.com/.org/.net or .test"
        )


def validate_lab_addresses(addresses: Iterable[str]) -> None:
    for a in addresses:
        validate_lab_address(a)


def build_message(
    header_from: str,
    to_addrs: list[str],
    subject: str,
    body: str,
    header_reply_to: str | None,
    extra_headers: list[tuple[str, str]] | None,
) -> EmailMessage:
    msg = EmailMessage()
    msg["From"] = header_from
    msg["To"] = ", ".join(to_addrs)
    msg["Subject"] = subject
    if header_reply_to:
        msg["Reply-To"] = header_reply_to
    if extra_headers:
        for k, v in extra_headers:
            # Basic safety: prevent header injection via newlines
            if "\n" in k or "\r" in k or "\n" in v or "\r" in v:
                raise ValueError("Header values must not contain CR/LF")
            msg[k] = v
    msg.set_content(body)
    return msg


def dry_run_print(envelope_from: str, to_addrs: list[str], host: str, port: int, msg: EmailMessage) -> None:
    print("Dry-run: would connect to SMTP server", host, port)
    print("MAIL FROM:", envelope_from)
    for rcpt in to_addrs:
        print("RCPT TO:", rcpt)
    print("\nComposed message:\n")
    sys.stdout.write(msg.as_string())
    print()


def send_message(envelope_from: str, to_addrs: list[str], host: str, port: int, msg: EmailMessage) -> None:
    if not is_localhost(host):
        raise RuntimeError("SMTP host must be localhost or 127.0.0.1 for lab safety")
    with smtplib.SMTP(host=host, port=port, timeout=10) as client:
        client.ehlo()
        # Intentionally do not start TLS; many debug servers are plain TCP
        client.send_message(msg, from_addr=envelope_from, to_addrs=to_addrs)


def parse_extra_headers(hlist: list[str]) -> list[tuple[str, str]]:
    parsed: list[tuple[str, str]] = []
    for h in hlist:
        if ":" not in h:
            raise ValueError(f"Invalid header format (expected 'Key: Value'): {h}")
        key, value = h.split(":", 1)
        parsed.append((key.strip(), value.strip()))
    return parsed


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Lab-only email spoofing simulator (local SMTP only)",
    )
    parser.add_argument("--smtp-host", default="localhost", help="SMTP host (must be localhost)")
    parser.add_argument("--smtp-port", type=int, default=1025, help="SMTP port (default 1025)")
    parser.add_argument("--from", dest="header_from", required=True, help="Header From (what recipients see)")
    parser.add_argument("--envelope-from", dest="envelope_from", required=True, help="Envelope MAIL FROM (return-path)")
    parser.add_argument("--to", dest="to_addrs", required=True, nargs="+", help="Recipient addresses")
    parser.add_argument("--subject", default="Lab Test", help="Message subject")
    parser.add_argument("--body", default="This is a lab-only test message.", help="Plain text body")
    parser.add_argument("--reply-to", dest="reply_to", help="Optional Reply-To header")
    parser.add_argument(
        "--header",
        dest="extra_headers",
        action="append",
        default=[],
        help="Additional header in 'Key: Value' format; can be repeated",
    )
    parser.add_argument("--dry-run", action="store_true", help="Do not send; print MIME and transaction")

    args = parser.parse_args(argv)

    # Validate safety constraints
    if not is_localhost(args.smtp_host):
        print("Error: SMTP host must be localhost for lab safety.", file=sys.stderr)
        return 2
    try:
        validate_lab_addresses([args.header_from, args.envelope_from, *(args.to_addrs)])
        if args.reply_to:
            validate_lab_address(args.reply_to)
        extra_headers = parse_extra_headers(list(args.extra_headers)) if args.extra_headers else []
    except Exception as exc:  # noqa: BLE001 - concise CLI
        print(f"Error: {exc}", file=sys.stderr)
        return 2

    msg = build_message(
        header_from=args.header_from,
        to_addrs=list(args.to_addrs),
        subject=args.subject,
        body=args.body,
        header_reply_to=args.reply_to,
        extra_headers=extra_headers,
    )

    if args.dry_run:
        dry_run_print(args.envelope_from, list(args.to_addrs), args.smtp_host, args.smtp_port, msg)
        return 0

    try:
        send_message(args.envelope_from, list(args.to_addrs), args.smtp_host, args.smtp_port, msg)
    except Exception as exc:  # noqa: BLE001
        print(f"SMTP error: {exc}", file=sys.stderr)
        return 1
    print("Message sent to local server.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


