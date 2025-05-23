import logging
import time
from datetime import datetime
from tenacity import retry, stop_after_attempt, wait_fixed, retry_if_exception_type
from playwright.sync_api import Playwright, sync_playwright, TimeoutError as PlaywrightTimeoutError

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class MetarFormFiller:
    def __init__(self, page):
        self.page = page

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_fixed(3),
        retry=retry_if_exception_type(PlaywrightTimeoutError)
    )
    def select_station_and_observer(self):
        """Select station code and observer with retry logic"""
        logging.info("Selecting station and observer...")
        self.page.wait_for_load_state("networkidle")
        
        # Select station
        self.page.get_by_role("option", name="97260").click()
        self.page.get_by_label("Loading...", exact=True).click()
        
        # Select observer with timeout
        self.page.get_by_role("option", name="Zulkifli Ramadhan").click(timeout=10000)
        logging.info("Station and observer selected successfully")

    def select_date_and_time(self, day, hour, minute):
        """Select date and time in the form"""
        logging.info("Selecting date and time...")
        
        # Handle date selection
        self.page.locator("#datepicker__value_").click()
        current_day = datetime.now().day
        
        if int(day) == current_day:
            self.page.get_by_label(f"/{day}/2025 (Today)").click()
        else:
            self.page.get_by_label(f"5/{day}/").click()
        
        # Select time
        self.page.get_by_label("Jam").select_option(hour)
        self.page.get_by_label("Menit").select_option(minute)
        logging.info("Date and time selected successfully")

    def handle_wind(self, direction, speed, is_vrb=False, var_from=None, var_to=None):
        """Handle wind input including VRB and wind variation"""
        logging.info("Handling wind input...")
        
        # Input wind direction
        self.page.get_by_label("Arah Angin (derajat)").fill(direction)
        self.page.get_by_label("Arah Angin (derajat)").press("Tab")
        
        # Handle VRB if needed
        if is_vrb:
            self.page.get_by_label("VRB").press("Tab")
        
        # Input wind speed
        self.page.get_by_label("Kecepatan Angin (knot)").fill(speed)
        
        # Handle wind variation if present
        if var_from and var_to:
            self.page.locator("#winds-wd-dn").click()
            self.page.locator("#winds-wd-dn").fill(var_from)
            self.page.locator("#winds-wd-dn").press("Tab")
            self.page.locator("#winds-wd-dx").fill(var_to)
            self.page.locator("#winds-wd-dx").press("Tab")
        
        logging.info("Wind information entered successfully")

    def handle_visibility(self, visibility, is_cavok=False):
        """Handle visibility input including CAVOK"""
        logging.info("Handling visibility...")
        
        if is_cavok:
            self.page.get_by_label("Kecepatan Angin (knot)").press("Tab")
            self.page.get_by_label("Gust (Knot)").press("Tab")
            self.page.locator("#tooltips13").press("Tab")
            # Double space after this as mentioned in requirements
            self.page.keyboard.press("Space")
            self.page.keyboard.press("Space")
        else:
            self.page.get_by_role("spinbutton", name="Prevailling (m) Jarak pandang").fill(visibility)
            self.page.get_by_role("spinbutton", name="Prevailling (m) Jarak pandang").press("Tab")
        
        logging.info("Visibility entered successfully")

    def handle_weather_phenomena(self, phenomena):
        """Handle weather phenomena like TS, RA, TSRA"""
        logging.info("Handling weather phenomena...")
        
        if not phenomena:
            return
            
        self.page.locator(".col-sm-4 > .btn").first.click()
        
        if "TS" in phenomena:
            self.page.get_by_label("Weather", exact=True).get_by_text("TS Thunderstorm").click()
        
        if "RA" in phenomena:
            self.page.locator("label").filter(has_text="RA Rain").click()
            
        self.page.get_by_role("button", name="OK").click()
        logging.info("Weather phenomena entered successfully")

    def handle_clouds(self, clouds):
        """Handle cloud layers including CB and TCU"""
        logging.info("Handling cloud information...")
        
        for cloud in clouds:
            cloud_type = cloud.get('cloud_type')
            height = cloud.get('height')
            subtype = cloud.get('subtype')
            
            self.page.get_by_label("General").locator("#clouds-jumlah").select_option(cloud_type)
            self.page.get_by_label("General").locator("#cloud_height").fill(str(height))
            
            if subtype in ['CB', 'TCU']:
                self.page.get_by_label("General").locator("#select-type").select_option(subtype)
            
            # Add the cloud layer
            cloud_name = f"{cloud_type} ({self._get_okta_range(cloud_type)}) {subtype or '-'}"
            self.page.get_by_role("row", name=cloud_name).get_by_role("button").click()
        
        logging.info("Cloud information entered successfully")

    def handle_temperature_and_pressure(self, temperature, dew_point, pressure):
        """Handle temperature, dew point and pressure inputs"""
        logging.info("Handling temperature, dew point and pressure...")
        
        self.page.locator("#v-air-temp").fill(temperature)
        self.page.locator("#v-air-temp").press("Tab")
        self.page.locator("#v-dew-point").fill(dew_point)
        self.page.locator("#v-dew-point").press("Tab")
        self.page.get_by_label("TEKANAN UDARA (QNH)").fill(pressure)
        
        logging.info("Temperature, dew point and pressure entered successfully")

    def handle_trend_and_remarks(self, trend="NOSIG", remarks=None):
        """Handle trend and remarks section"""
        logging.info("Handling trend and remarks...")
        
        self.page.get_by_role("tab", name="Trend").click()
        self.page.get_by_label("Trend").locator("#input-type").select_option(trend)
        
        if remarks:
            self.page.get_by_placeholder("Remark").click()
            self.page.get_by_placeholder("Remark").fill(remarks)
        
        logging.info("Trend and remarks entered successfully")

    def submit_form(self, preview_only=True):
        """Submit the form with option for preview only"""
        logging.info("Submitting form...")
        
        self.page.get_by_role("button", name="Preview").click()
        
        if not preview_only:
            self.page.get_by_role("button", name="Submit").click()
        
        logging.info("Form submitted successfully")

    @staticmethod
    def _get_okta_range(cloud_type):
        """Get okta range for cloud type"""
        ranges = {
            "FEW": "1-2 oktas",
            "SCT": "3-4 oktas",
            "BKN": "5-7 oktas",
            "OVC": "8 oktas"
        }
        return ranges.get(cloud_type, "")

def run(playwright: Playwright) -> None:
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()
    
    try:
        # Navigate to the page
        page.goto("https://bmkgsatu.bmkg.go.id/meteorologi/metarspeci")
        
        # Create form filler instance
        form_filler = MetarFormFiller(page)
        
        # Example usage:
        form_filler.select_station_and_observer()
        form_filler.select_date_and_time("23", "00", "30")
        form_filler.handle_wind("150", "05", is_vrb=False)
        form_filler.handle_visibility("10000")
        form_filler.handle_weather_phenomena(["TS", "RA"])
        
        clouds = [
            {"cloud_type": "FEW", "height": "2000", "subtype": None},
            {"cloud_type": "SCT", "height": "1800", "subtype": "CB"}
        ]
        form_filler.handle_clouds(clouds)
        
        form_filler.handle_temperature_and_pressure("28", "25", "1008")
        form_filler.handle_trend_and_remarks(remarks="CB TO NW")
        form_filler.submit_form()
        
    finally:
        context.close()
        browser.close()

if __name__ == "__main__":
    with sync_playwright() as playwright:
        run(playwright) 