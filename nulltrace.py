#!/usr/bin/env python3
# ╔══════════════════════════════════════════════════════════════════╗
# ║   NullTrace — Web Recon & Intelligence Toolkit                 ║
# ║   Maintained by : krypthane | wavegxz-design                   ║
# ║   GitHub        : github.com/wavegxz-design                    ║
# ║   Telegram      : t.me/Skrylakk                                ║
# ║   Email         : Workernova@proton.me                         ║
# ║   Location      : Mexico 🇲🇽 UTC-6                             ║
# ║                                                                 ║
# ║   Migrated & cleaned from hacktronian (Python 2 → Python 3)    ║
# ║                                                                 ║
# ║   Bugs fixed:                                                   ║
# ║   [BUG-01] Full Python 2→3 migration (urllib2,raw_input,etc)   ║
# ║   [BUG-02] unique() defined 3x → single utility function       ║
# ║   [BUG-03] bing_all_grabber() defined 3x → single function     ║
# ║   [BUG-04] check_wordpress() defined 2x → deduplicated         ║
# ║   [BUG-05] wpsycmium typo → wpsymposium (NameError fix)        ║
# ║   [BUG-06] portScanner() outside class with self → inside      ║
# ║   [BUG-07] menu() defined 2x → single clean menu               ║
# ║   [BUG-08] cmsscan @@ → && (broken shell cmd fix)              ║
# ║   [BUG-09] fluxion mixed tabs/spaces → removed (broken)        ║
# ║   [BUG-10] os.system('clear') x4 → single subprocess call      ║
# ║   [BUG-11] bcolors/colors empty stubs → real Color class        ║
# ║   [BUG-12] urllib2.HTTPError,e → except Exception as e          ║
# ║   [BUG-13] except(),message → except Exception as e             ║
# ║   [BUG-14] print statements → print() functions                 ║
# ║   [BUG-15] no timeouts on network calls → timeout=8s            ║
# ║                                                                 ║
# ║   Removed (malicious / unsafe):                                 ║
# ║   - drupal()/drupallist(): sends targets to C2 server           ║
# ║   - gabriel/sitechecker/vbulletinrce/joomlarce: wget+exec       ║
# ║   - smtpsend/pisher: wget+exec from pastebin                    ║
# ║   - webshells list + findUp webshell finder                     ║
# ║                                                                 ║
# ║   Authorized use only. Ethical hacking only.                    ║
# ╚══════════════════════════════════════════════════════════════════╝

import sys
import os
import re
import time
import socket
import threading
import subprocess
import json
from datetime import datetime
from urllib.parse import urlparse
from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError
from http.client import HTTPConnection
from platform import system

# ── VERSION ────────────────────────────────────────────────────────
VERSION = "1.0"

# ── COLORS ─────────────────────────────────────────────────────────
# FIX [BUG-11]: bcolors and colors were empty stubs — never colored anything
class C:
    R  = "\033[38;5;196m"
    G  = "\033[38;5;46m"
    GD = "\033[38;5;34m"
    CY = "\033[38;5;51m"
    MG = "\033[38;5;213m"
    WH = "\033[1;97m"
    YL = "\033[38;5;226m"
    DM = "\033[38;5;240m"
    BL = "\033[38;5;27m"
    RS = "\033[0m"
    BOLD = "\033[1m"

# ── TIMEOUT ────────────────────────────────────────────────────────
# FIX [BUG-15]: all network calls now use this timeout
NET_TIMEOUT = 8

# ── UTILITIES ──────────────────────────────────────────────────────
# FIX [BUG-02/03/04]: unique(), bing_all_grabber(), check_wordpress()
# were each defined 2-3 times. Single clean version here.

def clear():
    """FIX [BUG-10]: was os.system('clear') called 4x at startup."""
    try:
        subprocess.run(["cls" if os.name == "nt" else "clear"], check=False)
    except Exception:
        pass


def unique(seq: list) -> list:
    """Return list with duplicates removed, preserving order."""
    seen = set()
    result = []
    for x in seq:
        if x not in seen:
            seen.add(x)
            result.append(x)
    return result


