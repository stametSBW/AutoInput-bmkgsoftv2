"""
BMKG code mappings and default configurations.
"""

# Observer mappings
obs = {
    "zulkifli": "Zulkifli Ramadhan",
    "adw": "Angga Dwi Wibowo",
    "dwi": "Dwi Harjanto",
    "risna": "Ni Putu Risna Purwandari",
    "fajar": "Fajaruddin Ash Shiddiq",
    "titis": "Titis Wicaksono",
    "hudan": "Hudan Pulung Hanasti"
}
# Default user input configuration
default_user_input = {
    'obs_onduty': 'titis',
    'jam_pengamatan': '23',
    'pengenal_angin': '3',
    'arah_angin': '150',
    'kecepatan_angin': '11',
    'jarak_penglihatan': '10',
    'cuaca_pengamatan': 'MIST',
    'cuaca_w1': 'RAIN',
    'cuaca_w2': 'TS',
    'tekanan_qff': '1002.3',
    'tekanan_qfe': '1001.8',
    'suhu_bola_kering': '25.3',
    'suhu_bola_basah': '22.3',
    'suhu_maksimum': '23.4',
    'suhu_minimum': '23.4',
    'oktas': '6',
    'hujan_ditakar': '20',
    'cl_dominan': 'CU',
    'ncl_total': '6',
    'jenis_cl_lapisan1': 'SC',
    'jumlah_cl_lapisan1': '5',
    'tinggi_dasar_aw_lapisan1': '540',
    'tinggi_puncak_aw_lapisan1': '',
    'arah_gerak_aw_lapisan1': 'NORTH EAST',
    'sudut_elevasi_aw_lapisan1': '0',
    'jenis_cl_lapisan2': 'CU',
    'jumlah_cl_lapisan2': '4',
    'tinggi_dasar_aw_lapisan2': '600',
    'arah_gerak_aw_lapisan2': 'SOUTH EAST',
    'cm_awan_menengah': 'AC',
    'ncm_awan_menengah': '1',
    'jenis_awan_menengah': 'AS',
    'tinggi_dasar_aw_cm': '3000',
    'arah_gerak_cm': 'EAST',
    'ch_awan_tinggi': 'CI',
    'nch_awan_tinggi': '5',
    'tinggi_dasar_aw_ch': '9000',
    'arah_gerak_ch': 'WEST',
    'penguapan': '7.72',
    'pengenal_penguapan': '0',
    'lama_penyinaran': '7.76',
    'keadaan_tanah': '0'
}

