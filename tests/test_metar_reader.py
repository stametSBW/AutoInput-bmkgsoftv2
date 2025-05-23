import pytest
from src.core.metar_reader import MetarReader
import json

# Test METAR codes with expected results
TEST_CASES = [
    {
        "metar": "METAR WADS 230030Z 15005KT 9999 FEW020 28/25 Q1008 NOSIG=",
        "expected": {
            "station": "WADS",
            "day": "23",
            "hour": "00",
            "minute": "30",
            "wind_direction": "150",
            "wind_speed": "05",
            "visibility": "10000",
            "clouds": [{"cloud_type": "FEW", "cloud_height": "020", "cloud_subtype": ""}],
            "temperature": "28",
            "dew_point": "25",
            "pressure": "1008",
            "trend_type": "NOSIG"
        }
    },
    {
        "metar": "METAR WADS 230000Z 15006KT 9999 FEW020 27/25 Q1008 NOSIG=",
        "expected": {
            "station": "WADS",
            "day": "23",
            "hour": "00",
            "minute": "00",
            "wind_direction": "150",
            "wind_speed": "06",
            "visibility": "10000",
            "clouds": [{"cloud_type": "FEW", "cloud_height": "020", "cloud_subtype": ""}],
            "temperature": "27",
            "dew_point": "25",
            "pressure": "1008",
            "trend_type": "NOSIG"
        }
    },
    {
        "metar": "METAR WADS 130200Z 13003KT 9999 FEW018CB SCT020 30/25 Q1010 NOSIG RMK CB TO NW=",
        "expected": {
            "station": "WADS",
            "day": "13",
            "hour": "02",
            "minute": "00",
            "wind_direction": "130",
            "wind_speed": "03",
            "visibility": "10000",
            "clouds": [
                {"cloud_type": "FEW", "cloud_height": "018", "cloud_subtype": "CB"},
                {"cloud_type": "SCT", "cloud_height": "020", "cloud_subtype": ""}
            ],
            "temperature": "30",
            "dew_point": "25",
            "pressure": "1010",
            "trend_type": "NOSIG",
            "remarks": "RMK CB TO NW"
        }
    },
    {
        "metar": "METAR WADS 130630Z 07004KT 9000 RA BKN018 31/26 Q1006 TEMPO TL0730 RA=",
        "expected": {
            "station": "WADS",
            "day": "13",
            "hour": "06",
            "minute": "30",
            "wind_direction": "070",
            "wind_speed": "04",
            "visibility": "9000",
            "weather": ["RA"],
            "clouds": [{"cloud_type": "BKN", "cloud_height": "018", "cloud_subtype": ""}],
            "temperature": "31",
            "dew_point": "26",
            "pressure": "1006",
            "trend_type": "TEMPO",
            "trend_details": "TL0730 RA"
        }
    },
    {
        "metar": "METAR WADS 131100Z 19003KT 150V220 7000 SCT018 28/28 Q1008 NOSIG=",
        "expected": {
            "station": "WADS",
            "day": "13",
            "hour": "11",
            "minute": "00",
            "wind_direction": "190",
            "wind_speed": "03",
            "wind_variable_from": "150",
            "wind_variable_to": "220",
            "visibility": "7000",
            "clouds": [{"cloud_type": "SCT", "cloud_height": "018", "cloud_subtype": ""}],
            "temperature": "28",
            "dew_point": "28",
            "pressure": "1008",
            "trend_type": "NOSIG"
        }
    },
    {
        "metar": "METAR WADS 131130Z 12006KT 080V140 5000 RA BKN018 28/27 Q1008 TEMPO TL1230 RA=",
        "expected": {
            "station": "WADS",
            "day": "13",
            "hour": "11",
            "minute": "30",
            "wind_direction": "120",
            "wind_speed": "06",
            "wind_variable_from": "080",
            "wind_variable_to": "140",
            "visibility": "5000",
            "weather": ["RA"],
            "clouds": [{"cloud_type": "BKN", "cloud_height": "018", "cloud_subtype": ""}],
            "temperature": "28",
            "dew_point": "27",
            "pressure": "1008",
            "trend_type": "TEMPO",
            "trend_details": "TL1230 RA"
        }
    },
    {
        "metar": "METAR WADS 132030Z 13003KT 8000 FEW020CB 25/25 Q1009 NOSIG RMK CB TO N=",
        "expected": {
            "station": "WADS",
            "day": "13",
            "hour": "20",
            "minute": "30",
            "wind_direction": "130",
            "wind_speed": "03",
            "visibility": "8000",
            "clouds": [{"cloud_type": "FEW", "cloud_height": "020", "cloud_subtype": "CB"}],
            "temperature": "25",
            "dew_point": "25",
            "pressure": "1009",
            "trend_type": "NOSIG",
            "remarks": "RMK CB TO N"
        }
    },
    {
        "metar": "METAR WADS 150630Z 33008KT 8000 FEW017TCU SCT018 32/26 Q1007 NOSIG RMK TCU TO S=",
        "expected": {
            "station": "WADS",
            "day": "15",
            "hour": "06",
            "minute": "30",
            "wind_direction": "330",
            "wind_speed": "08",
            "visibility": "8000",
            "clouds": [
                {"cloud_type": "FEW", "cloud_height": "017", "cloud_subtype": "TCU"},
                {"cloud_type": "SCT", "cloud_height": "018", "cloud_subtype": ""}
            ],
            "temperature": "32",
            "dew_point": "26",
            "pressure": "1007",
            "trend_type": "NOSIG",
            "remarks": "RMK TCU TO S"
        }
    },
    {
        "metar": "METAR WADS 150730Z 34005KT 310V020 9000 SCT020 31/26 Q1007 NOSIG=",
        "expected": {
            "station": "WADS",
            "day": "15",
            "hour": "07",
            "minute": "30",
            "wind_direction": "340",
            "wind_speed": "05",
            "wind_variable_from": "310",
            "wind_variable_to": "020",
            "visibility": "9000",
            "clouds": [{"cloud_type": "SCT", "cloud_height": "020", "cloud_subtype": ""}],
            "temperature": "31",
            "dew_point": "26",
            "pressure": "1007",
            "trend_type": "NOSIG"
        }
    },
    {
        "metar": "METAR WADS 151700Z VRB02KT 5000 RA FEW015CB BKN017 26/26 Q1010 NOSIG RMK CB OTF=",
        "expected": {
            "station": "WADS",
            "day": "15",
            "hour": "17",
            "minute": "00",
            "wind_direction": "VRB",
            "wind_speed": "02",
            "visibility": "5000",
            "weather": ["RA"],
            "clouds": [
                {"cloud_type": "FEW", "cloud_height": "015", "cloud_subtype": "CB"},
                {"cloud_type": "BKN", "cloud_height": "017", "cloud_subtype": ""}
            ],
            "temperature": "26",
            "dew_point": "26",
            "pressure": "1010",
            "trend_type": "NOSIG",
            "remarks": "RMK CB OTF"
        }
    },
    {
        "metar": "METAR WADS 170000Z 13002KT CAVOK 27/25 Q1010 NOSIG=",
        "expected": {
            "station": "WADS",
            "day": "17",
            "hour": "00",
            "minute": "00",
            "wind_direction": "130",
            "wind_speed": "02",
            "visibility": "10000",
            "cavok": True,
            "clouds": [],
            "temperature": "27",
            "dew_point": "25",
            "pressure": "1010",
            "trend_type": "NOSIG"
        }
    },
    {
        "metar": "METAR WADS 010100Z VRB01KT 9999 FEW020 30/26 Q1010 NOSIG=",
        "expected": {
            "station": "WADS",
            "day": "01",
            "hour": "01",
            "minute": "00",
            "wind_direction": "VRB",
            "wind_speed": "01",
            "visibility": "10000",
            "clouds": [{"cloud_type": "FEW", "cloud_height": "020", "cloud_subtype": ""}],
            "temperature": "30",
            "dew_point": "26",
            "pressure": "1010",
            "trend_type": "NOSIG"
        }
    },
    {
        "metar": "METAR WADS 010130Z VRB02KT 9999 FEW020 31/26 Q1010 NOSIG=",
        "expected": {
            "station": "WADS",
            "day": "01",
            "hour": "01",
            "minute": "30",
            "wind_direction": "VRB",
            "wind_speed": "02",
            "visibility": "10000",
            "clouds": [{"cloud_type": "FEW", "cloud_height": "020", "cloud_subtype": ""}],
            "temperature": "31",
            "dew_point": "26",
            "pressure": "1010",
            "trend_type": "NOSIG"
        }
    }
]