def bing_all_grabber(ip: str) -> list:
    """
    Enumerate sites hosted on a given IP via Bing.
    FIX [BUG-01]: urllib2 → urllib.request
    FIX [BUG-15]: timeout added
    """
    lista = []
    page  = 1
    headers = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"}
    while page <= 101:
        try:
            url  = f"http://www.bing.com/search?q=ip%3A{ip}+&count=50&first={page}"
            req  = Request(url, headers=headers)
            html = urlopen(req, timeout=NET_TIMEOUT).read().decode("utf-8", errors="ignore")
            found = re.findall(r'<h2><a href="(.*?)"', html)
            for item in found:
                parts = re.findall(r'http://(.*?)/', item)
                for p in parts:
                    if "www" not in p:
                        lista.append(f"http://www.{p}/")
                    else:
                        lista.append(f"http://{p}/")
            page += 50
        except (URLError, HTTPError, Exception):
            page += 50
            continue
    return unique(lista)


def check_wordpress(sites: list) -> list:
    """Check which sites run WordPress."""
    wp = []
    for site in sites:
        try:
            if urlopen(site + "wp-login.php", timeout=NET_TIMEOUT).getcode() == 200:
                wp.append(site)
        except Exception:
            pass
    return wp


def check_joomla(sites: list) -> list:
    """Check which sites run Joomla."""
    joomla = []
    for site in sites:
        try:
            if urlopen(site + "administrator", timeout=NET_TIMEOUT).getcode() == 200:
                joomla.append(site)
        except Exception:
            pass
    return joomla


# ── LOGO ───────────────────────────────────────────────────────────
LOGO = f"""
{C.CY}  ███╗   ██╗██╗   ██╗██╗     ██╗  ████████╗██████╗  █████╗  ██████╗███████╗
{C.CY}  ████╗  ██║██║   ██║██║     ██║  ╚══██╔══╝██╔══██╗██╔══██╗██╔════╝██╔════╝
{C.MG}  ██╔██╗ ██║██║   ██║██║     ██║     ██║   ██████╔╝███████║██║     █████╗
{C.MG}  ██║╚██╗██║██║   ██║██║     ██║     ██║   ██╔══██╗██╔══██║██║     ██╔══╝
{C.CY}  ██║ ╚████║╚██████╔╝███████╗███████╗██║   ██║  ██║██║  ██║╚██████╗███████╗
{C.CY}  ╚═╝  ╚═══╝ ╚═════╝ ╚══════╝╚══════╝╚═╝   ╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝╚══════╝
{C.DM}  ╔══════════════════════════════════════════════════════════════════════════╗
{C.DM}  ║{C.WH}  Web Recon & Intelligence Toolkit             {C.YL}v{VERSION}               {C.DM}║
{C.DM}  ╠══════════════════════════════════════════════════════════════════════════╣
{C.DM}  ║{C.WH}  Author    : {C.G}krypthane{C.DM} · wavegxz-design                            ║
{C.DM}  ║{C.WH}  GitHub    : {C.CY}github.com/wavegxz-design                                ║
{C.DM}  ║{C.WH}  Telegram  : {C.CY}t.me/Skrylakk                                            ║
{C.DM}  ║{C.G}  ⚑ Authorized use only — Ethical hacking only                          {C.DM}║
{C.DM}  ╚══════════════════════════════════════════════════════════════════════════╝{C.RS}
"""

def show_logo():
    clear()
    print(LOGO)


# ══════════════════════════════════════════════════════════════════
# MODULE 1 — INFORMATION GATHERING
# ══════════════════════════════════════════════════════════════════

def host_to_ip():
    """Resolve hostname to IP address."""
    host = input(C.WH + "  Hostname: " + C.RS).strip()
    if not host:
        return
    try:
        ip = socket.gethostbyname(host)
        print(C.G + f"\n  [+] {host} → {ip}" + C.RS)
    except socket.gaierror as e:
        print(C.R + f"\n  [!] Could not resolve: {e}" + C.RS)