ww = {
    "CLD DEV UNK": "00",
    "CLD DECR": "01",
    "CLD UNCH": "02",
    "CLD INCR": "03",
    "SMOKE": "04",
    "HAZE": "05",
    "DUST 06": "06",
    "DUST 07": "07",
    "SAND 07": "07",
    "DW": "08",
    "DUST WHIRL": "08",
    "SW": "08",
    "SAND WHIRL": "08",
    "DS 09": "09",
    "DUST STORM 09": "09",
    "SS 09": "09",
    "SAND STORM 09": "09",
    "MIST": "10",
    "SHALLOW FOG 11": "11",
    "SHALLOW FOG 12": "12",
    "LIGHTNING": "13",
    "PREC IN SIGHT 14": "14",
    "PREC IN SIGHT 15": "15",
    "PREC IN SIGHT 16": "16",
    "TS NO PREC": "17",
    "SQUALLS": "18",
    "FUNNEL CLD": "19",
    "RE DZ (NOT FR)": "20",
    "REDZ (NOT FR)": "20",
    "RE DZ": "20",
    "REDZ": "20",
    "SN GR": "20",
    "SNGR": "20",
    "RE RA (NOT FR)": "21",
    "RERA (NOT FR)": "21",
    "RE RA": "21",
    "RERA": "21",
    "RE SN": "22",
    "RE RA + SN": "23",
    "RE FR DZ": "24",
    "RE FR RA": "24",
    "RE SH OF RA": "25",
    "RE SH OF SN": "26",
    "RE SH OF RA + SN": "26",
    "RE SH OF HA": "27",
    "RE SH OF RA + HA": "27",
    "RE FOG": "28",
    "RE ICE FOG": "28",
    "RE TS": "29",
    "RETS": "29",
    "SL/MOD DS ATAU SS DECR": "30",
    "SL/MOD DS ATAU SS UNCH": "31",
    "SL/MOD DS ATAU SS INCR": "32",
    "SEV DS ATAU SS DECR": "33",
    "SEV DS ATAU SS UNCH": "34",
    "SEV DS ATAU SS INCR": "35",
    "SL/MOD DRIFTING SN LOW": "36",
    "HEAVY DRIFTING SN LOW": "37",
    "SL/MOD BLOWING SN HIGH": "38",
    "HEAVY BLOWING SN HIGH": "39",
    "FOG AT A DIST": "40",
    "FOG IN PATCHES": "41",
    "FOG SV THINNER": "42",
    "FOG SINV THINNER": "43",
    "FOG SV UNCH": "44",
    "FOG SINV UNCH": "45",
    "FOG SV THICKER": "46",
    "FOG SINV THICKER": "47",
    "FOG DEP RIME SV": "48",
    "FOG DEP RIME SINV": "49",
    "INTER SL DZ": "50",
    "CNS SL DZ": "51",
    "INTER MOD DZ": "52",
    "CNS MOD DZ": "53",
    "INTER HEAVY (DENSE) DZ": "54",
    "CNS HEAVY (DENSE) DZ": "55",
    "SL DZ FR": "56",
    "MOD/HEAVY (DENSE) DZ FR": "57",
    "SL DZ AND RA": "58",
    "MOD/HEAVY DZ AND RA": "59",
    "INTER SL RA": "60",
    "CNS SL RA": "61",
    "INTER MOD RA": "62",
    "CNS MOD RA": "63",
    "INTER HEAVY RA": "64",
    "CNS HEAVY RA": "65",
    "SL RA FR": "66",
    "MOD/HEAVY RA FR": "67",
    "SL RA AND SN": "68",
    "SL DZ AND SN": "68",
    "MOD/HEAVY RA AND SN": "69",
    "MOD/HEAVY DZ AND SN": "69",
    "INTER SL OF SNF": "70",
    "CNS SL OF SNF": "71",
    "INTER MOD OF SNF": "72",
    "CNS MOD OF SNF": "73",
    "INTER HEAVY OF SNF": "74",
    "CNS HEAVY OF SNF": "75",
    "DIAMOND DUST FOG": "76",
    "DIAMOND DUST NO FOG": "76",
    "SN GRAINS FOG": "77",
    "SN GRAINS NO FOG": "77",
    "SN CRISTAL FOG": "78",
    "SN CRISTAL NO FOG": "78",
    "ICE PELLETS": "79",
    "SL RA SH": "80",
    "MOD/HEAVY RA SH": "81",
    "VIOLENT RA SH": "82",
    "SL RA + SN SH": "83",
    "MOD/HEAVY RA + SN SH": "84",
    "SL SN SH 85": "85",
    "MOD/HEAVY SN SH 86": "86",
    "SL SN SH 87": "87",
    "MOD/HEAVY SN SH 88": "88",
    "SL HAIL SH": "89",
    "MOD/HEAVY HAIL SH": "90",
    "SL RA RE TS": "91",
    "MOD/HEAVY RA RE TS": "92",
    "SL SN ATAU RA + SN ATAU HA RE TS": "93",
    "MOD/HEAVY SN ATAU RA + SN ATAU HA RE TS": "94",
    "SL/MOD TS NO HA + RA ATAU RA + SN ATAU SN": "95",
    "SL/MOD TS NO HA + RA": "95",
    "SL/MOD TS + HA": "96",
    "HEAVY TS NO HA + RA ATAU RA + SN ATAU SN": "97",
    "HEAVY TS NO HA + RA": "97",
    "TS + DS/SS": "98",
    "HEAVY TS + HA": "99"
}

