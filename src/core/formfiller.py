"""
Form filler module for BMKG Auto Input.
"""
import asyncio
from playwright.async_api import TimeoutError
from ..utils import get_logger
import pandas as pd

logger = get_logger(__name__)

class FormFiller:
    def __init__(self, browser_manager):
        self.browser_manager = browser_manager
        self.page = browser_manager.page

    async def _fill_form_async(self, row_data, hour_selected):
        """
        Fill the form with data from a single row asynchronously.
        
        Args:
            row_data (pd.Series): Data from a single row of the Excel file
            hour_selected (int): Selected observation hour (0-23)
        """
        try:
            # Wait for the form to be ready
            await self.page.wait_for_selector('#form-sinoptik', timeout=10000)
            
            # Select the observation hour
            hour_selector = '#hour'
            await self.page.select_option(hour_selector, str(hour_selected))
            
            # Fill in the form fields based on the row data
            for column, value in row_data.items():
                if pd.isna(value):
                    continue
                    
                # Convert value to string
                value_str = str(value)
                
                # Map Excel columns to form field IDs
                field_mapping = {
                    'temp': '#temp',
                    'rh': '#rh',
                    'pressure': '#pressure',
                    'wind_speed': '#wind_speed',
                    'wind_direction': '#wind_direction',
                    'visibility': '#visibility',
                    'cloud_cover': '#cloud_cover',
                    'weather': '#weather',
                    'remarks': '#remarks'
                }
                
                # Get the field selector
                field_selector = field_mapping.get(column.lower())
                if not field_selector:
                    logger.warning(f"No mapping found for column: {column}")
                    continue
                
                try:
                    # Try to fill the field
                    await self.page.fill(field_selector, value_str)
                    logger.info(f"Filled field {field_selector} with value: {value_str}")
                except TimeoutError:
                    logger.warning(f"Could not find input field: {field_selector}")
                    continue
            
            # Submit the form
            submit_button = '#submit-button'
            await self.page.click(submit_button)
            logger.info("Form submitted")
            
        except Exception as e:
            logger.error(f"Error filling form: {e}")
            raise

    def fill_form(self, row_data, hour_selected):
        """
        Fill the form with data from a single row.
        
        Args:
            row_data (pd.Series): Data from a single row of the Excel file
            hour_selected (int): Selected observation hour (0-23)
        """
        try:
            # Get the current event loop or create a new one
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            
            # Run the async form filling
            loop.run_until_complete(self._fill_form_async(row_data, hour_selected))
            
        except Exception as e:
            logger.error(f"Error in fill_form: {e}")
            raise

    async def _wait_for_submission_async(self):
        """
        Wait for form submission to complete asynchronously.
        """
        try:
            # Wait for success message or redirect
            await self.page.wait_for_selector('.alert-success, .success-message', timeout=10000)
            logger.info("Form submission successful")
            
        except TimeoutError:
            # If no success message, check if we're still on the form page
            if await self.page.query_selector('#form-sinoptik'):
                raise TimeoutError("Form submission did not complete successfully")
            else:
                logger.info("Form submission completed (redirect detected)")
            
        except Exception as e:
            logger.error(f"Error waiting for submission: {e}")
            raise

    def wait_for_submission(self):
        """
        Wait for form submission to complete.
        """
        try:
            # Get the current event loop or create a new one
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            
            # Run the async wait
            loop.run_until_complete(self._wait_for_submission_async())
            
        except Exception as e:
            logger.error(f"Error in wait_for_submission: {e}")
            raise 