def port_scan_simple():
    """
    Simple port scanner.
    FIX [BUG-01]: socket usage modernized.
    FIX [BUG-15]: timeout added per socket.
    """
    target = input(C.WH + "  Target IP: " + C.RS).strip()
    if not target:
        return
    print(C.DM + "  Range examples: 1-1000  or  80  or leave blank for common ports" + C.RS)
    rng = input(C.WH + "  Port range (Enter = common): " + C.RS).strip()

    if rng:
        try:
            parts = rng.split("-")
            start, end = (int(parts[0]), int(parts[1])) if len(parts) == 2 else (int(rng), int(rng))
        except ValueError:
            print(C.R + "\n  [!] Invalid range." + C.RS)
            return
        ports = range(start, end + 1)
    else:
        ports = [21, 22, 23, 25, 53, 80, 110, 143, 443, 445, 3306, 3389, 8080, 8443]

    print(C.GD + f"\n  ── Scanning {target} ──\n" + C.RS)
    open_ports = []

    def probe(port):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(1)
            if s.connect_ex((target, port)) == 0:
                open_ports.append(port)
                print(C.G + f"  [OPEN]  {port}" + C.RS)
            s.close()
        except Exception:
            pass

    threads = []
    for p in ports:
        t = threading.Thread(target=probe, args=(p,), daemon=True)
        t.start()
        threads.append(t)
    for t in threads:
        t.join()

    if not open_ports:
        print(C.DM + "  No open ports found." + C.RS)
    else:
        print(C.GD + f"\n  Found {len(open_ports)} open port(s)." + C.RS)


def server_banner():
    """Grab HTTP server banner."""
    target = input(C.WH + "  Target (IP or domain): " + C.RS).strip()
    if not target:
        return
    url = target if target.startswith("http") else f"http://{target}"
    try:
        resp = urlopen(url, timeout=NET_TIMEOUT)
        banner = resp.headers.get("Server", "N/A")
        powered = resp.headers.get("X-Powered-By", "N/A")
        print(C.G  + f"\n  [+] Server      : {banner}" + C.RS)
        print(C.G  + f"  [+] X-Powered-By: {powered}" + C.RS)
        print(C.DM + f"  [i] Status      : {resp.getcode()}" + C.RS)
    except Exception as e:
        print(C.R + f"\n  [!] Error: {e}" + C.RS)


def cms_detect():
    """Detect CMS (WordPress / Joomla) on a target."""
    target = input(C.WH + "  Target URL (e.g. http://example.com): " + C.RS).strip()
    if not target:
        return
    if not target.endswith("/"):
        target += "/"

    checks = {
        "WordPress": [
            "wp-login.php", "wp-admin/", "wp-content/", "xmlrpc.php"
        ],
        "Joomla": [
            "administrator/", "components/", "modules/", "templates/"
        ],
        "Drupal": [
            "sites/default/", "modules/", "CHANGELOG.txt"
        ],
    }

    print(C.GD + f"\n  ── CMS Detection: {target} ──\n" + C.RS)
    detected = {}
    for cms, paths in checks.items():
        score = 0
        for path in paths:
            try:
                code = urlopen(target + path, timeout=NET_TIMEOUT).getcode()
                if code in (200, 403):
                    score += 1
            except Exception:
                pass
        if score >= 2:
            detected[cms] = score

    if detected:
        for cms, score in detected.items():
            print(C.G + f"  [+] {cms} detected (confidence: {score}/{len(checks[cms])})" + C.RS)
    else:
        print(C.DM + "  No CMS fingerprint detected." + C.RS)


def wp_user_enum():
    """Enumerate WordPress users via ?author= parameter."""
    target = input(C.WH + "  WordPress URL: " + C.RS).strip()
    if not target:
        return
    if not target.endswith("/"):
        target += "/"

    print(C.GD + f"\n  ── WP User Enum: {target} ──\n" + C.RS)
    found = []
    for i in range(1, 11):
        try:
            resp = urlopen(f"{target}?author={i}", timeout=NET_TIMEOUT)
            final_url = resp.geturl()
            match = re.search(r"/author/([^/]+)/", final_url)
            if match:
                user = match.group(1)
                found.append(user)
                print(C.G + f"  [+] User #{i}: {user}" + C.RS)
        except Exception:
            pass

    if not found:
        print(C.DM + "  No users found (or author enumeration disabled)." + C.RS)
    else:
        print(C.GD + f"\n  Found {len(found)} user(s)." + C.RS)


# ══════════════════════════════════════════════════════════════════
# MODULE 2 — SERVER RECON (Fscan)
# ══════════════════════════════════════════════════════════════════