def test_metar_parsing():
    """Test METAR code parsing with various formats"""
    for test_case in TEST_CASES:
        metar_code = test_case["metar"]
        expected = test_case["expected"]
        
        reader = MetarReader(metar_code)
        result = reader.parse()
        
        # Check that all expected values are present in the result
        for key, value in expected.items():
            assert result[key] == value, f"Failed parsing {key} in METAR: {metar_code}"

def test_variable_wind():
    """Test parsing of variable wind directions"""
    test_cases = [
        {
            "metar": "METAR WADS 131100Z 19003KT 150V220 7000 SCT018 28/28 Q1008 NOSIG=",
            "wind_direction": "190",
            "wind_speed": "03",
            "variable_from": "150",
            "variable_to": "220"
        },
        {
            "metar": "METAR WADS 131130Z 12006KT 080V140 5000 RA BKN018 28/27 Q1008 TEMPO TL1230 RA=",
            "wind_direction": "120",
            "wind_speed": "06",
            "variable_from": "080",
            "variable_to": "140"
        },
        {
            "metar": "METAR WADS 150730Z 34005KT 310V020 9000 SCT020 31/26 Q1007 NOSIG=",
            "wind_direction": "340",
            "wind_speed": "05",
            "variable_from": "310",
            "variable_to": "020"
        }
    ]
    
    for test_case in test_cases:
        reader = MetarReader(test_case["metar"])
        result = reader.parse()
        
        assert result["wind_direction"] == test_case["wind_direction"]
        assert result["wind_speed"] == test_case["wind_speed"]
        assert result["wind_variable_from"] == test_case["variable_from"]
        assert result["wind_variable_to"] == test_case["variable_to"]

