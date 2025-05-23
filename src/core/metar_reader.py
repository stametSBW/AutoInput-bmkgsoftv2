"""
METAR code parsing functionality.
"""
import re
import logging
from datetime import datetime
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

class MetarReader:
    """Parses METAR codes into structured data."""

    def __init__(self, metar_code: str):
        """Initialize the METAR reader.
        
        Args:
            metar_code: Raw METAR code string
        """
        self.metar_code = metar_code.strip().rstrip('=')  # Remove trailing = if present
        self.parts = self.metar_code.split()
        self.current_index = 0

    def _get_next_part(self) -> str:
        """Get the next part of the METAR code.
        
        Returns:
            str: Next part of the METAR code
        """
        if self.current_index < len(self.parts):
            part = self.parts[self.current_index]
            self.current_index += 1
            return part
        return ""

    def _peek_next_part(self) -> str:
        """Look at the next part without advancing.
        
        Returns:
            str: Next part of the METAR code
        """
        if self.current_index < len(self.parts):
            return self.parts[self.current_index]
        return ""

    def _parse_station(self, station_part: str) -> str:
        """Parse station identifier.
        
        Args:
            station_part: Station section of METAR code
            
        Returns:
            str: Station identifier
        """
        parts = station_part.split()
        if len(parts) != 2 or parts[0] != "METAR":
            raise ValueError(f"Invalid METAR code format: {station_part}")
        return parts[1]

    def _parse_datetime(self, datetime_part: str) -> tuple:
        """Parse date and time.
        
        Args:
            datetime_part: Date/time section of METAR code
            
        Returns:
            tuple: (day, hour, minute)
        """
        # Remove Z suffix if present
        datetime_part = datetime_part.rstrip('Z')
        
        if not re.match(r"\d{6}", datetime_part):
            raise ValueError(f"Invalid date/time format: {datetime_part}")
            
        day = datetime_part[:2]
        hour = datetime_part[2:4]
        minute = datetime_part[4:6]
        
        return day, hour, minute

    def _parse_wind(self) -> tuple:
        """Parse wind information including variable wind directions.
        
        Returns:
            tuple: (direction, speed, variable_from, variable_to)
        """
        wind_part = self._get_next_part()
        variable_from = None
        variable_to = None
        
        # Handle calm or variable winds
        if wind_part == "00000KT":
            return "000", "00", None, None
        elif wind_part == "VRB00KT":
            return "VRB", "00", None, None
        
        # Handle standard wind format (dddssKT or VRBssKT)
        match = re.match(r"(VRB|\d{3})(\d{2,3})(?:G\d{2,3})?KT", wind_part)
        if not match:
            raise ValueError(f"Invalid wind format: {wind_part}")
        
        direction, speed = match.groups()
        
        # Check for variable wind direction range
        next_part = self._peek_next_part()
        if next_part and re.match(r"\d{3}V\d{3}", next_part):
            var_part = self._get_next_part()
            var_match = re.match(r"(\d{3})V(\d{3})", var_part)
            if var_match:
                variable_from, variable_to = var_match.groups()
        
        return direction, speed, variable_from, variable_to

    def _parse_visibility(self) -> tuple:
        """Parse visibility including special cases like CAVOK.
        
        Returns:
            tuple: (visibility, is_cavok)
        """
        part = self._peek_next_part()
        
        # Handle CAVOK
        if part == "CAVOK":
            self._get_next_part()  # Consume CAVOK
            return "10000", True
            
        # Handle standard visibility
        visibility = self._get_next_part()
        if visibility == "9999":
            visibility = "10000"
            
        return visibility, False

    def _parse_weather(self) -> List[str]:
        """Parse current weather phenomena.
        
        Returns:
            list: List of weather phenomena
        """
        weather = []
        while True:
            part = self._peek_next_part()
            if not part or not any(part.startswith(prefix) for prefix in ["+", "-", "VC", "MI", "BC", "PR", "DR", "BL", "SH", "TS", "FZ", "DZ", "RA", "SN", "SG", "IC", "PL", "GR", "GS", "UP", "BR", "FG", "FU", "VA", "DU", "SA", "HZ", "PY", "PO", "SQ", "FC", "SS", "DS"]):
                break
            weather.append(self._get_next_part())
        return weather

    def _parse_clouds(self) -> List[Dict[str, str]]:
        """Parse cloud information.
        
        Returns:
            list: List of cloud dictionaries
        """
        clouds = []
        while self.current_index < len(self.parts):
            part = self._peek_next_part()
            if not any(part.startswith(prefix) for prefix in ["FEW", "SCT", "BKN", "OVC"]):
                break
                
            cloud_part = self._get_next_part()
            match = re.match(r"(FEW|SCT|BKN|OVC)(\d{3})(CB|TCU)?", cloud_part)
            if not match:
                raise ValueError(f"Invalid cloud format: {cloud_part}")
                
            cloud_type, height, subtype = match.groups()
            clouds.append({
                "cloud_type": cloud_type,
                "cloud_height": height,
                "cloud_subtype": subtype or ""
            })
            
        return clouds

    def _parse_temperature_dew_point(self, temp_part: str) -> tuple:
        """Parse temperature and dew point.
        
        Args:
            temp_part: Temperature section of METAR code
            
        Returns:
            tuple: (temperature, dew_point)
        """
        match = re.match(r"(M?\d{2})/(M?\d{2})", temp_part)
        if not match:
            raise ValueError(f"Invalid temperature format: {temp_part}")
            
        temp, dew = match.groups()
        temp = temp.replace("M", "-")
        dew = dew.replace("M", "-")
        return temp, dew

    def _parse_pressure(self, pressure_part: str) -> str:
        """Parse pressure value.
        
        Args:
            pressure_part: Pressure section of METAR code
            
        Returns:
            str: Pressure value
        """
        match = re.match(r"Q(\d{4})", pressure_part)
        if not match:
            raise ValueError(f"Invalid pressure format: {pressure_part}")
            
        return match.group(1)

    def _parse_trend(self) -> Dict[str, Any]:
        """Parse trend information.
        
        Returns:
            dict: Trend information including type and details
        """
        trend_info = {"type": "", "details": ""}
        
        part = self._peek_next_part()
        if not part:
            return trend_info
            
        if part in ["NOSIG", "TEMPO", "BECMG"]:
            trend_info["type"] = self._get_next_part()
            
            # Parse additional trend information (e.g., TL0730)
            while self.current_index < len(self.parts):
                next_part = self._peek_next_part()
                if next_part and next_part.startswith("RMK"):
                    break
                if next_part:
                    trend_info["details"] += " " + self._get_next_part()
                else:
                    break
                    
            trend_info["details"] = trend_info["details"].strip()
            
        return trend_info

    def _parse_remarks(self) -> str:
        """Parse remarks section.
        
        Returns:
            str: Remarks text
        """
        remarks = ""
        while self.current_index < len(self.parts):
            part = self._peek_next_part()
            if part and (part == "RMK" or remarks):
                remarks += " " + self._get_next_part()
            else:
                break
        return remarks.strip()

    def parse(self) -> Dict[str, Any]:
        """Parse the METAR code into structured data.
        
        Returns:
            dict: Parsed METAR data
        """
        try:
            parts = self.metar_code.split()
            if len(parts) < 2 or parts[0] != "METAR":
                raise ValueError("Invalid METAR code format: Missing METAR identifier")
                
            # Get station identifier
            station = parts[1]
            self.current_index = 2  # Skip "METAR" and station identifier
            
            # Get date/time
            datetime_part = self._get_next_part()
            day, hour, minute = self._parse_datetime(datetime_part)
            
            # Get wind
            wind_direction, wind_speed, variable_from, variable_to = self._parse_wind()
            
            # Get visibility and check for CAVOK
            visibility, is_cavok = self._parse_visibility()
            
            # Get weather phenomena if present
            weather = [] if is_cavok else self._parse_weather()
            
            # Get clouds if not CAVOK
            clouds = [] if is_cavok else self._parse_clouds()
            
            # Get temperature and dew point
            temp_part = self._get_next_part()
            temperature, dew_point = self._parse_temperature_dew_point(temp_part)
            
            # Get pressure
            pressure_part = self._get_next_part()
            pressure = self._parse_pressure(pressure_part)
            
            # Get trend information
            trend_info = self._parse_trend()
            
            # Get remarks if present
            remarks = self._parse_remarks()

            return {
                "station": station,
                "day": day,
                "hour": hour,
                "minute": minute,
                "wind_direction": wind_direction,
                "wind_speed": wind_speed,
                "wind_variable_from": variable_from,
                "wind_variable_to": variable_to,
                "visibility": visibility,
                "cavok": is_cavok,
                "weather": weather,
                "clouds": clouds,
                "temperature": temperature,
                "dew_point": dew_point,
                "pressure": pressure,
                "trend_type": trend_info["type"],
                "trend_details": trend_info["details"],
                "remarks": remarks
            }

        except Exception as e:
            logger.error(f"Error parsing METAR code: {e}")
            raise ValueError(f"Failed to parse METAR code: {str(e)}") 