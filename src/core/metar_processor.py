"""
METAR processing functionality for BMKG Auto Input.
"""
import logging
from datetime import datetime
from tenacity import retry, stop_after_attempt, wait_fixed, retry_if_exception_type
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

logger = logging.getLogger(__name__)

class MetarProcessor:
    """Handles METAR code processing and form filling."""
    
    def __init__(self, page):
        """Initialize the METAR processor.
        
        Args:
            page: Playwright page object
        """
        self.page = page
        
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_fixed(3),
        retry=retry_if_exception_type(PlaywrightTimeoutError)
    )
    def select_station_and_observer(self):
        """Select the station code and observer."""
        logger.info("Filling station code...")
        self.page.wait_for_load_state("networkidle")
        self.page.locator("#vs2__combobox").scroll_into_view_if_needed()
        self.page.locator("#vs2__combobox").get_by_label("Loading...").click()
        self.page.get_by_role("option", name="97260").click()
        logger.info("Station code selected.")

        logger.info("Selecting observer...")
        self.page.wait_for_load_state("networkidle")
        self.page.get_by_label("Loading...", exact=True).click()
        self.page.get_by_role("option", name="Zulkifli Ramadhan").click(timeout=10000)
        logger.info("Observer selected.")

    def get_custom_date_selector(self, input_day: str) -> str:
        """Get the appropriate date selector string.
        
        Args:
            input_day: Day of the month as string
            
        Returns:
            str: Formatted date selector string
        """
        current_month = datetime.now().month
        current_year = datetime.now().year
        current_day = datetime.now().day

        if not input_day.isdigit() or not (1 <= int(input_day) <= 31):
            raise ValueError("Invalid day. Please enter a number between 1 and 31.")
            
        input_day = int(input_day)
        if input_day == current_day:
            return f"/{input_day}/{current_year} (Today)"
        else:
            return f"{current_month}/{input_day}/{current_year}"

    def handle_cloud_selection(self, cloud_type: str, cloud_subtype: str, cloud_height=None):
        """Handle cloud type and subtype selection.
        
        Args:
            cloud_type: Type of cloud (FEW, SCT, BKN, OVC)
            cloud_subtype: Subtype of cloud
            cloud_height: Height of cloud base
        """
        cloud_oktas_mapping = {
            "FEW": "1-2 oktas",
            "SCT": "3-4 oktas",
            "BKN": "5-7 oktas",
            "OVC": "8 oktas"
        }

        okta_value = cloud_oktas_mapping.get(cloud_type)
        if not okta_value:
            logger.error("Invalid cloud type provided.")
            return
            
        if not cloud_subtype:
            cloud_subtype = "-"

        try:
            self.page.get_by_label("General").locator("#clouds-jumlah").select_option(cloud_type)
            self.page.get_by_label("General").locator("#cloud_height").click()
            self.page.get_by_label("General").locator("#cloud_height").fill(str(cloud_height))

            cloud_name = f"{cloud_type} ({okta_value}) {cloud_subtype}"
            self.page.get_by_role("row", name=cloud_name).get_by_role("button").click()
            logger.info(f"Cloud selection successful: {cloud_name}")

        except Exception as e:
            logger.error(f"Error during cloud selection: {e}")
            raise

    def fill_form(self, metar_data: dict):
        """Fill the METAR form with provided data.
        
        Args:
            metar_data: Dictionary containing METAR data
        """
        try:
            # Select station and observer
            self.select_station_and_observer()

            # Set date
            logger.info("Selecting date...")
            custom_date_selector = self.get_custom_date_selector(metar_data['day'])
            self.page.locator("#datepicker__value_").click()
            self.page.get_by_label(custom_date_selector).click()
            logger.info("Date selected.")

            # Set time
            logger.info("Filling METAR time...")
            self.page.get_by_label("Jam").select_option(metar_data['hour'])
            self.page.get_by_label("Menit").select_option(metar_data['minute'])
            logger.info("Time selected.")
            self.page.wait_for_load_state("networkidle")
            self.page.wait_for_timeout(2000)

            # Set wind
            logger.info("Filling wind direction and speed...")
            self.page.get_by_label("Arah Angin (derajat)").click()
            self.page.get_by_label("Arah Angin (derajat)").fill(metar_data['wind_direction'])
            self.page.get_by_label("Kecepatan Angin (knot)").click()
            self.page.get_by_label("Kecepatan Angin (knot)").fill(metar_data['wind_speed'])
            logger.info("Wind direction and speed filled.")

            # Set visibility
            logger.info("Filling visibility...")
            self.page.get_by_role("spinbutton", name="Prevailling (m) Jarak pandang").click()
            self.page.get_by_role("spinbutton", name="Prevailling (m) Jarak pandang").fill(metar_data['visibility'])
            logger.info("Visibility filled.")

            # Set clouds
            logger.info("Selecting cloud type and subtype...")
            if metar_data.get('clouds'):
                for cloud in metar_data['clouds']:
                    self.handle_cloud_selection(
                        cloud['cloud_type'],
                        cloud['cloud_subtype'],
                        cloud['cloud_height']
                    )
            logger.info("Cloud selection completed.")

            # Set temperature and dew point
            logger.info("Filling temperature and dew point...")
            self.page.locator("#v-air-temp").fill(metar_data['temperature'])
            self.page.locator("#v-dew-point").fill(metar_data['dew_point'])
            logger.info("Temperature and dew point filled.")

            # Set pressure
            logger.info("Filling air pressure...")
            self.page.get_by_label("TEKANAN UDARA (QNH)").fill(metar_data['pressure'])
            logger.info("Air pressure filled.")

            # Set trend
            logger.info("Selecting trend NOSIG...")
            self.page.get_by_role("tab", name="Trend").click()
            self.page.get_by_label("Trend").locator("#input-type").select_option(metar_data['trend'])
            logger.info("Trend NOSIG selected.")

            # Preview
            logger.info("Clicking preview button...")
            self.page.get_by_role("button", name="Preview").click()
            logger.info("Form preview completed.")

            # Submit
            logger.info("Clicking submit button...")
            self.page.get_by_role("button", name="Submit").click()
            logger.info("Form submitted successfully.")

        except Exception as e:
            logger.error(f"Error filling form: {e}")
            raise 