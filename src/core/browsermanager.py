"""
Core functionality for BMKG Auto Input.
"""
import os
from tkinter import messagebox
from playwright.sync_api import sync_playwright
from .browserloader import BrowserLoader
from ..utils import get_logger

logger = get_logger(__name__)

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
            logger.info("Browser started and page loaded.")
        except Exception as e:
            logger.error(f"Failed to start browser: {e}")
            messagebox.showerror("Error", f"Failed to start browser: {e}")

    def navigate_to_form(self):
        """
        Navigate to the form page and wait for it to load.
        """
        try:
            if not self.page:
                raise RuntimeError("Browser not initialized")
            
            # Navigate to the form page
            self.page.goto("https://bmkgsatu.bmkg.go.id/meteorologi/sinoptik")
            self.page.wait_for_load_state("networkidle")
            logger.info("Navigated to form page successfully")
        except Exception as e:
            logger.error(f"Failed to navigate to form: {e}")
            raise

    def close_browser(self):
        """
        Close the browser cleanly.
        """
        try:
            if self.browser:
                self.browser.close()
                logger.info("Browser closed.")
            
            if self.playwright:
                self.playwright.stop()
                logger.info("Playwright stopped and browser fully closed.")
        except Exception as e:
            logger.error(f"Error closing browser: {e}")

    def reload_browser(self):
        """
        Reload the browser page with proper error handling and state management.
        """
        try:
            if not self.page:
                logger.warning("Browser not initialized, attempting to restart...")
                self.start_browser()
                return

            # Check if page is still valid
            try:
                self.page.url
            except Exception:
                logger.warning("Page is no longer valid, attempting to navigate to form...")
                self.navigate_to_form()
                return

            # Attempt to reload the page
            try:
                self.page.reload()
                self.page.wait_for_load_state("networkidle")
                logger.info("Page reloaded successfully")
            except Exception as reload_error:
                logger.error(f"Failed to reload page: {reload_error}")
                # If reload fails, try to navigate to the form again
                logger.info("Attempting to navigate to form instead...")
                self.navigate_to_form()

        except Exception as e:
            logger.error(f"Critical error during reload: {e}")
            # If all else fails, try to restart the browser
            try:
                self.close_browser()
                self.start_browser()
            except Exception as restart_error:
                logger.error(f"Failed to restart browser: {restart_error}")
                raise RuntimeError("Failed to recover browser state")

    def stop_browser(self):
        """
        Stop the browser and cleanup resources.
        """
        try:
            if self.browser:
                self.browser.close()
                logger.info("Browser stopped.")
            
            if self.playwright:
                self.playwright.stop()
                logger.info("Playwright stopped.")
        except Exception as e:
            logger.error(f"Error stopping browser: {e}")