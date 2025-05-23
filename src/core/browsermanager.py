"""
Core functionality for BMKG Auto Input.
"""
import os
from tkinter import messagebox
from playwright.sync_api import sync_playwright
from .browserloader import BrowserLoader
from ..utils import get_logger

logger = get_logger('browser')

class BrowserManager:
    """Manages browser interactions for the application."""
    
    # URLs for different pages
    URLS = {
        'auto_input': "https://bmkgsatu.bmkg.go.id/meteorologi/sinoptik",
        'metar': "https://bmkgsatu.bmkg.go.id/meteorologi/metarspeci"
    }
    
    def __init__(self, user_data_dir):
        """Initialize the browser manager.
        
        Args:
            user_data_dir: Directory for browser user data
        """
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None
        self.user_data_dir = user_data_dir
        self.current_page = None

    def start_browser(self, page_type='auto_input'):
        """Start the browser and load the specified page.
        
        Args:
            page_type: Type of page to load ('auto_input' or 'metar')
        """
        try:
            self.playwright = sync_playwright().start()
            if not os.path.exists(self.user_data_dir):
                os.makedirs(self.user_data_dir)

            # Initialize Playwright
            loader = BrowserLoader(playwright=self.playwright, user_data_dir=self.user_data_dir, headless=False)
            self.page = loader.load_page(self.URLS[page_type])
            self.browser = loader.browser
            self.current_page = page_type
            
            # Set viewport to full screen
            self.page.set_viewport_size({"width": 1920, "height": 920})
            # Maximize the browser window
            self.page.evaluate("window.moveTo(0, 0)")
            self.page.evaluate("window.resizeTo(screen.width, screen.height)")
            
            logger.info(f"Browser started and {page_type} page loaded in full screen mode.")
        except Exception as e:
            logger.error(f"Failed to launch browser: {str(e)}")
            messagebox.showerror("Error", f"Failed to start browser: {e}")
            raise

    def navigate_to_page(self, page_type: str):
        """Navigate to a specific page type.
        
        Args:
            page_type: Type of page to navigate to ('auto_input' or 'metar')
        """
        if not self.page:
            self.start_browser(page_type)
            return
            
        try:
            if page_type != self.current_page:
                self.page.goto(self.URLS[page_type])
                self.current_page = page_type
                self.page.wait_for_load_state("networkidle")
                logger.info(f"Navigated to {page_type} page")
        except Exception as e:
            logger.error(f"Failed to navigate to {page_type} page: {str(e)}")
            raise

    def reload_page(self):
        """Reload the current page."""
        if self.page:
            try:
                self.page.reload()
                self.page.wait_for_load_state("networkidle")
                logger.info("Page reloaded successfully")
            except Exception as e:
                logger.error(f"Failed to reload page: {str(e)}")
                raise

    def stop_browser(self):
        """Stop the browser and clean up resources."""
        try:
            if self.browser:
                self.browser.close()
            if self.playwright:
                self.playwright.stop()
            self.browser = None
            self.page = None
            self.playwright = None
            self.current_page = None
            logger.info("Browser stopped successfully")
        except Exception as e:
            logger.error(f"Error stopping browser: {str(e)}")
            raise