class ServerRecon:
    """
    Enumerate sites and run recon on a shared hosting server.
    FIX [BUG-01]: urllib2 → urllib.request throughout.
    FIX [BUG-05]: wpsycmium typo fixed → wpsymposium.
    FIX [BUG-06]: portScanner now inside class (not standalone with self).
    FIX [BUG-13]: except(),message → except Exception as e.
    FIX [BUG-15]: timeout on all network calls.
    """

    def __init__(self, ip: str):
        self.ip    = ip
        self.sites = []

    def run(self):
        print(C.GD + f"\n  ── Server Recon: {self.ip} ──\n" + C.RS)
        self.sites = bing_all_grabber(self.ip)
        print(C.G + f"  [+] Found {len(self.sites)} site(s) on this server.\n" + C.RS)

        menu = {
            "1": ("Get all sites",           self.show_sites),
            "2": ("Detect WordPress",         self.detect_wp),
            "3": ("Detect Joomla",            self.detect_joomla),
            "4": ("Find admin panels",        self.find_panels),
            "5": ("Find zip/backup files",    self.find_zip),
            "6": ("Port scan",                self.port_scanner),
            "7": ("Server banner",            self.get_banner),
            "8": ("Cloudflare bypass check",  self.cloudflare_bypass),
            "9": ("SQL error scan",           self.sql_scan),
            "99": ("Back",                    None),
        }

        while True:
            print(C.DM + "\n  ┌──────────────────────────────────┐" + C.RS)
            for k, (label, _) in menu.items():
                color = C.R if k == "99" else C.WH
                print(C.DM + "  │" + color + f"  [{k:2}] {label}" + C.RS)
            print(C.DM + "  └──────────────────────────────────┘" + C.RS)

            choice = input(C.CY + "\n  nulltrace~# " + C.RS).strip()
            if choice == "99":
                break
            elif choice in menu:
                menu[choice][1]()
            else:
                print(C.R + "  [!] Invalid option." + C.RS)

    def show_sites(self):
        print(C.GD + f"\n  Sites on {self.ip}:\n" + C.RS)
        for s in self.sites:
            print(C.G + f"  {s}" + C.RS)

    def detect_wp(self):
        print(C.GD + "\n  Checking for WordPress...\n" + C.RS)
        wp = check_wordpress(self.sites)
        for s in wp:
            print(C.G + f"  [WP]  {s}" + C.RS)
        print(C.DM + f"\n  Found: {len(wp)}" + C.RS)

    def detect_joomla(self):
        print(C.GD + "\n  Checking for Joomla...\n" + C.RS)
        joomla = check_joomla(self.sites)
        for s in joomla:
            print(C.G + f"  [JM]  {s}" + C.RS)
        print(C.DM + f"\n  Found: {len(joomla)}" + C.RS)

    def find_panels(self):
        """Find common admin panel paths."""
        panels = [
            "admin/", "administrator/", "wp-admin/", "admincp/",
            "login/", "login.php", "cpanel/", "panel/", "control/",
            "webmaster/", "myadmin/", "adm/", "member/",
        ]
        print(C.GD + "\n  Scanning for admin panels...\n" + C.RS)
        found = 0
        for site in self.sites:
            for panel in panels:
                try:
                    code = urlopen(site + panel, timeout=NET_TIMEOUT).getcode()
                    if code == 200:
                        print(C.G + f"  [+] Admin panel → {site + panel}" + C.RS)
                        found += 1
                except Exception:
                    pass
        if not found:
            print(C.DM + "  No panels found." + C.RS)

    def find_zip(self):
        """Look for exposed backup / zip files."""
        zip_paths = [
            "backup.zip", "backup.tar.gz", "backup.sql", "backup.rar",
            "site.zip", "www.zip", "wordpress.zip", "joomla.zip",
            "db.sql", "database.sql", "dump.sql",
        ]
        print(C.GD + "\n  Scanning for backup/zip files...\n" + C.RS)
        found = 0
        for site in self.sites:
            for z in zip_paths:
                try:
                    code = urlopen(site + z, timeout=NET_TIMEOUT).getcode()
                    if code == 200:
                        print(C.G + f"  [+] Found → {site + z}" + C.RS)
                        found += 1
                except Exception:
                    pass
        if not found:
            print(C.DM + "  No backup files found." + C.RS)

    def port_scanner(self):
        """
        Port scanner — FIX [BUG-06]: was defined outside class with self.
        Now properly inside ServerRecon.
        """
        print(C.DM + "  Mode: (1) custom range  (2) common ports" + C.RS)
        try:
            mode = int(input(C.WH + "  Choice: " + C.RS).strip())
        except ValueError:
            return

        if mode == 1:
            rng = input(C.WH + "  Range (e.g. 1-1000): " + C.RS).strip()
            try:
                a, b = rng.split("-")
                ports = range(int(a), int(b) + 1)
            except Exception:
                print(C.R + "  [!] Invalid range." + C.RS)
                return
        else:
            ports = [21, 22, 23, 25, 53, 80, 110, 143, 443, 445, 3306, 3389, 8080]

        print(C.GD + f"\n  Scanning {self.ip}...\n" + C.RS)
        for port in ports:
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(0.8)
                if s.connect_ex((self.ip, port)) == 0:
                    print(C.G + f"  [OPEN]  {port}" + C.RS)
                s.close()
            except Exception:
                pass

    def get_banner(self):
        """Get HTTP server banner."""
        try:
            resp = urlopen(f"http://{self.ip}", timeout=NET_TIMEOUT)
            banner  = resp.headers.get("Server",       "N/A")
            powered = resp.headers.get("X-Powered-By", "N/A")
            print(C.G + f"\n  [+] Server      : {banner}" + C.RS)
            print(C.G + f"  [+] X-Powered-By: {powered}" + C.RS)
        except Exception as e:
            print(C.R + f"\n  [!] {e}" + C.RS)

    def cloudflare_bypass(self):
        """
        Check if Cloudflare-protected sub-domains reveal origin IP.
        FIX [BUG-01]: socket usage modernized.
        """
        print(C.GD + "\n  Checking for Cloudflare bypass...\n" + C.RS)
        subs = ["mail", "webmail", "ftp", "direct", "cpanel", "smtp", "pop"]
        for site in self.sites[:5]:  # limit to first 5
            domain = site.replace("http://", "").replace("https://", "").rstrip("/")
            try:
                origin_ip = socket.gethostbyname(domain)
            except Exception:
                continue
            for sub in subs:
                target = f"{sub}.{domain}"
                try:
                    sub_ip = socket.gethostbyname(target)
                    if sub_ip != origin_ip:
                        print(C.G + f"  [+] Possible bypass → {target} = {sub_ip}" + C.RS)
                except socket.error:
                    pass

    def sql_scan(self):
        """
        Test Bing-found URLs for SQL error-based injection indicators.
        FIX [BUG-01]: urllib2 → urllib.request.
        FIX [BUG-12]: except urllib2.HTTPError,e → except HTTPError as e.
        FIX [BUG-15]: timeout added.
        """
        print(C.GD + "\n  Collecting SQLi targets from Bing...\n" + C.RS)
        lista = []
        page  = 1
        headers = {"User-Agent": "Mozilla/5.0"}
        while page <= 51:
            try:
                url = (f"http://www.bing.com/search?q=ip%3A{self.ip}"
                       f"+php?id=&count=50&first={page}")
                req  = Request(url, headers=headers)
                html = urlopen(req, timeout=NET_TIMEOUT).read().decode("utf-8", errors="ignore")
                found = re.findall(r'<h2><a href="(.*?)"', html)
                lista.extend(found)
            except Exception:
                pass
            page += 50

        lista = unique(lista)
        print(C.DM + f"  Testing {len(lista)} URLs for SQL errors...\n" + C.RS)

        payloads = ["'", "\"", "' OR '1'='1", "' AND 1=2--"]
        errors   = re.compile(
            r"sql syntax|mysql_fetch|syntax error|unclosed.*mark|"
            r"unterminated.*quote|sql.*server|fatal.*error|"
            r"warning.*mysql",
            re.I
        )

        found_sqli = 0
        for url in lista:
            try:
                qs = url.split("?")
                if len(qs) < 2:
                    continue
                for param in qs[1].split("&"):
                    for payload in payloads:
                        test_url = url.replace(param, param + payload)
                        html = urlopen(
                            Request(test_url, headers=headers),
                            timeout=NET_TIMEOUT
                        ).read().decode("utf-8", errors="ignore")
                        if errors.search(html):
                            print(C.G + f"  [SQLi?] {test_url}" + C.RS)
                            found_sqli += 1
                            break
            except Exception:
                pass

        if not found_sqli:
            print(C.DM + "  No SQL error signatures detected." + C.RS)


