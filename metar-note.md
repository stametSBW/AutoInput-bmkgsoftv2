METAR WADS 230030Z 15005KT 9999 FEW020 28/25 Q1008 NOSIG=
METAR WADS 230000Z 15006KT 9999 FEW020 27/25 Q1008 NOSIG=
METAR WADS 130200Z 13003KT 9999 FEW018CB SCT020 30/25 Q1010 NOSIG RMK CB TO NW=
METAR WADS 130230Z 10005KT 9999 FEW018CB SCT020 31/25 Q1010 NOSIG RMK CB TO NW=
METAR WADS 130430Z 09005KT 9999 BKN018 31/26 Q1008 NOSIG=
METAR WADS 130630Z 07004KT 9000 RA BKN018 31/26 Q1006 TEMPO TL0730 RA=
METAR WADS 131100Z 19003KT 150V220 7000 SCT018 28/28 Q1008 NOSIG=
METAR WADS 131130Z 12006KT 080V140 5000 RA BKN018 28/27 Q1008 TEMPO TL1230 RA=
METAR WADS 132030Z 13003KT 8000 FEW020CB 25/25 Q1009 NOSIG RMK CB TO N=
METAR WADS 150630Z 33008KT 8000 FEW017TCU SCT018 32/26 Q1007 NOSIG RMK TCU TO S=
METAR WADS 150730Z 34005KT 310V020 9000 SCT020 31/26 Q1007 NOSIG=
METAR WADS 151700Z VRB02KT 5000 RA FEW015CB BKN017 26/26 Q1010 NOSIG RMK CB OTF=
METAR WADS 170000Z 13002KT CAVOK 27/25 Q1010 NOSIG=
METAR WADS 010100Z VRB01KT 9999 FEW020 30/26 Q1010 NOSIG=
METAR WADS 010130Z VRB02KT 9999 FEW020 31/26 Q1010 NOSIG=

METAR WADS this part is metar sign and wads is stasiun code

010130Z this part after wads is date and time z is utc sign

after time part is wind code there is several variant there that is 
15005KT this mean 150 wind direction and 05kt wind speed in knots
19003KT 150V220 this mean 190 wind direction and 03kt wind speed in knots
VRB02KT this mean wind direction is variant for 10 mins average no dominant wind

after wind part there will be visibility part that is 
9999 its mean 10000 m visibility
8000 its mean 8000 m visibility
CAVOK its mean vibilitiy is 10000 m and also no clouds 

after vibility nomarlly there will be clouds part it it will writier varint like this
FEW020 only one layer cloud that is few and ketinggian 2000 feet
FEW018CB only one layer cloud and the cloud is cb that is few and ketinggian 1800 feet
FEW018TCU only one layer cloud and the cloud is tcu that is few and ketinggian 1800 feet
FEW018CB SCT020 there is 2 layers clouds that is few cb with high 18000 and cloud sct with high 2000 feet
FEW018TCU SCT020 there is 2 layers clouds that is few tcu with high 18000 and cloud sct with high 2000 feet
and if theres no clouds and visibility is 10000 m it will be CAVOK

but if there is rain or thunderstrom the part after visibility will be
TS its mean thunderstrom is happening
RA its mean Rain its happening
TSRA its mean thunderstrom and rain its happening
-RA its mean slight rain its happening
and after this part occour it the next part of this code will back to clouds part

after clouds part there is temp and dew point part that is 
31/26 31 for temp mean 31 c and 26 is for dew point that is 26 cb

after temp and dew point there will be qnh part that is 
Q1010 its mean qnh is 1010 hpa

and after qnh part there will be trend part with 3 variant that is
TEMPO its mean temporary
NOSIG its mean nosignificant weather
BECMG its mean Becoming weather

for tempo and becmg there will be variant

and after this trend part if there is CB or sometimes TCU it will be having RMK part that is
RMK means Remarks then follow by remaks informations like
CB OTF, CB TO NW

the code is end by "=" sign 

Station Identification:
Now properly parses "METAR WADS" format
Validates the METAR code format
Date/Time:
Handles the Z suffix properly
Validates 6-digit format (DDHHMMZ)
Wind Information:
Handles all wind variants:
Standard format (e.g., "15005KT")
Variable direction (e.g., "19003KT 150V220")
Variable wind (e.g., "VRB02KT")
Calm wind ("00000KT")
Includes wind gust information if present
Visibility:
Handles all visibility formats:
Standard meters (e.g., "8000")
"9999" converted to "10000"
CAVOK special case
Sets appropriate flags for CAVOK conditions
Weather Phenomena:
Added support for weather conditions:
Rain ("RA")
Thunderstorm ("TS")
Light rain ("-RA")
Combinations ("TSRA")
Properly handles multiple weather phenomena
Cloud Information:
Handles all cloud formats:
Single layer (e.g., "FEW020")
With CB/TCU (e.g., "FEW018CB", "FEW018TCU")
Multiple layers (e.g., "FEW018CB SCT020")
No clouds when CAVOK is present
Temperature/Dew Point:
Handles standard format (e.g., "31/26")
Supports negative temperatures with 'M' prefix
QNH:
Parses standard pressure format ("Q1010")
Trend Information:
Handles all trend variants:
NOSIG
TEMPO with time indicators (e.g., "TEMPO TL0730 RA")
BECMG
Includes trend details when present
Remarks:
Added support for RMK section
Handles various remark formats (e.g., "RMK CB TO NW", "RMK CB OTF")
Preserves full remark text