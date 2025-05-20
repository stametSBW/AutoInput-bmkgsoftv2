import time
from datetime import datetime, timezone, timedelta
from playwright.sync_api import Playwright, sync_playwright
import re
from src.data.sandi import obs
from src.data import default_user_input
from src.utils import get_logger

logger = get_logger(__name__)

class AutoSender:
    def __init__(self, page=None, headless=False):
        self.headless = headless
        self.is_running = False
        self.page = page
        self.browser = None
        self.context = None
        self.last_run_hour = None
        self.user_input = default_user_input.copy()
        logger.info("AutoSender initialized")

    def get_next_full_hour(self):
        """Calculate the next full hour from current time."""
        now = datetime.now()
        next_hour = now.replace(minute=0, second=0, microsecond=0) + timedelta(hours=1)
        return next_hour

    def wait_until_next_hour(self):
        """Wait until the next full hour."""
        next_hour = self.get_next_full_hour()
        wait_seconds = (next_hour - datetime.now()).total_seconds()
        if wait_seconds > 0:
            logger.info(f"Waiting {wait_seconds:.0f} seconds until {next_hour.strftime('%H:%M')}")
            time.sleep(wait_seconds)

    def wait_for_element(self, selector, timeout=10000, retries=5):
        """Wait for element with improved retry mechanism."""
        attempt = 0
        while attempt < retries:
            try:
                self.page.wait_for_selector(selector, timeout=timeout, state="visible")
                logger.debug(f"Element '{selector}' found and visible")
                return True
            except Exception as e:
                attempt += 1
                logger.warning(f"Attempt {attempt}/{retries}: Element '{selector}' not found")
                if attempt == retries:
                    logger.error(f"Failed to find element '{selector}' after {retries} attempts")
                    raise e
                time.sleep(2)

    def fill_form(self, current_hour):
        """Fill the form with required data."""
        try:
            # Select station
            logger.debug("Selecting station...")
            self.page.locator("#select-station div").nth(1).click()
            self.page.get_by_role("option", name=re.compile(r"^Stasiun")).click()
            logger.debug("Station selected successfully")

            # Select observer
            logger.debug("Selecting observer...")
            obs_onduty_value = obs.get(self.user_input['obs_onduty'].lower(), "Zulkifli Ramadhan")
            self.page.locator("#select-observer div").nth(1).click()
            self.page.get_by_role("option", name=obs_onduty_value).click()
            logger.debug(f"Observer selected: {obs_onduty_value}")

            # Set date
            logger.debug("Setting observation date...")
            today = datetime.now(timezone.utc)
            tgl_harini = f"/{today.month}/{today.year} (Today)"
            self.page.locator("#input-datepicker__value_").click()
            self.page.get_by_label(tgl_harini).click()
            logger.debug(f"Date set: {tgl_harini}")

            # Set hour
            logger.debug(f"Setting observation hour: {current_hour}:00")
            self.page.locator("#input-jam div").nth(1).click()
            self.page.locator("#input-jam").get_by_role("textbox").fill(str(current_hour))
            self.page.locator("#input-jam").get_by_role("textbox").press("Enter")
            self.page.wait_for_load_state("networkidle")
            logger.debug("Hour set successfully")

            return True
        except Exception as e:
            logger.error(f"Error filling form: {str(e)}")
            return False

    def submit_form(self):
        """Submit the form and send data."""
        try:
            logger.info("Starting data submission process...")
            self.page.get_by_role("button", name="View").click()
            time.sleep(0.5)
            self.page.get_by_role("button", name="Preview").click()
            time.sleep(0.5)
            time.sleep(2)
            self.page.get_by_role("button", name="OK").click()
            time.sleep(0.5)
            self.page.get_by_role("button", name="Send").click()
            time.sleep(0.5)
            self.page.get_by_role("button", name="Send to INASwitching").click()
            time.sleep(0.5)
            self.page.get_by_role("button", name="OK").click()
            logger.info("Data sent successfully!")
            return True
        except Exception as e:
            logger.error(f"Error submitting form: {str(e)}")
            return False

    def handle_page_error(self):
        """Handle page errors and attempt recovery."""
        try:
            logger.debug("Attempting to reload page...")
            self.page.reload()
            self.page.wait_for_load_state("networkidle")
            return True
        except Exception as e:
            logger.error(f"Error reloading page: {str(e)}")
            try:
                logger.debug("Attempting to access page again...")
                self.page.goto("https://bmkgsatu.bmkg.go.id/meteorologi/sinoptik")
                self.page.wait_for_load_state("networkidle")
                return True
            except Exception as goto_error:
                logger.error(f"Error accessing page: {str(goto_error)}")
                return False

    def start(self):
        """Start the auto-send process."""
        if not self.page:
            logger.error("No browser page provided")
            raise ValueError("No browser page provided. Please open the browser first.")
            
        self.is_running = True
        logger.info("Auto-send process started")
        
        try:
            while self.is_running:
                try:
                    # Wait until next full hour first
                    self.wait_until_next_hour()
                    
                    if not self.is_running:
                        break

                    # Get the current hour AFTER waiting for the next full hour
                    current_time = datetime.now()
                    current_hour = current_time.hour
                    
                    logger.info(f"Starting data submission for hour {current_hour}:00")
                    
                    # Fill and submit form
                    if self.fill_form(current_hour) and self.submit_form():
                        self.last_run_hour = current_hour
                        logger.info(f"Completed at {current_hour}:00. Waiting for next hour.")
                        
                        # Wait 2 minutes before reloading
                        logger.debug("Waiting 2 minutes before reload...")
                        time.sleep(2 * 60)
                        
                        # Always reload the page after 2 minutes
                        logger.debug("Reloading page...")
                        try:
                            self.page.reload()
                            self.page.wait_for_load_state("networkidle")
                            logger.debug("Page reloaded successfully")
                        except Exception as e:
                            logger.error(f"Error reloading page: {str(e)}")
                            # If reload fails, try to access the page again
                            try:
                                logger.debug("Attempting to access page again...")
                                self.page.goto("https://bmkgsatu.bmkg.go.id/meteorologi/sinoptik")
                                self.page.wait_for_load_state("networkidle")
                                logger.debug("Page accessed successfully")
                            except Exception as goto_error:
                                logger.error(f"Error accessing page: {str(goto_error)}")
                                time.sleep(300)  # Wait 5 minutes if both reload and access fail
                    else:
                        logger.error("Form submission failed")
                        time.sleep(60)

                except Exception as e:
                    logger.error(f"Error in auto-send iteration: {str(e)}")
                    if self.is_running:
                        logger.warning("Retrying in 1 minute...")
                        time.sleep(60)
                        try:
                            self.page.reload()
                            self.page.wait_for_load_state("networkidle")
                        except Exception as reload_error:
                            logger.error(f"Error reloading page: {str(reload_error)}")
                            time.sleep(300)

        except Exception as e:
            logger.error(f"Fatal error in auto-send process: {str(e)}")
        finally:
            self.stop()

    def stop(self):
        """Stop the auto-send process."""
        self.is_running = False
        self.last_run_hour = None
        logger.info("Auto-send process stopped")
        self.page = None
