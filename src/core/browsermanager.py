"""
Core functionality for BMKG Auto Input.
"""
import os
from tkinter import messagebox
from playwright.sync_api import sync_playwright
from .browserloader import BrowserLoader
from ..utils import get_logger

logger = get_logger('browser')  # Use the browser-specific logger

class BrowserManager:
    def __init__(self, user_data_dir):
        self.playwright = None
        self.browser = None
        self.context = None
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
            
            # Set viewport to full screen
            self.page.set_viewport_size({"width": 1920, "height": 1020})
            # Maximize the browser window
            self.page.evaluate("window.moveTo(0, 0)")
            self.page.evaluate("window.resizeTo(screen.width, screen.height)")
            
            logger.info("Browser started and page loaded in full screen mode.")
        except Exception as e:
            logger.error(f"Failed to launch browser: {str(e)}")
            messagebox.showerror("Error", f"Failed to start browser: {e}")
            raise

    def navigate_to_form(self):
        """
        Navigate to the form page and wait for it to load.
        """
        try:
            logger.info("Navigating to BMKG form...")
            self.page.goto("https://bmkgsatu.bmkg.go.id/meteorologi/sinoptik")
            self.page.wait_for_load_state("networkidle")
            logger.info("Successfully navigated to BMKG form")
        except Exception as e:
            logger.error(f"Failed to navigate to form: {str(e)}")
            raise

    def close_browser(self):
        """
        Close the browser cleanly.
        """
        try:
            if self.browser:
                logger.info("Closing browser...")
                self.browser.close()
                self.browser = None
                self.context = None
                self.page = None
                logger.info("Browser closed successfully")
        except Exception as e:
            logger.error(f"Error closing browser: {str(e)}")
            raise

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
                self.browser = None
                logger.info("Browser stopped.")
            
            if self.playwright:
                self.playwright.stop()
                self.playwright = None
                logger.info("Playwright stopped.")
                
            # Clear all references
            self.context = None
            self.page = None
        except Exception as e:
            logger.error(f"Error stopping browser: {e}")
            raise