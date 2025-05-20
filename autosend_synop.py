import time
from datetime import datetime, timezone
from playwright.sync_api import Playwright, sync_playwright
import re

def wait_until_full_hour():
    """Menunggu sampai waktu penuh berikutnya (misalnya 18:00, 19:00, dst)."""
    current_time = datetime.now()
    if current_time.minute != 0:
        # Hitung selisih waktu untuk sampai ke jam penuh berikutnya
        seconds_until_next_hour = (60 - current_time.minute) * 60 - current_time.second
        print(f"Menunggu {seconds_until_next_hour} detik untuk jam penuh berikutnya.")
        time.sleep(seconds_until_next_hour)

def wait_for_element(page, selector, timeout=1000, retries=5):
    """Menunggu elemen hingga muncul dengan percobaan ulang maksimal 5 kali jika elemen tidak ditemukan."""
    attempt = 0
    while attempt < retries:
        try:
            page.wait_for_selector(selector, timeout=timeout, state="visible")
            print(f"Elemen '{selector}' ditemukan dan visible.")
            return True
        except Exception as e:
            attempt += 1
            print(f"Percobaan {attempt}/{retries}: Elemen '{selector}' tidak ditemukan atau tidak visible.")
            if attempt == retries:
                print(f"Error: Elemen '{selector}' tidak ditemukan setelah {retries} percobaan.")
                raise e  # Jika sudah mencapai retry limit, lemparkan exception
            time.sleep(1)  # Tunggu 1 detik sebelum percobaan ulang

def run(playwright: Playwright) -> None:
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()

    # Akses halaman sinoptik
    page.goto("https://bmkgsatu.bmkg.go.id/meteorologi/sinoptik")
    print("Halaman sinoptik BMKG telah dimuat.")

    while True:
        # Tunggu hingga jam penuh
        # Pilih stasiun
        page.locator("#select-station div").nth(1).click()
        page.get_by_role("option", name=re.compile(r"^Stasiun")).click()

        # pilih observer on duty
        page.locator("#select-observer div").nth(1).click()
        page.get_by_role("option", name="Zulkifli Ramadhan").click()

        # Tanggal Pengamatan
        today = datetime.now(timezone.utc)
        tgl_harini = f"/{today.month}/{today.year} (Today)"
        page.locator("#input-datepicker__value_").click()
        page.get_by_label(tgl_harini).click()

        wait_until_full_hour()

        # Mendapatkan jam saat ini (misalnya, 17 untuk jam 17:00)
        current_hour = datetime.now().hour
        print(f"Jam saat ini: {current_hour}:00")  # Menampilkan jam yang terpilih

        # Klik opsi jam yang sesuai
        page.locator("#input-jam div").nth(1).click()

        # Tunggu hingga elemen jam yang sesuai muncul dan pastikan elemen tersebut visible
        page.locator("#input-jam").get_by_role("textbox").fill(f"{current_hour}")

        # Klik opsi berdasarkan jam yang sesuai
        page.locator("#input-jam").get_by_role("textbox").press("Enter")

        # Tunggu dan klik tombol "View"
        page.get_by_role("button", name="View").click()

        # Tunggu dan klik tombol "Preview"
        page.get_by_role("button", name="Preview").click()
        time.sleep(2)
        # wait_for_element(page, 'button[name="OK"]')

        # Tunggu dan klik tombol "OK"
        page.get_by_role("button", name="OK").click()

        # Tunggu dan klik tombol "Send"
        page.get_by_role("button", name="Send").click()

        # Tunggu dan klik tombol "Send to INASwitching"
        page.get_by_role("button", name="Send to INASwitching").click()

        # Tunggu dan klik tombol "OK"
        page.get_by_role("button", name="OK").click()
        # time.sleep(50*60)
        time.sleep(20*60)
        page.reload()

        # Setelah tugas selesai, tunggu hingga jam penuh berikutnya
        print(f"Selesai pada jam {current_hour}:00. Menunggu hingga jam {current_hour + 1}:00.")
        wait_until_full_hour()

    context.close()
    browser.close()

with sync_playwright() as playwright:
    run(playwright)