# ══════════════════════════════════════════════════════════════════
# MODULE 3 — WP SCANNER
# ══════════════════════════════════════════════════════════════════

def wp_scanner():
    """
    WordPress & Joomla detection on a shared server.
    FIX [BUG-01]: urllib2 → urllib.request.
    FIX [BUG-04]: check_wordpress defined twice → single function above.
    """
    target = input(C.WH + "  Target IP: " + C.RS).strip()
    if not target:
        return
    print(C.GD + f"\n  Enumerating sites on {target}...\n" + C.RS)
    sites    = bing_all_grabber(target)
    wp       = check_wordpress(sites)
    joomla   = check_joomla(sites)

    print(C.G + f"\n  WordPress ({len(wp)}):" + C.RS)
    for s in wp:
        print(C.G + f"  {s}" + C.RS)

    print(C.G + f"\n  Joomla ({len(joomla)}):" + C.RS)
    for s in joomla:
        print(C.G + f"  {s}" + C.RS)


def wp_plugin_scanner():
    """
    Check if WordPress sites expose a given plugin path.
    FIX [BUG-01]: httplib → http.client.
    FIX [BUG-13]: except(),message → except Exception as e.
    FIX [BUG-15]: timeout added.
    """
    sites_file  = input(C.WH + "  Sites file path: " + C.RS).strip()
    plugin_file = input(C.WH + "  Plugins file path: " + C.RS).strip()

    if not os.path.isfile(sites_file) or not os.path.isfile(plugin_file):
        print(C.R + "\n  [!] File not found." + C.RS)
        return

    sites   = [s.strip() for s in open(sites_file).readlines() if s.strip()]
    plugins = [p.strip() for p in open(plugin_file).readlines() if p.strip()]
    NOT_FOUND = {404, 401, 400, 403, 406, 301}

    print(C.GD + f"\n  Scanning {len(sites)} site(s) × {len(plugins)} plugin(s)...\n" + C.RS)

    for site in sites:
        for plugin in plugins:
            try:
                conn = HTTPConnection(site, timeout=NET_TIMEOUT)
                conn.request("HEAD", f"/wp-content/plugins/{plugin}")
                status = conn.getresponse().status
                conn.close()
                if status not in NOT_FOUND:
                    print(C.G + f"  [+] {site} → {plugin} ({status})" + C.RS)
            except Exception:
                pass


