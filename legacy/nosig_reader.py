import re

class MetarReader:
    """Parser for METAR data"""
    def __init__(self, metar_code):
        self.metar_code = metar_code.strip().rstrip('=')  # Remove trailing = if present
        self.parsed_metar = {}

    def parse(self):
        self.read_station()
        self.read_time()
        self.read_wind()
        self.read_visibility()
        self.read_weather()
        self.read_clouds()
        self.read_temperature()
        self.read_pressure()
        self.read_trend()
        self.read_remarks()
        return self.parsed_metar

    def read_station(self):
        """Parse station identifier."""
        station_regex = r'METAR\s+(\w+)'
        station_match = re.search(station_regex, self.metar_code)
        if station_match:
            self.parsed_metar['station'] = station_match.group(1)

    def read_time(self):
        """Parse date and time."""
        time_regex = r'(\d{2})(\d{2})(\d{2})Z?'  # Made Z optional
        time_match = re.search(time_regex, self.metar_code)
        if time_match:
            day, hour, minute = time_match.groups()
            self.parsed_metar['day'] = day
            self.parsed_metar['hour'] = hour
            self.parsed_metar['minute'] = minute

    def read_wind(self):
        """Parse wind information including variable directions."""
        # Handle variable winds and gusts
        wind_regex = r'(VRB|\d{3})(\d{2,3})(?:G\d{2,3})?KT'
        wind_match = re.search(wind_regex, self.metar_code)
        if wind_match:
            direction = wind_match.group(1)
            speed = wind_match.group(2)
            # Handle calm winds
            if direction == "000" and speed == "00":
                direction = "000"
                speed = "00"
            self.parsed_metar['wind_direction'] = direction
            self.parsed_metar['wind_speed'] = speed

            # Check for variable wind direction range
            var_regex = r'(\d{3})V(\d{3})'
            var_match = re.search(var_regex, self.metar_code)
            if var_match:
                self.parsed_metar['wind_variable_from'] = var_match.group(1)
                self.parsed_metar['wind_variable_to'] = var_match.group(2)

    def read_visibility(self):
        """Parse visibility including CAVOK."""
        # Check for CAVOK first
        if 'CAVOK' in self.metar_code:
            self.parsed_metar['visibility'] = '10000'
            self.parsed_metar['cavok'] = True
            return

        # Regular visibility
        visibility_regex = r'\s(\d{4})\s'
        visibility_match = re.search(visibility_regex, self.metar_code)
        if visibility_match:
            visibility_value = visibility_match.group(1)
            if visibility_value == '9999':
                visibility_value = '10000'
            self.parsed_metar['visibility'] = visibility_value
            self.parsed_metar['cavok'] = False

    def read_weather(self):
        """Parse current weather phenomena."""
        weather_phenomena = []
        weather_regex = r'\s([-+]?(?:RA|SN|SG|IC|PL|GR|GS|DZ|TS|FG|BR|SA|HZ|FU|VA|DU|SQ|PO|FC|SS|DS)(?:\s|$))'
        weather_matches = re.finditer(weather_regex, self.metar_code)
        for match in weather_matches:
            weather_phenomena.append(match.group(1).strip())
        self.parsed_metar['weather'] = weather_phenomena

    def read_clouds(self):
        """Parse cloud information."""
        if self.parsed_metar.get('cavok', False):
            self.parsed_metar['clouds'] = []
            return

        # Extracting cloud type and cloud subtype, converting height into thousands of feet
        cloud_regex = r'(FEW|SCT|BKN|OVC)(\d{3})(CB|TCU)?'
        cloud_matches = re.findall(cloud_regex, self.metar_code)
        if cloud_matches:
            clouds = []
            for cloud_type, cloud_height, cloud_subtype in cloud_matches:
                # Convert cloud height to thousands of feet (e.g., 018 -> 1800 feet)
                height_in_feet = int(cloud_height) * 100
                clouds.append({
                    'cloud_type': cloud_type,
                    'cloud_height': height_in_feet,
                    'cloud_subtype': cloud_subtype if cloud_subtype else None
                })
            self.parsed_metar['clouds'] = clouds

    def read_temperature(self):
        """Parse temperature and dew point."""
        temp_regex = r'(M?\d{2})/(M?\d{2})'  # Handle negative temperatures with M prefix
        temp_match = re.search(temp_regex, self.metar_code)
        if temp_match:
            temp, dew = temp_match.groups()
            # Convert M prefix to minus sign
            temp = temp.replace('M', '-')
            dew = dew.replace('M', '-')
            self.parsed_metar['temperature'] = temp
            self.parsed_metar['dew_point'] = dew

    def read_pressure(self):
        """Parse pressure value."""
        pressure_regex = r'Q(\d{4})'
        pressure_match = re.search(pressure_regex, self.metar_code)
        if pressure_match:
            self.parsed_metar['pressure'] = pressure_match.group(1)

    def read_trend(self):
        """Parse trend information."""
        # Basic trend type
        trend_regex = r'\s(NOSIG|TEMPO|BECMG)(?:\s|$)'
        trend_match = re.search(trend_regex, self.metar_code)
        if trend_match:
            trend_type = trend_match.group(1)
            self.parsed_metar['trend_type'] = trend_type

            # Get additional trend details if TEMPO or BECMG
            if trend_type in ['TEMPO', 'BECMG']:
                # Look for time indicators and conditions after trend type
                details_regex = fr'{trend_type}\s+(.*?)(?=\s+RMK\s+|$)'
                details_match = re.search(details_regex, self.metar_code)
                if details_match:
                    self.parsed_metar['trend_details'] = details_match.group(1).strip()
                else:
                    self.parsed_metar['trend_details'] = ''
            else:
                self.parsed_metar['trend_details'] = ''

    def read_remarks(self):
        """Parse remarks section."""
        remarks_regex = r'RMK\s+(.+?)(?=$)'
        remarks_match = re.search(remarks_regex, self.metar_code)
        if remarks_match:
            self.parsed_metar['remarks'] = remarks_match.group(1).strip()
        else:
            self.parsed_metar['remarks'] = ''

    @staticmethod
    def read_metar_code(metar_code):
        reader = MetarReader(metar_code)
        return reader.parse()