import logging
import re
from datetime import datetime, timezone


class AutoInput:
    def __init__(self, page, user_input, obs, ww, w1w2, awan_lapisan, arah_angin, ci, cm, ch):
        """
        Inisialisasi objek AutoInput.

        Args:
            page: Objek halaman Playwright yang sedang aktif.
            user_input: Dictionary berisi input data dari pengguna.
            obs, ww, w1w2, awan_lapisan, arah_angin, ci, cm, ch: Mapping untuk pengisian data cuaca.
        """
        self.page = page
        self.user_input = user_input
        self.obs = obs
        self.ww = ww
        self.w1w2 = w1w2
        self.awan_lapisan = awan_lapisan
        self.arah_angin = arah_angin
        self.ci = ci
        self.cm = cm
        self.ch = ch

    # Do the task
    def fill_form(self):
        """Mengisi seluruh form berdasarkan input pengguna."""
        try:
            logging.info("Memulai Proses Input Data")
            self.select_station_and_observer()
            self.select_date_and_time()
            self.fill_parameters_based_on_time()
            self.fill_wind_visibility_data()
            self.fill_weather_conditions()
            self.fill_pressure_and_temperature()
            self.fill_cloud_cover()
            self.fill_cl_dominant()
            self.fill_cm_mid_level_cloud()
            self.fill_ch_high_level_cloud()
            self.fill_land_condition()
            self.click_preview_button()

            logging.info("Proses Input Selesai")
        except Exception as e:
            logging.error(f"Error filling form: {e}")

    # Helper Method
    def press_enter(self, locator):
        """Helper method to press 'Enter' after filling a field."""
        try:
            field = self.page.locator(locator).get_by_role("textbox")
            field.press("Enter")
        except Exception as e:
            logging.error(f"Error pressing 'Enter' for locator: {locator}: {e}")
            raise

    def click_and_fill(self, locator, value):
        """Helper to click and fill a locator field."""
        try:
            field = self.page.locator(locator)
            field.click()
            field.fill(value)
        except Exception as e:
            logging.error(f"Error in filling {locator} with {value}: {e}")
            raise

    def select_dropdown_option(self, locator, value):
        """Helper to select an option from a dropdown."""
        try:
            self.page.locator(locator).click()
            self.page.get_by_role("option", name=value).click()
        except Exception as e:
            logging.error(f"Error selecting dropdown option {value} for {locator}: {e}")
            raise

    def click_and_fill_by_label(self, label_text, value):
        """Clicks a label and fills the corresponding input."""
        try:
            field = self.page.get_by_label(label_text)
            field.click()
            field.fill(value)
        except Exception as e:
            logging.error(f"Error filling field with label {label_text}: {e}")
            raise

    def select_dropdown_option_by_name(self, locator, option_name):
        """Helper method to select a dropdown option by its name."""
        try:
            self.page.locator(locator).click()
            self.page.get_by_role("option", name=option_name).click()
        except Exception as e:
            logging.error(f"Error selecting dropdown option by name {option_name} for locator {locator}: {e}")
            raise

    # Parameters to fill
    def select_station_and_observer(self):
        """Select station and observer based on user input."""
        logging.info("Selecting station and observer")
        try:
            # Select station
            self.page.locator("#select-station div").nth(1).click()
            self.page.get_by_role("option", name=re.compile(r"^Stasiun")).click()

            self.page.wait_for_load_state("networkidle")

            # Select observer on duty
            obs_onduty_value = self.obs.get(self.user_input['obs_onduty'].lower(), "Zulkifli Ramadhan")
            self.page.locator("#select-observer div").nth(1).click()
            self.page.get_by_role("option", name=obs_onduty_value).click()

        except Exception as e:
            logging.error(f"Error selecting station or observer: {e}")
            raise

    def select_date_and_time(self):
        """Select the date and fill the observation time."""
        logging.info("Selecting date and filling observation time")
        try:
            # Select the date (Today)
            today = datetime.now(timezone.utc)
            tgl_harini = f"/{today.month}/{today.year} (Today)"
            self.page.locator("#input-datepicker__value_").click()
            self.page.get_by_label(tgl_harini).click()

            # This is the correct way to handle the #input-jam field
            self.page.locator("#input-jam div").nth(1).click()  # Click on the dropdown or div element
            self.page.locator("#input-jam").get_by_role("textbox").fill(self.user_input.get('jam_pengamatan', ''))
            self.page.locator("#input-jam").get_by_role("textbox").press("Enter")

            # Ensure the page is fully loaded before proceeding
            self.page.wait_for_load_state("networkidle")

        except Exception as e:
            logging.error(f"Error selecting date or time: {e}")
            raise

    def fill_parameters_based_on_time(self):
        """Fill specific parameters based on the observation time (jam_pengamatan)."""
        try:
            jam_penting = int(self.user_input.get('jam_pengamatan', 0))
            logging.info(f"Filling parameters for jam_pengamatan: {jam_penting}")

            if jam_penting == 0:
                self._fill_parameters_for_time_0()
            elif jam_penting == 12:
                self._fill_parameters_for_time_12()
            elif jam_penting in [3, 6, 9, 15, 18, 21]:
                self._fill_parameters_for_other_times()
            else:
                logging.info("Jam Pengamatan Tidak Termasuk Jam Pengiriman Utama.")

        except Exception as e:
            logging.error(f"Error in filling parameters based on time: {e}")
            raise

    def _fill_parameters_for_time_0(self):
        """Fill parameters specific to 00:00 observation time."""
        logging.info("Filling parameters for 00:00 observation time")
        try:
            self.click_and_fill_by_label("Suhu Minimum (℃)", self.user_input.get('suhu_minimum', ''))
            self.click_and_fill_by_label("Hujan ditakar (mm)", self.user_input.get('hujan_ditakar', ''))
            self.click_and_fill_by_label("Penguapan (mm)", self.user_input.get('penguapan', ''))
            self.click_and_fill("#evaporation_eq_indicator_ie", self.user_input.get('pengenal_penguapan', ''))
            self.click_and_fill_by_label("Lama Penyinaran Matahari (jam)", self.user_input.get('lama_penyinaran', ''))

        except Exception as e:
            logging.error(f"Error filling parameters for 00:00: {e}")
            raise

    def _fill_parameters_for_time_12(self):
        """Fill parameters specific to 12:00 observation time."""
        logging.info("Filling parameters for 12:00 observation time")
        try:
            self.click_and_fill_by_label("Suhu Maksimum (℃)", self.user_input.get('suhu_maksimum', ''))
            self.click_and_fill_by_label("Hujan ditakar (mm)", self.user_input.get('hujan_ditakar', ''))

        except Exception as e:
            logging.error(f"Error filling parameters for 12:00: {e}")
            raise

    def _fill_parameters_for_other_times(self):
        """Fill parameters for other observation times: 03:00, 06:00, 09:00, 15:00, 18:00, 21:00."""
        logging.info(f"Filling parameters for other observation times")
        try:
            self.click_and_fill_by_label("Hujan ditakar (mm)", self.user_input.get('hujan_ditakar', ''))

        except Exception as e:
            logging.error(f"Error filling parameters for other times: {e}")
            raise

    def fill_wind_visibility_data(self):
        """Fills wind data including wind indicator, direction, and speed."""
        logging.info("Filling wind data")
        try:
            # Fill wind indicator (iw)
            # self.page.locator("#wind_indicator_iw div").nth(1).click()  # Open the dropdown or activate the field
            # self.page.locator("#wind_indicator_iw").get_by_role("textbox").fill(
            #     self.user_input.get('pengenal_angin', ''))
            self.get_by_role("option", name="4 - wind speed from").click()
            self.locator("#wind_indicator_iw").get_by_role("combobox").click()
            self.page.locator("#wind_indicator_iw").get_by_role("textbox").press("Enter")  # Press Enter to submit

            # Fill wind direction (Arah Angin)
            self.click_and_fill_by_label("Arah Angin (derajat)", self.user_input.get('arah_angin', ''))

            # Fill wind speed (Kecepatan Angin)
            self.click_and_fill_by_label("Kecepatan Angin (knot)", self.user_input.get('kecepatan_angin', ''))

            # Fill visibility (Jarak Penglihatan)
            self.click_and_fill_by_label("Jarak penglihatan mendatar (", self.user_input.get('jarak_penglihatan', ''))

        except Exception as e:
            logging.error(f"Error filling wind data: {e}")
            raise

    def fill_weather_conditions(self):
        """Fills the present and past weather conditions based on user input."""
        logging.info("Filling weather conditions (Present Weather, Past Weather W1, W2)")
        try:
            # 6 Cuaca Saat Pengamatan (ww)
            ww_value = self.ww.get(self.user_input.get('cuaca_pengamatan', ''), "00")
            self.page.locator("#present_weather_ww div").nth(1).click()  # Click on the dropdown or div element
            self.page.locator("#present_weather_ww").get_by_role("textbox").fill(ww_value)
            self.page.locator("#present_weather_ww").get_by_role("textbox").press("Enter")

            # 7 Cuaca yang lalu (W1)
            w1_value = self.w1w2.get(self.user_input.get('cuaca_w1', ''), "0")
            self.page.locator("#past_weather_w1 div").nth(1).click()
            self.page.locator("#past_weather_w1").get_by_role("textbox").fill(w1_value)
            self.page.locator("#past_weather_w1").get_by_role("textbox").press("Enter")

            # 8 Cuaca yang lalu (W2)
            w2_value = self.w1w2.get(self.user_input.get('cuaca_w2', ''), "0")
            self.page.locator("#past_weather_w2 div").nth(1).click()
            self.page.locator("#past_weather_w2").get_by_role("textbox").fill(w2_value)
            self.page.locator("#past_weather_w2").get_by_role("textbox").press("Enter")

        except Exception as e:
            logging.error(f"Error filling weather conditions: {e}")
            raise

    def fill_pressure_and_temperature(self):
        """Fills the pressure and temperature fields based on user input."""
        logging.info("Filling pressure (QFF, QFE) and temperature (Dry Bulb, Wet Bulb) fields")
        try:
            # 9 Tekanan QFF
            self.click_and_fill_by_label("Tekanan QFF", self.user_input.get('tekanan_qff', ''))

            # 10 Tekanan QFE
            self.click_and_fill_by_label("Tekanan QFE", self.user_input.get('tekanan_qfe', ''))

            # 11 Suhu Bola Kering (Dry Bulb Temperature)
            self.click_and_fill_by_label("Suhu Bola Kering (℃)", self.user_input.get('suhu_bola_kering', ''))

            # 12 Suhu Bola Basah (Wet Bulb Temperature)
            self.click_and_fill_by_label("Suhu Bola Basah (℃)", self.user_input.get('suhu_bola_basah', ''))

        except Exception as e:
            logging.error(f"Error filling pressure and temperature fields: {e}")
            raise

    def fill_cloud_cover(self):
        """Fills the cloud cover (oktas) based on user input."""
        logging.info("Filling cloud cover (oktas)")
        try:
            # 15 Bagian Langit Tertutup Awan (oktas)
            self.page.locator("#cloud_cover_oktas_m div").nth(1).click()  # Click the dropdown
            self.page.locator("#cloud_cover_oktas_m").get_by_role("textbox").fill(self.user_input.get('oktas', ''))
            self.page.locator("#cloud_cover_oktas_m").get_by_role("textbox").press("Enter")  # Press Enter to confirm

        except Exception as e:
            logging.error(f"Error filling cloud cover: {e}")
            raise

    def fill_cl_dominant(self):
        """Fills dominant low cloud (CL) data."""
        logging.info("Filling dominant low cloud (CL)")
        try:
            # 17 CL Dominan
            cl_value = self.ci.get(self.user_input.get('cl_dominan', ''), "0")
            self.page.locator("#cloud_low_type_cl div").nth(1).click()  # Open the dropdown
            if cl_value == "1":
                self.page.get_by_role("option", name="1 - cumulus humilis atau").click()
            else:
                # Ensure filling in the correct field with better specificity
                self.page.locator("#cloud_low_type_cl").get_by_role("textbox").fill(cl_value)
                self.page.locator("#cloud_low_type_cl").get_by_role("textbox").press("Enter")

            if cl_value != "0":
                # 18 NCL Total (Jumlah Awan Rendah)
                self.page.locator("#cloud_low_cover_oktas div").nth(1).click()  # Open the dropdown
                self.page.locator("#cloud_low_cover_oktas").get_by_role("textbox").fill(
                    self.user_input.get('ncl_total', ''))
                self.page.locator("#cloud_low_cover_oktas").get_by_role("textbox").press("Enter")

                # 19 Jenis CL Lapisan 1
                jenis_cl_lap1_value = self.awan_lapisan.get(self.user_input.get('jenis_cl_lapisan1', ''), "0")
                self.page.locator("div:nth-child(3) > .ant-select > .ant-select-selection").first.click()
                self.page.get_by_role("option", name=jenis_cl_lap1_value).click()

                # 20 Jumlah CL Lapisan 1
                self.page.locator("div:nth-child(4) > .ant-select > .ant-select-selection").first.click()
                self.page.locator("div:nth-child(4) > .ant-select > .ant-select-selection > .ant-select-selection__rendered > .ant-select-search > .ant-select-search__field__wrap > .ant-select-search__field").first.fill(self.user_input['jumlah_cl_lapisan1'])
                self.page.locator("div:nth-child(4) > .ant-select > .ant-select-selection").first.press("Enter")

                # 21 Tinggi Dasar Awan Lapisan 1
                self.page.locator("#cloud_low_base_1").click()
                self.page.locator("#cloud_low_base_1").fill(self.user_input.get('tinggi_dasar_aw_lapisan1', ''))

        except Exception as e:
            logging.error(f"Error filling CL Dominant: {e}")
            raise

    def select_cl_type(self, cl_value):
        """Selects the type of CL (low cloud) based on the cl_value."""
        logging.info(f"Selecting CL type: {cl_value}")
        try:
            self.page.locator("#cloud_low_type_cl div").nth(1).click()
            if cl_value == "1":
                self.page.get_by_role("option", name="1 - cumulus humilis atau").click()
            else:
                self.click_and_fill("#cloud_low_type_cl", cl_value)
                self.press_enter("#cloud_low_type_cl")
        except Exception as e:
            logging.error(f"Error selecting CL type: {e}")
            raise

    def fill_cl_additional_fields(self):
        """Fills additional fields related to CL Dominant (low cloud)."""
        logging.info("Filling additional CL fields")
        try:
            # 18 NCL Total (Jumlah Awan Rendah)
            self.page.locator("#cloud_low_cover_oktas div").nth(1).click()  # Open the dropdown
            self.page.locator("#cloud_low_cover_oktas").get_by_role("textbox").fill(
                self.user_input.get('ncl_total', ''))
            self.page.locator("#cloud_low_cover_oktas").get_by_role("textbox").press("Enter")

            # 19 Jenis CL Lapisan 1
            jenis_cl_lap1_value = self.awan_lapisan.get(self.user_input.get('jenis_cl_lapisan1', ''), "0")
            self.page.locator("div:nth-child(3) > .ant-select > .ant-select-selection").first.click()
            self.page.get_by_role("option", name=jenis_cl_lap1_value).click()

            # 20 Jumlah CL Lapisan 1
            self.page.locator("div:nth-child(4) > .ant-select > .ant-select-selection").first.click()
            self.page.locator(
                "div:nth-child(4) > .ant-select > .ant-select-selection__rendered > .ant-select-search__field__wrap > .ant-select-search__field").first.fill(
                self.user_input.get('jumlah_cl_lapisan1', ''))
            self.page.locator("div:nth-child(4) > .ant-select > .ant-select-selection").first.press("Enter")

            # 21 Tinggi Dasar Awan Lapisan 1
            self.page.locator("#cloud_low_base_1").click()
            self.page.locator("#cloud_low_base_1").fill(self.user_input.get('tinggi_dasar_aw_lapisan1', ''))

            # 23 Arah Gerak Awan Lapisan 1
            arah_gerak_aw_lap1_value = self.arah_angin.get(self.user_input.get('arah_gerak_aw_lapisan1', ''), "0")
            self.page.locator("div:nth-child(7) > .ant-select-selection__rendered").first.click()
            self.page.locator(
                "div:nth-child(7) > .ant-select-selection__rendered > .ant-select-search__field__wrap > .ant-select-search__field").first.fill(
                arah_gerak_aw_lap1_value)

        except Exception as e:
            logging.error(f"Error filling additional CL fields: {e}")
            raise

    def fill_special_cloud_layer_1(self, arah_gerak_aw_lap1_value):
        """Fills data for special cloud conditions (Cumulus or Cumulonimbus)."""
        logging.info("Filling special cloud data for Cumulus/Cumulonimbus")
        try:
            # 22 Tinggi Puncak Awan Lapisan 1
            has_peak = self.user_input.get('tinggi_puncak_aw_lapisan1', '')
            if has_peak:
                self.click_and_fill("#cloud_low_peak_1", has_peak)

                # 24 Sudut Elevasi Awan Lapisan 1
                self.click_and_fill("#cloud_elevation_1_angle_ec",
                                    str(self.user_input.get('sudut_elevasi_aw_lapisan1', '')))
                self.press_enter("#cloud_elevation_1_angle_ec")

                # Arah Gerak Awan Lapisan 1
                self.click_and_fill("div:nth-child(9) > .ant-select-selection__rendered", arah_gerak_aw_lap1_value)

            # Call method to fill second cloud layer if needed
            self.input_cloud_layer_2()

        except Exception as e:
            logging.error(f"Error filling special cloud layer data: {e}")
            raise

    def input_cloud_layer_2(self):
        """Mengisi data untuk lapisan awan kedua (CL Lapisan 2) berdasarkan user_input."""
        logging.info("Filling data for the second cloud layer (CL Lapisan 2)")
        try:
            # 25 Activate switch for the second cloud layer
            logging.info("Activating second cloud layer")
            self.page.locator(".switch-icon-left > .feather").first.click()

            # 26 Jenis CL Lapisan 2
            logging.info("Filling jenis CL Lapisan 2")
            jenis_cl_lap2_value = self.awan_lapisan.get(self.user_input.get('jenis_cl_lapisan2', ''), "0")
            self.select_dropdown_option("div:nth-child(3) > div:nth-child(3) > .ant-select > .ant-select-selection",
                                        jenis_cl_lap2_value)

            # 27 Jumlah CL Lapisan 2
            logging.info("Filling jumlah CL Lapisan 2")
            self.click_and_fill(
                "div:nth-child(3) > div:nth-child(4) > .ant-select-selection__rendered > .ant-select-search__field__wrap > .ant-select-search__field",
                self.user_input.get('jumlah_cl_lapisan2', ''))
            self.page.get_by_role("option", name="oktas").click()

            # 28 Tinggi Dasar Awan Lapisan 2
            logging.info("Filling tinggi dasar awan lapisan 2")
            self.click_and_fill("#cloud_low_base_2", self.user_input.get('tinggi_dasar_aw_lapisan2', ''))

            # 29 Arah Gerak Awan Lapisan 2
            logging.info("Filling arah gerak awan lapisan 2")
            arah_gerak_aw_lap2_value = self.arah_angin.get(self.user_input.get('arah_gerak_aw_lapisan2', ''), "0")
            self.click_and_fill(
                "div:nth-child(3) > div:nth-child(7) > .ant-select-selection__rendered > .ant-select-search__field",
                arah_gerak_aw_lap2_value)

        except Exception as e:
            logging.error(f"Error filling data for cloud layer 2: {e}")
            raise

    def fill_cm_mid_level_cloud(self):
        """Fills medium-level cloud (CM) data based on user input."""
        logging.info("Filling medium-level cloud (CM) data")
        try:
            # 30 CM Awan Menengah
            cm_value = self.cm.get(self.user_input.get('cm_awan_menengah', ''), "0")
            # Click the dropdown and fill the value using role 'textbox'
            self.page.locator("#cloud_med_type_cm div").nth(1).click()
            self.page.locator("#cloud_med_type_cm").get_by_role("textbox").fill(cm_value)
            self.page.locator("#cloud_med_type_cm").get_by_role("textbox").press("Enter")

            # Conditional: If cm_value is "0", skip the remaining steps
            if cm_value != "0":
                # 31 NCM Jumlah Awan Menengah
                self.page.locator("#cloud_med_cover_oktas div").nth(1).click()
                self.page.locator("#cloud_med_cover_oktas").get_by_role("textbox").fill(
                    self.user_input.get('ncm_awan_menengah', ''))
                self.page.locator("#cloud_med_cover_oktas").get_by_role("textbox").press("Enter")

                # 32 Jenis Awan Menengah
                jenis_awan_menengah_value = self.awan_lapisan.get(self.user_input.get('jenis_awan_menengah', ''), "0")
                self.page.locator(".col-4 > div:nth-child(3) > .ant-select > .ant-select-selection").first.click()
                self.page.get_by_role("option", name=jenis_awan_menengah_value).click()

                # 33 Jumlah Awan Menengah
                jumlah_awan_menengah = self.user_input['ncm_awan_menengah']
                self.page.locator(".col-4 > div:nth-child(4) > .ant-select > .ant-select-selection > .ant-select-selection__rendered").first.click()
                self.page.locator(".col-4 > div:nth-child(4) > .ant-select > .ant-select-selection > .ant-select-selection__rendered > .ant-select-search > .ant-select-search__field__wrap > .ant-select-search__field").first.fill(jumlah_awan_menengah)
                self.page.locator(".col-4 > div:nth-child(4) > .ant-select > .ant-select-selection > .ant-select-selection__rendered").first.press("Enter")


                # 34 Tinggi Dasar Awan Menengah
                self.page.locator("#cloud_med_base_1").click()
                self.page.locator("#cloud_med_base_1").fill(self.user_input.get('tinggi_dasar_aw_cm', ''))

                # 35 Arah Gerak Awan CM
                arah_gerak_cm_value = self.arah_angin.get(self.user_input['arah_gerak_cm'], "0")
                self.page.locator(
                    "div:nth-child(6) > .ant-select > .ant-select-selection > .ant-select-selection__rendered").first.click()
                self.page.locator(
                    "div:nth-child(6) > .ant-select > .ant-select-selection > .ant-select-selection__rendered > .ant-select-search > .ant-select-search__field__wrap > .ant-select-search__field").first.fill(
                    arah_gerak_cm_value)

        except Exception as e:
            logging.error(f"Error filling CM mid-level cloud data: {e}")
            raise

    def fill_ch_high_level_cloud(self):
        """Fills high-level cloud (CH) data based on user input."""
        logging.info("Filling high-level cloud (CH) data")
        try:
            # 36 CH Awan Tinggi
            ch_value = self.ch.get(self.user_input['ch_awan_tinggi'], "0")
            self.page.locator("#cloud_high_type_ch div").nth(1).click()
            self.page.locator("#cloud_high_type_ch").get_by_role("textbox").fill(ch_value)
            self.page.locator("#cloud_high_type_ch").get_by_role("textbox").press("Enter")

            if ch_value != "0":
                # 37 NCH jumah awan tinggi
                self.page.locator("#cloud_high_cover_oktas div").nth(1).click()
                self.page.locator("#cloud_high_cover_oktas").get_by_role("textbox").fill(self.user_input['nch_awan_tinggi'])
                self.page.locator("#cloud_high_cover_oktas div").nth(1).press("Enter")

                # 38 jenis awan tinggi
                jenis_awan_tinggi_value = self.awan_lapisan.get(self.user_input['ch_awan_tinggi'], "0")
                self.page.locator("div:nth-child(3) > .card > .card-body > #collapse-row-2 > div > div:nth-child(2) > div:nth-child(3) > .ant-select > .ant-select-selection > .ant-select-selection__rendered").click()
                self.page.get_by_role("option", name=jenis_awan_tinggi_value).click()

                # # 39 Jumlah awan tinggi
                jumlah_awan_tinggi = self.user_input['nch_awan_tinggi']
                self.page.locator("div:nth-child(3) > .card > .card-body > #collapse-row-2 > div > div:nth-child(2) > div:nth-child(4) > .ant-select > .ant-select-selection > .ant-select-selection__rendered").click()
                self.page.locator("div:nth-child(3) > .card > .card-body > #collapse-row-2 > div > div:nth-child(2) > div:nth-child(4) > .ant-select > .ant-select-selection > .ant-select-selection__rendered > .ant-select-search > .ant-select-search__field__wrap > .ant-select-search__field").fill(jumlah_awan_tinggi)
                # page.get_by_role("option", name=f"- {jumlah_awan_tinggi} oktas").click()
                self.page.locator("div:nth-child(3) > .card > .card-body > #collapse-row-2 > div > div:nth-child(2) > div:nth-child(4) > .ant-select > .ant-select-selection > .ant-select-selection__rendered").press("Enter")

                # 40 Tinggi Dasar Awan Tinggi
                self.page.locator("#cloud_high_base_1").click()
                self.page.locator("#cloud_high_base_1").fill(self.user_input['tinggi_dasar_aw_ch'])

                # 41 Arah Gerak Awan CH
                arah_gerak_ch_value = self.arah_angin.get(self.user_input['arah_gerak_ch'], "0")
                self.page.locator("div:nth-child(3) > .card > .card-body > #collapse-row-2 > div > div:nth-child(2) > div:nth-child(6) > .ant-select > .ant-select-selection > .ant-select-selection__rendered").click()
                self.page.locator("div:nth-child(3) > .card > .card-body > #collapse-row-2 > div > div:nth-child(2) > div:nth-child(6) > .ant-select > .ant-select-selection > .ant-select-selection__rendered > .ant-select-search > .ant-select-search__field__wrap > .ant-select-search__field").fill(arah_gerak_ch_value)


        except Exception as e:
            logging.error(f"Error filling high-level cloud data: {e}")
            raise

    def fill_land_condition(self):
        """Fills the land condition field based on user input."""
        logging.info("Filling land condition (Keadaan Tanah)")
        try:
            # 45 Keadaan Tanah
            self.page.locator("#land_cond div").nth(1).click()
            self.page.locator("#land_cond").get_by_role("textbox").fill(self.user_input['keadaan_tanah'])
            self.page.locator("#land_cond").get_by_role("textbox").press("Enter")

        except Exception as e:
            logging.error(f"Error filling land condition or clicking preview: {e}")
            raise

    def click_preview_button(self):
        """Clicks the Preview button."""
        logging.info("Clicking Preview button")
        try:
            self.page.get_by_role("button", name="Preview").click()
        except Exception as e:
            logging.error(f"Error clicking Preview button: {e}")
            raise


class InputProcessor:
    def __init__(self):
        pass

    def process(self, data):
        # Placeholder for processing logic
        return data