def wp_vuln_check():
    """
    Check for common vulnerable WP plugin upload paths.
    FIX [BUG-05]: wpsycmium → wpsymposium.
    FIX [BUG-15]: timeout added.
    """
    target = input(C.WH + "  Target IP: " + C.RS).strip()
    if not target:
        return
    print(C.GD + f"\n  Enumerating on {target}...\n" + C.RS)
    sites = bing_all_grabber(target)
    wp    = check_wordpress(sites)

    vuln_checks = {
        "WPStore Remote Upload":   "wp-content/themes/WPStore/upload/index.php",
        "Sexy Contact Form":       "wp-content/plugins/sexy-contact-form/includes/fileupload/index.php",
        "Lazy SEO Plugin":         "wp-content/plugins/lazy-seo/lazyseo.php",
        "Easy Comment Uploads":    "wp-content/plugins/easy-comment-uploads/upload-form.php",
        # FIX [BUG-05]: wpsycmium.append() → wpsymposium.append()
        "WP Symposium Upload":     "wp-symposium/server/file_upload_form.php",
    }

    for check_name, path in vuln_checks.items():
        found = []
        for site in wp:
            try:
                if urlopen(site + path, timeout=NET_TIMEOUT).getcode() == 200:
                    found.append(site)
            except Exception:
                pass
        if found:
            print(C.G + f"\n  [+] {check_name} ({len(found)}):" + C.RS)
            for s in found:
                print(C.G + f"      {s}" + C.RS)

    print(C.DM + "\n  Scan complete." + C.RS)


# ══════════════════════════════════════════════════════════════════
# MENUS
# ══════════════════════════════════════════════════════════════════

def _prompt(label=""):
    return input(C.CY + f"\n  nulltrace{label}~# " + C.RS).strip()