arah_angin = {
    "STNR": "0",
    "NO CLOUD": "0",
    "NORTH EAST": "1",
    "ne": "1",
    "25": "1",
    "30": "1",
    "35": "1",
    "40": "1",
    "45": "1",
    "50": "1",
    "55": "1",
    "60": "1",
    "65": "1",
    "EAST": "2",
    "E": "2",
    "70": "2",
    "75": "2",
    "80": "2",
    "85": "2",
    "90": "2",
    "95": "2",
    "100": "2",
    "105": "2",
    "110": "2",
    "SOUTH EAST": "3",
    "SE": "3",
    "115": "3",
    "120": "3",
    "125": "3",
    "130": "3",
    "135": "3",
    "140": "3",
    "145": "3",
    "150": "3",
    "155": "3",
    "SOUTH": "4",
    "S": "4",
    "160": "4",
    "165": "4",
    "170": "4",
    "175": "4",
    "180": "4",
    "185": "4",
    "190": "4",
    "195": "4",
    "200": "4",
    "SOUTH WEST": "5",
    "SW": "5",
    "205": "5",
    "210": "5",
    "215": "5",
    "220": "5",
    "225": "5",
    "230": "5",
    "235": "5",
    "240": "5",
    "245": "5",
    "WEST": "6",
    "W": "6",
    "250": "6",
    "255": "6",
    "260": "6",
    "265": "6",
    "270": "6",
    "275": "6",
    "280": "6",
    "285": "6",
    "290": "6",
    "NORTH WEST": "7",
    "NW": "7",
    "295": "7",
    "300": "7",
    "305": "7",
    "310": "7",
    "315": "7",
    "320": "7",
    "325": "7",
    "330": "7",
    "335": "7",
    "N": "8",
    "340": "8",
    "345": "8",
    "350": "8",
    "355": "8",
    "360": "8",
    "5": "8",
    "10": "8",
    "15": "8",
    "20": "8"
}

w1w2 = {
    "CLOUDY -": "0",
    "CLOUDY ±": "1",
    "CLOUDY +": "2",
    "SAND": "3",
    "HAZE": "4",
    "DZ": "5",
    "DRIZZEL": "5",
    "RAIN": "6",
    "RA": "6",
    "SNOW": "7",
    "SHOWER": "8",
    "SH": "8",
    "TS": "9",
    "THUNDERSTORM": "9"
}

ci = {
    "CU": "1",
    "Cu": "2",
    "Cb": "3",
    "Sc": "4",
    "CU/SC": "8",
    "SC": "5",
    "ST": "6",
    "CB": "9",
    "CB/CU": "9",
    "CB/SC": "9",
    "CB/CU/SC": "9",
    "CB/SC/CU": "9"
}

cm = {
    "AS": "1",
    "As": "2",
    "AC": "3",
    "Ac": "4",
    "AC/AS": "7",
    "AS/AC": "7"
}

ch = {
    "CI": "1",
    "Ci": "2",
    "CS": "7",
    "Cs": "8",
    "CC": "9"
}

awan_lapisan = {
    "CI": "- cirrus (Ci)",
    "CC": "- cirrocumulus (Cc)",
    "CS": "- cirrostratus (Cs)",
    "AC": "- altocumulus (Ac)",
    "AS": "- altostratus (As)",
    "NS": "- nimbostratus (Ns)",
    "SC": "- stratocumulus (Sc)",
    "ST": "- stratus (St)",
    "CU": "- cumulus (Cu)",
    "CB": "- cumulonimbus (Cb)",
    "/": "/ - cloud not visible"
}

elevasi = {
    0: 0,
    45: 1,
    30: 2,
    20: 3,
    15: 4,
    12: 5,
    9: 6,
    7: 7,
    6: 8,
    5: 9
}