def test_weather_phenomena():
    """Test parsing of weather phenomena and remarks"""
    test_cases = [
        {
            "metar": "METAR WADS 130630Z 07004KT 9000 RA BKN018 31/26 Q1006 TEMPO TL0730 RA=",
            "weather": ["RA"],
            "trend_type": "TEMPO",
            "trend_details": "TL0730 RA"
        },
        {
            "metar": "METAR WADS 151700Z VRB02KT 5000 RA FEW015CB BKN017 26/26 Q1010 NOSIG RMK CB OTF=",
            "weather": ["RA"],
            "remarks": "RMK CB OTF"
        },
        {
            "metar": "METAR WADS 130200Z 13003KT 9999 FEW018CB SCT020 30/25 Q1010 NOSIG RMK CB TO NW=",
            "remarks": "RMK CB TO NW"
        }
    ]
    
    for test_case in test_cases:
        reader = MetarReader(test_case["metar"])
        result = reader.parse()
        
        if "weather" in test_case:
            assert all(wx in result["weather"] for wx in test_case["weather"])
        if "remarks" in test_case:
            assert result["remarks"] == test_case["remarks"]
        if "trend_type" in test_case:
            assert result["trend_type"] == test_case["trend_type"]
        if "trend_details" in test_case:
            assert result["trend_details"] == test_case["trend_details"]

def test_cloud_types():
    """Test parsing of different cloud types and special indicators"""
    test_cases = [
        {
            "metar": "METAR WADS 130200Z 13003KT 9999 FEW018CB SCT020 30/25 Q1010 NOSIG RMK CB TO NW=",
            "expected_clouds": [
                {"cloud_type": "FEW", "cloud_height": "018", "cloud_subtype": "CB"},
                {"cloud_type": "SCT", "cloud_height": "020", "cloud_subtype": ""}
            ]
        },
        {
            "metar": "METAR WADS 150630Z 33008KT 8000 FEW017TCU SCT018 32/26 Q1007 NOSIG RMK TCU TO S=",
            "expected_clouds": [
                {"cloud_type": "FEW", "cloud_height": "017", "cloud_subtype": "TCU"},
                {"cloud_type": "SCT", "cloud_height": "018", "cloud_subtype": ""}
            ]
        },
        {
            "metar": "METAR WADS 170000Z 13002KT CAVOK 27/25 Q1010 NOSIG=",
            "expected_clouds": []
        }
    ]
    
    for test_case in test_cases:
        reader = MetarReader(test_case["metar"])
        result = reader.parse()
        
        assert result["clouds"] == test_case["expected_clouds"]

if __name__ == "__main__":
    # This allows running the tests with detailed output
    import sys
    import pytest
    sys.exit(pytest.main([__file__, "-v"])) 