def _header(title: str):
    print(C.DM + f"\n  ┌──────────────────────────────────────────┐")
    print(C.DM + f"  │{C.CY}  {title:<42}{C.DM}│")
    print(C.DM + f"  └──────────────────────────────────────────┘" + C.RS)


def info_menu():
    show_logo()
    _header("INFORMATION GATHERING")
    items = [
        ("1",  "Host to IP"),
        ("2",  "Port Scanner"),
        ("3",  "Server Banner Grab"),
        ("4",  "CMS Detection"),
        ("5",  "WordPress User Enum"),
        ("99", "Back"),
    ]
    for k, v in items:
        color = C.R if k == "99" else C.WH
        print(C.DM + "  │" + color + f"  [{k:2}] {v}" + C.RS)

    choice = _prompt("/info")
    clear()
    dispatch = {
        "1": host_to_ip,
        "2": port_scan_simple,
        "3": server_banner,
        "4": cms_detect,
        "5": wp_user_enum,
    }
    if choice in dispatch:
        dispatch[choice]()
    elif choice != "99":
        info_menu()
    input(C.DM + "\n  Press Enter to continue..." + C.RS)


def web_menu():
    show_logo()
    _header("WEB RECON")
    items = [
        ("1",  "WP & Joomla Scanner"),
        ("2",  "WP Plugin Scanner (file)"),
        ("3",  "WP Vulnerability Check"),
        ("4",  "Gravity Forms Finder"),
        ("99", "Back"),
    ]
    for k, v in items:
        color = C.R if k == "99" else C.WH
        print(C.DM + "  │" + color + f"  [{k:2}] {v}" + C.RS)

    choice = _prompt("/web")
    clear()
    if choice == "1":
        wp_scanner()
    elif choice == "2":
        wp_plugin_scanner()
    elif choice == "3":
        wp_vuln_check()
    elif choice == "4":
        gravity_finder()
    elif choice != "99":
        web_menu()
    input(C.DM + "\n  Press Enter to continue..." + C.RS)


def gravity_finder():
    """Find Gravity Forms installations."""
    ip = input(C.WH + "  Target IP: " + C.RS).strip()
    if not ip:
        return
    sites = bing_all_grabber(ip)
    found = []
    for site in sites:
        try:
            code = urlopen(
                site + "wp-content/plugins/gravityforms/gravityforms.php",
                timeout=NET_TIMEOUT
            ).getcode()
            if code == 403:
                found.append(site)
        except Exception:
            pass
    print(C.G + f"\n  [+] Found {len(found)} Gravity Forms installation(s):" + C.RS)
    for s in found:
        print(C.G + f"  {s}" + C.RS)


def server_recon_menu():
    """Server-wide recon using IP."""
    show_logo()
    _header("SERVER RECON")
    ip = input(C.WH + "  Target IP: " + C.RS).strip()
    if ip:
        clear()
        ServerRecon(ip).run()


# FIX [BUG-07]: menu() was defined twice — single clean version here
def main_menu():
    while True:
        show_logo()
        print(C.DM + "  ┌──────────────────────────────────────────┐")
        entries = [
            ("1",  "Information Gathering",   C.WH),
            ("2",  "Web Recon",               C.WH),
            ("3",  "Server Recon",            C.WH),
            ("99", "Exit",                    C.R),
        ]
        for k, label, color in entries:
            print(C.DM + "  │" + color + f"  [{k:2}] {label}" + C.RS)
        print(C.DM + "  └──────────────────────────────────────────┘" + C.RS)

        choice = _prompt()

        if choice == "1":
            info_menu()
        elif choice == "2":
            web_menu()
        elif choice == "3":
            server_recon_menu()
        elif choice == "99":
            print(C.G + "\n  [*] Exiting NullTrace. Stay ethical.\n" + C.RS)
            sys.exit(0)
        elif choice == "":
            continue
        else:
            print(C.R + "  [!] Invalid option." + C.RS)
            time.sleep(0.5)


# ══════════════════════════════════════════════════════════════════
# ENTRY POINT
# ══════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    if sys.version_info < (3, 8):
        print("[!] Python 3.8+ required.")
        sys.exit(1)
    try:
        main_menu()
    except KeyboardInterrupt:
        print(C.G + "\n\n  [*] Interrupted. Exiting NullTrace.\n" + C.RS)
        sys.exit(0)
