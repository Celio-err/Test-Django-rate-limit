"""
Script pengujian rate-limiting / brute-force protection pada Django admin.
HANYA untuk digunakan pada website milik sendiri / yang sudah diberi izin resmi.

Cara pakai:
    python test_login_ratelimit.py

Script ini akan:
1. Ambil CSRF token dari halaman login
2. Coba login dengan password salah sebanyak N kali (default 10x)
3. Catat status code, response time, dan apakah muncul indikasi pemblokiran
   (misal status 403, pesan "too many attempts", atau HTTP 429)

Jumlah percobaan sengaja dibatasi kecil supaya:
- Tidak membebani server kantor
- Tidak memicu alert keamanan yang tidak perlu
- Cukup untuk membuktikan apakah proteksi rate-limit aktif atau tidak
"""

import requests
import time
import sys

# ==== KONFIGURASI - SESUAIKAN DENGAN SITUSMU ====
BASE_URL = "https://www.example.com"          # ganti dengan domain kantor
LOGIN_PATH = "https://www.example.com/login/"                 # ganti URL admin
USERNAME_TO_TEST = "admin"                   # username yang mau dites (pastikan bukan akun produksi aktif, idealnya buat dummy account)
NUM_ATTEMPTS = 50                            # jumlah percobaan, JANGAN terlalu besar
DELAY_BETWEEN_ATTEMPTS = 1                   # jeda detik antar percobaan, sopan ke server
# ==================================================

session = requests.Session()

def get_csrf_token():
    resp = session.get(BASE_URL + LOGIN_PATH)
    if resp.status_code != 200:
        print(f"[!] Gagal akses halaman login. Status: {resp.status_code}")
        sys.exit(1)
    token = session.cookies.get("csrftoken")
    if not token:
        print("[!] CSRF token tidak ditemukan. Cek apakah URL login benar.")
        sys.exit(1)
    return token

def try_login(username, password, csrf_token):
    payload = {
        "username": username,
        "password": password,
        "csrfmiddlewaretoken": csrf_token,
        "next": "/admin/",
    }
    headers = {"Referer": BASE_URL + LOGIN_PATH}
    start = time.time()
    resp = session.post(BASE_URL + LOGIN_PATH, data=payload, headers=headers, allow_redirects=False)
    elapsed = time.time() - start
    return resp, elapsed

def main():
    print(f"[*] Menguji rate-limit login di {BASE_URL + LOGIN_PATH}")
    print(f"[*] Username uji: {USERNAME_TO_TEST}, jumlah percobaan: {NUM_ATTEMPTS}\n")

    csrf_token = get_csrf_token()
    blocked_detected = False

    for i in range(1, NUM_ATTEMPTS + 1):
        fake_password = f"wrongpass{i}"
        resp, elapsed = try_login(USERNAME_TO_TEST, fake_password, csrf_token)

        status = resp.status_code
        body_snippet = resp.text[:200].replace("\n", " ")

        indikasi_blokir = (
            status in (403, 429)
            or "too many" in resp.text.lower()
            or "locked" in resp.text.lower()
            or "diblokir" in resp.text.lower()
        )

        print(f"[{i:02d}] status={status} waktu={elapsed:.2f}s "
              f"{'<-- TERINDIKASI DIBLOKIR' if indikasi_blokir else ''}")

        if indikasi_blokir and not blocked_detected:
            blocked_detected = True
            print(f"\n[+] Proteksi rate-limit terdeteksi aktif pada percobaan ke-{i}.")

        # refresh csrf token in case session changes
        csrf_token = session.cookies.get("csrftoken", csrf_token)

        time.sleep(DELAY_BETWEEN_ATTEMPTS)

    print("\n=== HASIL ===")
    if blocked_detected:
        print("✅ Proteksi brute-force TERDETEKSI. Bagus, sistem sudah membatasi percobaan login.")
    else:
        print("⚠️  Tidak ada indikasi pemblokiran setelah "
              f"{NUM_ATTEMPTS} percobaan. Pertimbangkan menambah proteksi "
              "seperti django-axes atau rate limiting di level web server (nginx).")

if __name__ == "__main__":
    main()
