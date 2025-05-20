import os
import logging
from playwright.sync_api import sync_playwright
from browserloader import BrowserLoader
from tkinter import messagebox

class BrowserManager:
    def __init__(self, user_data_dir):
        self.playwright = None
        self.browser = None
        self.page = None
        self.user_data_dir = user_data_dir

    def start_browser(self):
        """
        Mulai browser menggunakan Playwright dan muat halaman BMKGSatu.
        """
        try:
            self.playwright = sync_playwright().start()
            if not os.path.exists(self.user_data_dir):
                os.makedirs(self.user_data_dir)

            # Inisialisasi Playwright
            loader = BrowserLoader(playwright=self.playwright, user_data_dir=self.user_data_dir, headless=False)
            self.page = loader.load_page("https://bmkgsatu.bmkg.go.id/meteorologi/sinoptik")
            self.browser = loader.browser
            logging.info("Browser started and page loaded.")
        except Exception as e:
            logging.error(f"Failed to start browser: {e}")
            messagebox.showerror("Error", f"Terdapat Error saat membuka browser: {e}")

    def close_browser(self):
        """
        Close the browser cleanly.
        """
        if self.browser:
            self.browser.close()
            logging.info("Browser closed.")

        if self.playwright:
            # This ensures the entire Playwright instance is stopped, closing the actual browser
            self.playwright.stop()
            logging.info("Playwright stopped and browser fully closed.")

    def reload_browser(self):
        """
        Reload the browser page.
        """
        if self.page:
            # Reload the page using the reload() method of the Page object
            self.page.reload()
            self.page.wait_for_load_state("networkidle")  # Optionally wait for the page to fully reload
            logging.info("Page reloaded.")