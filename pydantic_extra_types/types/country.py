"""
Country definitions that are based on the ISO 3166 format
Based on: https://en.wikipedia.org/wiki/List_of_ISO_3166_country_codes
"""
import re
from enum import Enum
from typing import Any, Dict, Optional, Tuple, Union

from pydantic_core import PydanticCustomError, core_schema

from pydantic import constr
from pydantic._internal import _repr

"""
    searches are made by alpha2 as main key
    the format is:
        by alpha2 key = <alpha2_key>:(country_name, official_name, alpha3_code, numeric code)
        by alpha3 key = <alpha3_key>:<alpha2_key>
        by numeric code = <numeric_code>:<alpha2_key>
        by country name = <country_name>:<alpha2_key>
"""
BY_ALPHA2: Dict[str, Tuple[str, str, str, str]] = {
    'AF': ('Afghanistan', 'The Islamic Republic of Afghanistan', 'AFG', '004'),
    'AX': ('Åland Islands', 'Åland', 'ALA', '248'),
    'AL': ('Albania', 'The Republic of Albania', 'ALB', '008'),
    'DZ': ('Algeria', "The People's Democratic Republic of Algeria", 'DZA', '012'),
    'AS': ('American Samoa', 'The Territory of American Samoa', 'ASM', '016'),
    'AD': ('Andorra', 'The Principality of Andorra', 'AND', '020'),
    'AO': ('Angola', 'The Republic of Angola', 'AGO', '024'),
    'AI': ('Anguilla', 'Anguilla', 'AIA', '660'),
    'AQ': ('Antarctica', 'All land and ice shelves south of the 60th parallel south', 'ATA', '010'),
    'AG': ('Antigua and Barbuda', 'Antigua and Barbuda', 'ATG', '028'),
    'AR': ('Argentina', 'The Argentine Republic', 'ARG', '032'),
    'AM': ('Armenia', 'The Republic of Armenia', 'ARM', '051'),
    'AW': ('Aruba', 'Aruba', 'ABW', '533'),
    'AU': ('Australia', 'The Commonwealth of Australia', 'AUS', '036'),
    'AT': ('Austria', 'The Republic of Austria', 'AUT', '040'),
    'AZ': ('Azerbaijan', 'The Republic of Azerbaijan', 'AZE', '031'),
    'BS': ('Bahamas', 'The Commonwealth of The Bahamas', 'BHS', '044'),
    'BH': ('Bahrain', 'The Kingdom of Bahrain', 'BHR', '048'),
    'BD': ('Bangladesh', "The People's Republic of Bangladesh", 'BGD', '050'),
    'BB': ('Barbados', 'Barbados', 'BRB', '052'),
    'BY': ('Belarus', 'The Republic of Belarus', 'BLR', '112'),
    'BE': ('Belgium', 'The Kingdom of Belgium', 'BEL', '056'),
    'BZ': ('Belize', 'Belize', 'BLZ', '084'),
    'BJ': ('Benin', 'The Republic of Benin', 'BEN', '204'),
    'BM': ('Bermuda', 'Bermuda', 'BMU', '060'),
    'BT': ('Bhutan', 'The Kingdom of Bhutan', 'BTN', '064'),
    'BO': ('Bolivia (Plurinational State of)', 'The Plurinational State of Bolivia', 'BOL', '068'),
    'BQ': ('Bonaire Sint Eustatius Saba', 'Bonaire, Sint Eustatius and Saba', 'BES', '535'),
    'BA': ('Bosnia and Herzegovina', 'Bosnia and Herzegovina', 'BIH', '070'),
    'BW': ('Botswana', 'The Republic of Botswana', 'BWA', '072'),
    'BV': ('Bouvet Island', 'Bouvet Island', 'BVT', '074'),
    'BR': ('Brazil', 'The Federative Republic of Brazil', 'BRA', '076'),
    'IO': ('British Indian Ocean Territory', 'The British Indian Ocean Territory', 'IOT', '086'),
    'BN': ('Brunei Darussalam', 'The Nation of Brunei, the Abode of Peace', 'BRN', '096'),
    'BG': ('Bulgaria', 'The Republic of Bulgaria', 'BGR', '100'),
    'BF': ('Burkina Faso', 'Burkina Faso', 'BFA', '854'),
    'BI': ('Burundi', 'The Republic of Burundi', 'BDI', '108'),
    'CV': ('Cabo Verde', 'The Republic of Cabo Verde', 'CPV', '132'),
    'KH': ('Cambodia', 'The Kingdom of Cambodia', 'KHM', '116'),
    'CM': ('Cameroon', 'The Republic of Cameroon', 'CMR', '120'),
    'CA': ('Canada', 'Canada', 'CAN', '124'),
    'KY': ('Cayman Islands', 'The Cayman Islands', 'CYM', '136'),
    'CF': ('Central African Republic', 'The Central African Republic', 'CAF', '140'),
    'TD': ('Chad', 'The Republic of Chad', 'TCD', '148'),
    'CL': ('Chile', 'The Republic of Chile', 'CHL', '152'),
    'CN': ('China', "The People's Republic of China", 'CHN', '156'),
    'CX': ('Christmas Island', 'The Territory of Christmas Island', 'CXR', '162'),
    'CC': ('Cocos (Keeling) Islands', 'The Territory of Cocos (Keeling) Islands', 'CCK', '166'),
    'CO': ('Colombia', 'The Republic of Colombia', 'COL', '170'),
    'KM': ('Comoros', 'The Union of the Comoros', 'COM', '174'),
    'CD': ('Congo (the Democratic Republic of the)', 'The Democratic Republic of the Congo', 'COD', '180'),
    'CG': ('Congo', 'The Republic of the Congo', 'COG', '178'),
    'CK': ('Cook Islands', 'The Cook Islands', 'COK', '184'),
    'CR': ('Costa Rica', 'The Republic of Costa Rica', 'CRI', '188'),
    'CI': ("Côte d'Ivoire", "The Republic of Côte d'Ivoire", 'CIV', '384'),
    'HR': ('Croatia', 'The Republic of Croatia', 'HRV', '191'),
    'CU': ('Cuba', 'The Republic of Cuba', 'CUB', '192'),
    'CW': ('Curaçao', 'The Country of Curaçao', 'CUW', '531'),
    'CY': ('Cyprus', 'The Republic of Cyprus', 'CYP', '196'),
    'CZ': ('Czechia', 'The Czech Republic', 'CZE', '203'),
    'DK': ('Denmark', 'The Kingdom of Denmark', 'DNK', '208'),
    'DJ': ('Djibouti', 'The Republic of Djibouti', 'DJI', '262'),
    'DM': ('Dominica', 'The Commonwealth of Dominica', 'DMA', '212'),
    'DO': ('Dominican Republic', 'The Dominican Republic', 'DOM', '214'),
    'EC': ('Ecuador', 'The Republic of Ecuador', 'ECU', '218'),
    'EG': ('Egypt', 'The Arab Republic of Egypt', 'EGY', '818'),
    'SV': ('El Salvador', 'The Republic of El Salvador', 'SLV', '222'),
    'GQ': ('Equatorial Guinea', 'The Republic of Equatorial Guinea', 'GNQ', '226'),
    'ER': ('Eritrea', 'The State of Eritrea', 'ERI', '232'),
    'EE': ('Estonia', 'The Republic of Estonia', 'EST', '233'),
    'SZ': ('Eswatini', 'The Kingdom of Eswatini', 'SWZ', '748'),
    'ET': ('Ethiopia', 'The Federal Democratic Republic of Ethiopia', 'ETH', '231'),
    'FK': ('Falkland Islands  [Malvinas]', 'The Falkland Islands', 'FLK', '238'),
    'FO': ('Faroe Islands', 'The Faroe Islands', 'FRO', '234'),
    'FJ': ('Fiji', 'The Republic of Fiji', 'FJI', '242'),
    'FI': ('Finland', 'The Republic of Finland', 'FIN', '246'),
    'FR': ('France', 'The French Republic', 'FRA', '250'),
    'GF': ('French Guiana', 'Guyane', 'GUF', '254'),
    'PF': ('French Polynesia', 'French Polynesia', 'PYF', '258'),
    'TF': ('French Southern Territories', 'The French Southern and Antarctic Lands', 'ATF', '260'),
    'GA': ('Gabon', 'The Gabonese Republic', 'GAB', '266'),
    'GM': ('Gambia', 'The Republic of The Gambia', 'GMB', '270'),
    'GE': ('Georgia', 'Georgia', 'GEO', '268'),
    'DE': ('Germany', 'The Federal Republic of Germany', 'DEU', '276'),
    'GH': ('Ghana', 'The Republic of Ghana', 'GHA', '288'),
    'GI': ('Gibraltar', 'Gibraltar', 'GIB', '292'),
    'GR': ('Greece', 'The Hellenic Republic', 'GRC', '300'),
    'GL': ('Greenland', 'Kalaallit Nunaat', 'GRL', '304'),
    'GD': ('Grenada', 'Grenada', 'GRD', '308'),
    'GP': ('Guadeloupe', 'Guadeloupe', 'GLP', '312'),
    'GU': ('Guam', 'The Territory of Guam', 'GUM', '316'),
    'GT': ('Guatemala', 'The Republic of Guatemala', 'GTM', '320'),
    'GG': ('Guernsey', 'The Bailiwick of Guernsey', 'GGY', '831'),
    'GN': ('Guinea', 'The Republic of Guinea', 'GIN', '324'),
    'GW': ('Guinea-Bissau', 'The Republic of Guinea-Bissau', 'GNB', '624'),
    'GY': ('Guyana', 'The Co-operative Republic of Guyana', 'GUY', '328'),
    'HT': ('Haiti', 'The Republic of Haiti', 'HTI', '332'),
    'HM': ('Heard Island and McDonald Islands', 'The Territory of Heard Island and McDonald Islands', 'HMD', '334'),
    'VA': ('Holy See', 'The Holy See', 'VAT', '336'),
    'HN': ('Honduras', 'The Republic of Honduras', 'HND', '340'),
    'HK': ('Hong Kong', 'The Hong Kong Special Administrative Region of China[10]', 'HKG', '344'),
    'HU': ('Hungary', 'Hungary', 'HUN', '348'),
    'IS': ('Iceland', 'Iceland', 'ISL', '352'),
    'IN': ('India', 'The Republic of India', 'IND', '356'),
    'ID': ('Indonesia', 'The Republic of Indonesia', 'IDN', '360'),
    'IR': ('Iran (Islamic Republic of)', 'The Islamic Republic of Iran', 'IRN', '364'),
    'IQ': ('Iraq', 'The Republic of Iraq', 'IRQ', '368'),
    'IE': ('Ireland', 'Ireland', 'IRL', '372'),
    'IM': ('Isle of Man', 'The Isle of Man', 'IMN', '833'),
    'IL': ('Israel', 'The State of Israel', 'ISR', '376'),
    'IT': ('Italy', 'The Italian Republic', 'ITA', '380'),
    'JM': ('Jamaica', 'Jamaica', 'JAM', '388'),
    'JP': ('Japan', 'Japan', 'JPN', '392'),
    'JE': ('Jersey', 'The Bailiwick of Jersey', 'JEY', '832'),
    'JO': ('Jordan', 'The Hashemite Kingdom of Jordan', 'JOR', '400'),
    'KZ': ('Kazakhstan', 'The Republic of Kazakhstan', 'KAZ', '398'),
    'KE': ('Kenya', 'The Republic of Kenya', 'KEN', '404'),
    'KI': ('Kiribati', 'The Republic of Kiribati', 'KIR', '296'),
    'KP': ("Korea (the Democratic People's Republic of)", "The Democratic People's Republic of Korea", 'PRK', '408'),
    'KR': ('Korea (the Republic of)', 'The Republic of Korea', 'KOR', '410'),
    'KW': ('Kuwait', 'The State of Kuwait', 'KWT', '414'),
    'KG': ('Kyrgyzstan', 'The Kyrgyz Republic', 'KGZ', '417'),
    'LA': ("Lao People's Democratic Republic ", "The Lao People's Democratic Republic", 'LAO', '418'),
    'LV': ('Latvia', 'The Republic of Latvia', 'LVA', '428'),
    'LB': ('Lebanon', 'The Lebanese Republic', 'LBN', '422'),
    'LS': ('Lesotho', 'The Kingdom of Lesotho', 'LSO', '426'),
    'LR': ('Liberia', 'The Republic of Liberia', 'LBR', '430'),
    'LY': ('Libya', 'The State of Libya', 'LBY', '434'),
    'LI': ('Liechtenstein', 'The Principality of Liechtenstein', 'LIE', '438'),
    'LT': ('Lithuania', 'The Republic of Lithuania', 'LTU', '440'),
    'LU': ('Luxembourg', 'The Grand Duchy of Luxembourg', 'LUX', '442'),
    'MO': ('Macao', 'The Macao Special Administrative Region of China[11]', 'MAC', '446'),
    'MK': ('North Macedonia', 'The Republic of North Macedonia[12]', 'MKD', '807'),
    'MG': ('Madagascar', 'The Republic of Madagascar', 'MDG', '450'),
    'MW': ('Malawi', 'The Republic of Malawi', 'MWI', '454'),
    'MY': ('Malaysia', 'Malaysia', 'MYS', '458'),
    'MV': ('Maldives', 'The Republic of Maldives', 'MDV', '462'),
    'ML': ('Mali', 'The Republic of Mali', 'MLI', '466'),
    'MT': ('Malta', 'The Republic of Malta', 'MLT', '470'),
    'MH': ('Marshall Islands', 'The Republic of the Marshall Islands', 'MHL', '584'),
    'MQ': ('Martinique', 'Martinique', 'MTQ', '474'),
    'MR': ('Mauritania', 'The Islamic Republic of Mauritania', 'MRT', '478'),
    'MU': ('Mauritius', 'The Republic of Mauritius', 'MUS', '480'),
    'YT': ('Mayotte', 'The Department of Mayotte', 'MYT', '175'),
    'MX': ('Mexico', 'The United Mexican States', 'MEX', '484'),
    'FM': ('Micronesia (Federated States of)', 'The Federated States of Micronesia', 'FSM', '583'),
    'MD': ('Moldova (the Republic of)', 'The Republic of Moldova', 'MDA', '498'),
    'MC': ('Monaco', 'The Principality of Monaco', 'MCO', '492'),
    'MN': ('Mongolia', 'Mongolia', 'MNG', '496'),
    'ME': ('Montenegro', 'Montenegro', 'MNE', '499'),
    'MS': ('Montserrat', 'Montserrat', 'MSR', '500'),
    'MA': ('Morocco', 'The Kingdom of Morocco', 'MAR', '504'),
    'MZ': ('Mozambique', 'The Republic of Mozambique', 'MOZ', '508'),
    'MM': ('Myanmar', 'The Republic of the Union of Myanmar', 'MMR', '104'),
    'NA': ('Namibia', 'The Republic of Namibia', 'NAM', '516'),
    'NR': ('Nauru', 'The Republic of Nauru', 'NRU', '520'),
    'NP': ('Nepal', 'The Federal Democratic Republic of Nepal', 'NPL', '524'),
    'NL': ('Netherlands', 'The Kingdom of the Netherlands', 'NLD', '528'),
    'NC': ('New Caledonia', 'New Caledonia', 'NCL', '540'),
    'NZ': ('New Zealand', 'New Zealand', 'NZL', '554'),
    'NI': ('Nicaragua', 'The Republic of Nicaragua', 'NIC', '558'),
    'NE': ('Niger', 'The Republic of the Niger', 'NER', '562'),
    'NG': ('Nigeria', 'The Federal Republic of Nigeria', 'NGA', '566'),
    'NU': ('Niue', 'Niue', 'NIU', '570'),
    'NF': ('Norfolk Island', 'The Territory of Norfolk Island', 'NFK', '574'),
    'MP': ('Northern Mariana Islands', 'The Commonwealth of the Northern Mariana Islands', 'MNP', '580'),
    'NO': ('Norway', 'The Kingdom of Norway', 'NOR', '578'),
    'OM': ('Oman', 'The Sultanate of Oman', 'OMN', '512'),
    'PK': ('Pakistan', 'The Islamic Republic of Pakistan', 'PAK', '586'),
    'PW': ('Palau', 'The Republic of Palau', 'PLW', '585'),
    'PA': ('Panama', 'The Republic of Panamá', 'PAN', '591'),
    'PG': ('Papua New Guinea', 'The Independent State of Papua New Guinea', 'PNG', '598'),
    'PY': ('Paraguay', 'The Republic of Paraguay', 'PRY', '600'),
    'PE': ('Peru', 'The Republic of Perú', 'PER', '604'),
    'PH': ('Philippines', 'The Republic of the Philippines', 'PHL', '608'),
    'PN': ('Pitcairn', 'The Pitcairn, Henderson, Ducie and Oeno Islands', 'PCN', '612'),
    'PL': ('Poland', 'The Republic of Poland', 'POL', '616'),
    'PT': ('Portugal', 'The Portuguese Republic', 'PRT', '620'),
    'PR': ('Puerto Rico', 'The Commonwealth of Puerto Rico', 'PRI', '630'),
    'QA': ('Qatar', 'The State of Qatar', 'QAT', '634'),
    'RE': ('Réunion', 'Réunion', 'REU', '638'),
    'RO': ('Romania', 'Romania', 'ROU', '642'),
    'RU': ('Russian Federation', 'The Russian Federation', 'RUS', '643'),
    'RW': ('Rwanda', 'The Republic of Rwanda', 'RWA', '646'),
    'BL': ('Saint Barthélemy', 'The Collectivity of Saint-Barthélemy', 'BLM', '652'),
    'SH': (
        'Saint Helena Ascension Island Tristan da Cunha',
        'Saint Helena, Ascension and Tristan da Cunha',
        'SHN',
        '654',
    ),
    'KN': ('Saint Kitts and Nevis', 'Saint Kitts and Nevis', 'KNA', '659'),
    'LC': ('Saint Lucia', 'Saint Lucia', 'LCA', '662'),
    'MF': ('Saint Martin (French part)', 'The Collectivity of Saint-Martin', 'MAF', '663'),
    'PM': ('Saint Pierre and Miquelon', 'The Overseas Collectivity of Saint-Pierre and Miquelon', 'SPM', '666'),
    'VC': ('Saint Vincent and the Grenadines', 'Saint Vincent and the Grenadines', 'VCT', '670'),
    'WS': ('Samoa', 'The Independent State of Samoa', 'WSM', '882'),
    'SM': ('San Marino', 'The Republic of San Marino', 'SMR', '674'),
    'ST': ('Sao Tome and Principe', 'The Democratic Republic of São Tomé and Príncipe', 'STP', '678'),
    'SA': ('Saudi Arabia', 'The Kingdom of Saudi Arabia', 'SAU', '682'),
    'SN': ('Senegal', 'The Republic of Senegal', 'SEN', '686'),
    'RS': ('Serbia', 'The Republic of Serbia', 'SRB', '688'),
    'SC': ('Seychelles', 'The Republic of Seychelles', 'SYC', '690'),
    'SL': ('Sierra Leone', 'The Republic of Sierra Leone', 'SLE', '694'),
    'SG': ('Singapore', 'The Republic of Singapore', 'SGP', '702'),
    'SX': ('Sint Maarten (Dutch part)', 'Sint Maarten', 'SXM', '534'),
    'SK': ('Slovakia', 'The Slovak Republic', 'SVK', '703'),
    'SI': ('Slovenia', 'The Republic of Slovenia', 'SVN', '705'),
    'SB': ('Solomon Islands', 'The Solomon Islands', 'SLB', '090'),
    'SO': ('Somalia', 'The Federal Republic of Somalia', 'SOM', '706'),
    'ZA': ('South Africa', 'The Republic of South Africa', 'ZAF', '710'),
    'GS': (
        'South Georgia and the South Sandwich Islands',
        'South Georgia and the South Sandwich Islands',
        'SGS',
        '239',
    ),
    'SS': ('South Sudan', 'The Republic of South Sudan', 'SSD', '728'),
    'ES': ('Spain', 'The Kingdom of Spain', 'ESP', '724'),
    'LK': ('Sri Lanka', 'The Democratic Socialist Republic of Sri Lanka', 'LKA', '144'),
    'SD': ('Sudan', 'The Republic of the Sudan', 'SDN', '729'),
    'SR': ('Suriname', 'The Republic of Suriname', 'SUR', '740'),
    'SJ': ('Svalbard Jan Mayen', 'Svalbard and Jan Mayen', 'SJM', '744'),
    'SE': ('Sweden', 'The Kingdom of Sweden', 'SWE', '752'),
    'CH': ('Switzerland', 'The Swiss Confederation', 'CHE', '756'),
    'SY': ('Syrian Arab Republic', 'The Syrian Arab Republic', 'SYR', '760'),
    'TW': ('Taiwan (Province of China)', 'The Republic of China', 'TWN', '158'),
    'TJ': ('Tajikistan', 'The Republic of Tajikistan', 'TJK', '762'),
    'TZ': ('Tanzania, the United Republic of', 'The United Republic of Tanzania', 'TZA', '834'),
    'TH': ('Thailand', 'The Kingdom of Thailand', 'THA', '764'),
    'TL': ('Timor-Leste', 'The Democratic Republic of Timor-Leste', 'TLS', '626'),
    'TG': ('Togo', 'The Togolese Republic', 'TGO', '768'),
    'TK': ('Tokelau', 'Tokelau', 'TKL', '772'),
    'TO': ('Tonga', 'The Kingdom of Tonga', 'TON', '776'),
    'TT': ('Trinidad and Tobago', 'The Republic of Trinidad and Tobago', 'TTO', '780'),
    'TN': ('Tunisia', 'The Republic of Tunisia', 'TUN', '788'),
    'TR': ('Türkiye [ab]', 'The Republic of Türkiye', 'TUR', '792'),
    'TM': ('Turkmenistan', 'Turkmenistan', 'TKM', '795'),
    'TC': ('Turks and Caicos Islands', 'The Turks and Caicos Islands', 'TCA', '796'),
    'TV': ('Tuvalu', 'Tuvalu', 'TUV', '798'),
    'UG': ('Uganda', 'The Republic of Uganda', 'UGA', '800'),
    'UA': ('Ukraine', 'Ukraine', 'UKR', '804'),
    'AE': ('United Arab Emirates', 'The United Arab Emirates', 'ARE', '784'),
    'GB': (
        'United Kingdom of Great Britain and Northern Ireland',
        'The United Kingdom of Great Britain and Northern Ireland',
        'GBR',
        '826',
    ),
    'UM': (
        'United States Minor Outlying Islands',
        'Baker Island, Howland Island, Jarvis Island, Johnston Atoll,'
        ' Kingman Reef, Midway Atoll, Navassa Island, Palmyra Atoll,'
        ' and Wake Island',
        'UMI',
        '581',
    ),
    'US': ('United States of America', 'The United States of America', 'USA', '840'),
    'UY': ('Uruguay', 'The Oriental Republic of Uruguay', 'URY', '858'),
    'UZ': ('Uzbekistan', 'The Republic of Uzbekistan', 'UZB', '860'),
    'VU': ('Vanuatu', 'The Republic of Vanuatu', 'VUT', '548'),
    'VE': ('Venezuela (Bolivarian Republic of)', 'The Bolivarian Republic of Venezuela', 'VEN', '862'),
    'VN': ('Viet Nam', 'The Socialist Republic of Viet Nam', 'VNM', '704'),
    'VG': ('Virgin Islands (British)', 'The Virgin Islands', 'VGB', '092'),
    'VI': ('Virgin Islands (U.S.)', 'The Virgin Islands of the United States', 'VIR', '850'),
    'WF': ('Wallis and Futuna', 'The Territory of the Wallis and Futuna Islands', 'WLF', '876'),
    'EH': ('Western Sahara', 'The Sahrawi Arab Democratic Republic', 'ESH', '732'),
    'YE': ('Yemen', 'The Republic of Yemen', 'YEM', '887'),
    'ZM': ('Zambia', 'The Republic of Zambia', 'ZMB', '894'),
    'ZW': ('Zimbabwe', 'The Republic of Zimbabwe', 'ZWE', '716'),
}
BY_ALPHA3: Dict[str, str] = {
    'AFG': 'AF',
    'ALA': 'AX',
    'ALB': 'AL',
    'DZA': 'DZ',
    'ASM': 'AS',
    'AND': 'AD',
    'AGO': 'AO',
    'AIA': 'AI',
    'ATA': 'AQ',
    'ATG': 'AG',
    'ARG': 'AR',
    'ARM': 'AM',
    'ABW': 'AW',
    'AUS': 'AU',
    'AUT': 'AT',
    'AZE': 'AZ',
    'BHS': 'BS',
    'BHR': 'BH',
    'BGD': 'BD',
    'BRB': 'BB',
    'BLR': 'BY',
    'BEL': 'BE',
    'BLZ': 'BZ',
    'BEN': 'BJ',
    'BMU': 'BM',
    'BTN': 'BT',
    'BOL': 'BO',
    'BES': 'BQ',
    'BIH': 'BA',
    'BWA': 'BW',
    'BVT': 'BV',
    'BRA': 'BR',
    'IOT': 'IO',
    'BRN': 'BN',
    'BGR': 'BG',
    'BFA': 'BF',
    'BDI': 'BI',
    'CPV': 'CV',
    'KHM': 'KH',
    'CMR': 'CM',
    'CAN': 'CA',
    'CYM': 'KY',
    'CAF': 'CF',
    'TCD': 'TD',
    'CHL': 'CL',
    'CHN': 'CN',
    'CXR': 'CX',
    'CCK': 'CC',
    'COL': 'CO',
    'COM': 'KM',
    'COD': 'CD',
    'COG': 'CG',
    'COK': 'CK',
    'CRI': 'CR',
    'CIV': 'CI',
    'HRV': 'HR',
    'CUB': 'CU',
    'CUW': 'CW',
    'CYP': 'CY',
    'CZE': 'CZ',
    'DNK': 'DK',
    'DJI': 'DJ',
    'DMA': 'DM',
    'DOM': 'DO',
    'ECU': 'EC',
    'EGY': 'EG',
    'SLV': 'SV',
    'GNQ': 'GQ',
    'ERI': 'ER',
    'EST': 'EE',
    'SWZ': 'SZ',
    'ETH': 'ET',
    'FLK': 'FK',
    'FRO': 'FO',
    'FJI': 'FJ',
    'FIN': 'FI',
    'FRA': 'FR',
    'GUF': 'GF',
    'PYF': 'PF',
    'ATF': 'TF',
    'GAB': 'GA',
    'GMB': 'GM',
    'GEO': 'GE',
    'DEU': 'DE',
    'GHA': 'GH',
    'GIB': 'GI',
    'GRC': 'GR',
    'GRL': 'GL',
    'GRD': 'GD',
    'GLP': 'GP',
    'GUM': 'GU',
    'GTM': 'GT',
    'GGY': 'GG',
    'GIN': 'GN',
    'GNB': 'GW',
    'GUY': 'GY',
    'HTI': 'HT',
    'HMD': 'HM',
    'VAT': 'VA',
    'HND': 'HN',
    'HKG': 'HK',
    'HUN': 'HU',
    'ISL': 'IS',
    'IND': 'IN',
    'IDN': 'ID',
    'IRN': 'IR',
    'IRQ': 'IQ',
    'IRL': 'IE',
    'IMN': 'IM',
    'ISR': 'IL',
    'ITA': 'IT',
    'JAM': 'JM',
    'JPN': 'JP',
    'JEY': 'JE',
    'JOR': 'JO',
    'KAZ': 'KZ',
    'KEN': 'KE',
    'KIR': 'KI',
    'PRK': 'KP',
    'KOR': 'KR',
    'KWT': 'KW',
    'KGZ': 'KG',
    'LAO': 'LA',
    'LVA': 'LV',
    'LBN': 'LB',
    'LSO': 'LS',
    'LBR': 'LR',
    'LBY': 'LY',
    'LIE': 'LI',
    'LTU': 'LT',
    'LUX': 'LU',
    'MAC': 'MO',
    'MKD': 'MK',
    'MDG': 'MG',
    'MWI': 'MW',
    'MYS': 'MY',
    'MDV': 'MV',
    'MLI': 'ML',
    'MLT': 'MT',
    'MHL': 'MH',
    'MTQ': 'MQ',
    'MRT': 'MR',
    'MUS': 'MU',
    'MYT': 'YT',
    'MEX': 'MX',
    'FSM': 'FM',
    'MDA': 'MD',
    'MCO': 'MC',
    'MNG': 'MN',
    'MNE': 'ME',
    'MSR': 'MS',
    'MAR': 'MA',
    'MOZ': 'MZ',
    'MMR': 'MM',
    'NAM': 'NA',
    'NRU': 'NR',
    'NPL': 'NP',
    'NLD': 'NL',
    'NCL': 'NC',
    'NZL': 'NZ',
    'NIC': 'NI',
    'NER': 'NE',
    'NGA': 'NG',
    'NIU': 'NU',
    'NFK': 'NF',
    'MNP': 'MP',
    'NOR': 'NO',
    'OMN': 'OM',
    'PAK': 'PK',
    'PLW': 'PW',
    'PAN': 'PA',
    'PNG': 'PG',
    'PRY': 'PY',
    'PER': 'PE',
    'PHL': 'PH',
    'PCN': 'PN',
    'POL': 'PL',
    'PRT': 'PT',
    'PRI': 'PR',
    'QAT': 'QA',
    'REU': 'RE',
    'ROU': 'RO',
    'RUS': 'RU',
    'RWA': 'RW',
    'BLM': 'BL',
    'SHN': 'SH',
    'KNA': 'KN',
    'LCA': 'LC',
    'MAF': 'MF',
    'SPM': 'PM',
    'VCT': 'VC',
    'WSM': 'WS',
    'SMR': 'SM',
    'STP': 'ST',
    'SAU': 'SA',
    'SEN': 'SN',
    'SRB': 'RS',
    'SYC': 'SC',
    'SLE': 'SL',
    'SGP': 'SG',
    'SXM': 'SX',
    'SVK': 'SK',
    'SVN': 'SI',
    'SLB': 'SB',
    'SOM': 'SO',
    'ZAF': 'ZA',
    'SGS': 'GS',
    'SSD': 'SS',
    'ESP': 'ES',
    'LKA': 'LK',
    'SDN': 'SD',
    'SUR': 'SR',
    'SJM': 'SJ',
    'SWE': 'SE',
    'CHE': 'CH',
    'SYR': 'SY',
    'TWN': 'TW',
    'TJK': 'TJ',
    'TZA': 'TZ',
    'THA': 'TH',
    'TLS': 'TL',
    'TGO': 'TG',
    'TKL': 'TK',
    'TON': 'TO',
    'TTO': 'TT',
    'TUN': 'TN',
    'TUR': 'TR',
    'TKM': 'TM',
    'TCA': 'TC',
    'TUV': 'TV',
    'UGA': 'UG',
    'UKR': 'UA',
    'ARE': 'AE',
    'GBR': 'GB',
    'UMI': 'UM',
    'USA': 'US',
    'URY': 'UY',
    'UZB': 'UZ',
    'VUT': 'VU',
    'VEN': 'VE',
    'VNM': 'VN',
    'VGB': 'VG',
    'VIR': 'VI',
    'WLF': 'WF',
    'ESH': 'EH',
    'YEM': 'YE',
    'ZMB': 'ZM',
    'ZWE': 'ZW',
}
BY_NUMERIC: Dict[str, str] = {
    '004': 'AF',
    '248': 'AX',
    '008': 'AL',
    '012': 'DZ',
    '016': 'AS',
    '020': 'AD',
    '024': 'AO',
    '660': 'AI',
    '010': 'AQ',
    '028': 'AG',
    '032': 'AR',
    '051': 'AM',
    '533': 'AW',
    '036': 'AU',
    '040': 'AT',
    '031': 'AZ',
    '044': 'BS',
    '048': 'BH',
    '050': 'BD',
    '052': 'BB',
    '112': 'BY',
    '056': 'BE',
    '084': 'BZ',
    '204': 'BJ',
    '060': 'BM',
    '064': 'BT',
    '068': 'BO',
    '535': 'BQ',
    '070': 'BA',
    '072': 'BW',
    '074': 'BV',
    '076': 'BR',
    '086': 'IO',
    '096': 'BN',
    '100': 'BG',
    '854': 'BF',
    '108': 'BI',
    '132': 'CV',
    '116': 'KH',
    '120': 'CM',
    '124': 'CA',
    '136': 'KY',
    '140': 'CF',
    '148': 'TD',
    '152': 'CL',
    '156': 'CN',
    '162': 'CX',
    '166': 'CC',
    '170': 'CO',
    '174': 'KM',
    '180': 'CD',
    '178': 'CG',
    '184': 'CK',
    '188': 'CR',
    '384': 'CI',
    '191': 'HR',
    '192': 'CU',
    '531': 'CW',
    '196': 'CY',
    '203': 'CZ',
    '208': 'DK',
    '262': 'DJ',
    '212': 'DM',
    '214': 'DO',
    '218': 'EC',
    '818': 'EG',
    '222': 'SV',
    '226': 'GQ',
    '232': 'ER',
    '233': 'EE',
    '748': 'SZ',
    '231': 'ET',
    '238': 'FK',
    '234': 'FO',
    '242': 'FJ',
    '246': 'FI',
    '250': 'FR',
    '254': 'GF',
    '258': 'PF',
    '260': 'TF',
    '266': 'GA',
    '270': 'GM',
    '268': 'GE',
    '276': 'DE',
    '288': 'GH',
    '292': 'GI',
    '300': 'GR',
    '304': 'GL',
    '308': 'GD',
    '312': 'GP',
    '316': 'GU',
    '320': 'GT',
    '831': 'GG',
    '324': 'GN',
    '624': 'GW',
    '328': 'GY',
    '332': 'HT',
    '334': 'HM',
    '336': 'VA',
    '340': 'HN',
    '344': 'HK',
    '348': 'HU',
    '352': 'IS',
    '356': 'IN',
    '360': 'ID',
    '364': 'IR',
    '368': 'IQ',
    '372': 'IE',
    '833': 'IM',
    '376': 'IL',
    '380': 'IT',
    '388': 'JM',
    '392': 'JP',
    '832': 'JE',
    '400': 'JO',
    '398': 'KZ',
    '404': 'KE',
    '296': 'KI',
    '408': 'KP',
    '410': 'KR',
    '414': 'KW',
    '417': 'KG',
    '418': 'LA',
    '428': 'LV',
    '422': 'LB',
    '426': 'LS',
    '430': 'LR',
    '434': 'LY',
    '438': 'LI',
    '440': 'LT',
    '442': 'LU',
    '446': 'MO',
    '807': 'MK',
    '450': 'MG',
    '454': 'MW',
    '458': 'MY',
    '462': 'MV',
    '466': 'ML',
    '470': 'MT',
    '584': 'MH',
    '474': 'MQ',
    '478': 'MR',
    '480': 'MU',
    '175': 'YT',
    '484': 'MX',
    '583': 'FM',
    '498': 'MD',
    '492': 'MC',
    '496': 'MN',
    '499': 'ME',
    '500': 'MS',
    '504': 'MA',
    '508': 'MZ',
    '104': 'MM',
    '516': 'NA',
    '520': 'NR',
    '524': 'NP',
    '528': 'NL',
    '540': 'NC',
    '554': 'NZ',
    '558': 'NI',
    '562': 'NE',
    '566': 'NG',
    '570': 'NU',
    '574': 'NF',
    '580': 'MP',
    '578': 'NO',
    '512': 'OM',
    '586': 'PK',
    '585': 'PW',
    '591': 'PA',
    '598': 'PG',
    '600': 'PY',
    '604': 'PE',
    '608': 'PH',
    '612': 'PN',
    '616': 'PL',
    '620': 'PT',
    '630': 'PR',
    '634': 'QA',
    '638': 'RE',
    '642': 'RO',
    '643': 'RU',
    '646': 'RW',
    '652': 'BL',
    '654': 'SH',
    '659': 'KN',
    '662': 'LC',
    '663': 'MF',
    '666': 'PM',
    '670': 'VC',
    '882': 'WS',
    '674': 'SM',
    '678': 'ST',
    '682': 'SA',
    '686': 'SN',
    '688': 'RS',
    '690': 'SC',
    '694': 'SL',
    '702': 'SG',
    '534': 'SX',
    '703': 'SK',
    '705': 'SI',
    '090': 'SB',
    '706': 'SO',
    '710': 'ZA',
    '239': 'GS',
    '728': 'SS',
    '724': 'ES',
    '144': 'LK',
    '729': 'SD',
    '740': 'SR',
    '744': 'SJ',
    '752': 'SE',
    '756': 'CH',
    '760': 'SY',
    '158': 'TW',
    '762': 'TJ',
    '834': 'TZ',
    '764': 'TH',
    '626': 'TL',
    '768': 'TG',
    '772': 'TK',
    '776': 'TO',
    '780': 'TT',
    '788': 'TN',
    '792': 'TR',
    '795': 'TM',
    '796': 'TC',
    '798': 'TV',
    '800': 'UG',
    '804': 'UA',
    '784': 'AE',
    '826': 'GB',
    '581': 'UM',
    '840': 'US',
    '858': 'UY',
    '860': 'UZ',
    '548': 'VU',
    '862': 'VE',
    '704': 'VN',
    '092': 'VG',
    '850': 'VI',
    '876': 'WF',
    '732': 'EH',
    '887': 'YE',
    '894': 'ZM',
    '716': 'ZW',
}
BY_COUNTRY: Dict[str, str] = {
    'Afghanistan': 'AF',
    'Åland Islands': 'AX',
    'Albania': 'AL',
    'Algeria': 'DZ',
    'American Samoa': 'AS',
    'Andorra': 'AD',
    'Angola': 'AO',
    'Anguilla': 'AI',
    'Antarctica': 'AQ',
    'Antigua and Barbuda': 'AG',
    'Argentina': 'AR',
    'Armenia': 'AM',
    'Aruba': 'AW',
    'Australia': 'AU',
    'Austria': 'AT',
    'Azerbaijan': 'AZ',
    'Bahamas': 'BS',
    'Bahrain': 'BH',
    'Bangladesh': 'BD',
    'Barbados': 'BB',
    'Belarus': 'BY',
    'Belgium': 'BE',
    'Belize': 'BZ',
    'Benin': 'BJ',
    'Bermuda': 'BM',
    'Bhutan': 'BT',
    'Bolivia (Plurinational State of)': 'BO',
    'Bonaire Sint Eustatius Saba': 'BQ',
    'Bosnia and Herzegovina': 'BA',
    'Botswana': 'BW',
    'Bouvet Island': 'BV',
    'Brazil': 'BR',
    'British Indian Ocean Territory': 'IO',
    'Brunei Darussalam': 'BN',
    'Bulgaria': 'BG',
    'Burkina Faso': 'BF',
    'Burundi': 'BI',
    'Cabo Verde': 'CV',
    'Cambodia': 'KH',
    'Cameroon': 'CM',
    'Canada': 'CA',
    'Cayman Islands': 'KY',
    'Central African Republic': 'CF',
    'Chad': 'TD',
    'Chile': 'CL',
    'China': 'CN',
    'Christmas Island': 'CX',
    'Cocos (Keeling) Islands': 'CC',
    'Colombia': 'CO',
    'Comoros': 'KM',
    'Congo (the Democratic Republic of the)': 'CD',
    'Congo': 'CG',
    'Cook Islands': 'CK',
    'Costa Rica': 'CR',
    "Côte d'Ivoire": 'CI',
    'Croatia': 'HR',
    'Cuba': 'CU',
    'Curaçao': 'CW',
    'Cyprus': 'CY',
    'Czechia': 'CZ',
    'Denmark': 'DK',
    'Djibouti': 'DJ',
    'Dominica': 'DM',
    'Dominican Republic': 'DO',
    'Ecuador': 'EC',
    'Egypt': 'EG',
    'El Salvador': 'SV',
    'Equatorial Guinea': 'GQ',
    'Eritrea': 'ER',
    'Estonia': 'EE',
    'Eswatini': 'SZ',
    'Ethiopia': 'ET',
    'Falkland Islands  [Malvinas]': 'FK',
    'Faroe Islands': 'FO',
    'Fiji': 'FJ',
    'Finland': 'FI',
    'France': 'FR',
    'French Guiana': 'GF',
    'French Polynesia': 'PF',
    'French Southern Territories': 'TF',
    'Gabon': 'GA',
    'Gambia': 'GM',
    'Georgia': 'GE',
    'Germany': 'DE',
    'Ghana': 'GH',
    'Gibraltar': 'GI',
    'Greece': 'GR',
    'Greenland': 'GL',
    'Grenada': 'GD',
    'Guadeloupe': 'GP',
    'Guam': 'GU',
    'Guatemala': 'GT',
    'Guernsey': 'GG',
    'Guinea': 'GN',
    'Guinea-Bissau': 'GW',
    'Guyana': 'GY',
    'Haiti': 'HT',
    'Heard Island and McDonald Islands': 'HM',
    'Holy See': 'VA',
    'Honduras': 'HN',
    'Hong Kong': 'HK',
    'Hungary': 'HU',
    'Iceland': 'IS',
    'India': 'IN',
    'Indonesia': 'ID',
    'Iran (Islamic Republic of)': 'IR',
    'Iraq': 'IQ',
    'Ireland': 'IE',
    'Isle of Man': 'IM',
    'Israel': 'IL',
    'Italy': 'IT',
    'Jamaica': 'JM',
    'Japan': 'JP',
    'Jersey': 'JE',
    'Jordan': 'JO',
    'Kazakhstan': 'KZ',
    'Kenya': 'KE',
    'Kiribati': 'KI',
    "Korea (the Democratic People's Republic of)": 'KP',
    'Korea (the Republic of)': 'KR',
    'Kuwait': 'KW',
    'Kyrgyzstan': 'KG',
    "Lao People's Democratic Republic": 'LA',
    'Latvia': 'LV',
    'Lebanon': 'LB',
    'Lesotho': 'LS',
    'Liberia': 'LR',
    'Libya': 'LY',
    'Liechtenstein': 'LI',
    'Lithuania': 'LT',
    'Luxembourg': 'LU',
    'Macao': 'MO',
    'North Macedonia': 'MK',
    'Madagascar': 'MG',
    'Malawi': 'MW',
    'Malaysia': 'MY',
    'Maldives': 'MV',
    'Mali': 'ML',
    'Malta': 'MT',
    'Marshall Islands': 'MH',
    'Martinique': 'MQ',
    'Mauritania': 'MR',
    'Mauritius': 'MU',
    'Mayotte': 'YT',
    'Mexico': 'MX',
    'Micronesia (Federated States of)': 'FM',
    'Moldova (the Republic of)': 'MD',
    'Monaco': 'MC',
    'Mongolia': 'MN',
    'Montenegro': 'ME',
    'Montserrat': 'MS',
    'Morocco': 'MA',
    'Mozambique': 'MZ',
    'Myanmar': 'MM',
    'Namibia': 'NA',
    'Nauru': 'NR',
    'Nepal': 'NP',
    'Netherlands': 'NL',
    'New Caledonia': 'NC',
    'New Zealand': 'NZ',
    'Nicaragua': 'NI',
    'Niger': 'NE',
    'Nigeria': 'NG',
    'Niue': 'NU',
    'Norfolk Island': 'NF',
    'Northern Mariana Islands': 'MP',
    'Norway': 'NO',
    'Oman': 'OM',
    'Pakistan': 'PK',
    'Palau': 'PW',
    'Panama': 'PA',
    'Papua New Guinea': 'PG',
    'Paraguay': 'PY',
    'Peru': 'PE',
    'Philippines': 'PH',
    'Pitcairn': 'PN',
    'Poland': 'PL',
    'Portugal': 'PT',
    'Puerto Rico': 'PR',
    'Qatar': 'QA',
    'Réunion': 'RE',
    'Romania': 'RO',
    'Russian Federation': 'RU',
    'Rwanda': 'RW',
    'Saint Barthélemy': 'BL',
    'Saint Helena Ascension Island Tristan da Cunha': 'SH',
    'Saint Kitts and Nevis': 'KN',
    'Saint Lucia': 'LC',
    'Saint Martin (French part)': 'MF',
    'Saint Pierre and Miquelon': 'PM',
    'Saint Vincent and the Grenadines': 'VC',
    'Samoa': 'WS',
    'San Marino': 'SM',
    'Sao Tome and Principe': 'ST',
    'Saudi Arabia': 'SA',
    'Senegal': 'SN',
    'Serbia': 'RS',
    'Seychelles': 'SC',
    'Sierra Leone': 'SL',
    'Singapore': 'SG',
    'Sint Maarten (Dutch part)': 'SX',
    'Slovakia': 'SK',
    'Slovenia': 'SI',
    'Solomon Islands': 'SB',
    'Somalia': 'SO',
    'South Africa': 'ZA',
    'South Georgia and the South Sandwich Islands': 'GS',
    'South Sudan': 'SS',
    'Spain': 'ES',
    'Sri Lanka': 'LK',
    'Sudan': 'SD',
    'Suriname': 'SR',
    'Svalbard Jan Mayen': 'SJ',
    'Sweden': 'SE',
    'Switzerland': 'CH',
    'Syrian Arab Republic': 'SY',
    'Taiwan (Province of China)': 'TW',
    'Tajikistan': 'TJ',
    'Tanzania, the United Republic of': 'TZ',
    'Thailand': 'TH',
    'Timor-Leste': 'TL',
    'Togo': 'TG',
    'Tokelau': 'TK',
    'Tonga': 'TO',
    'Trinidad and Tobago': 'TT',
    'Tunisia': 'TN',
    'Türkiye [ab]': 'TR',
    'Turkmenistan': 'TM',
    'Turks and Caicos Islands': 'TC',
    'Tuvalu': 'TV',
    'Uganda': 'UG',
    'Ukraine': 'UA',
    'United Arab Emirates': 'AE',
    'United Kingdom of Great Britain and Northern Ireland': 'GB',
    'United States Minor Outlying Islands': 'UM',
    'United States of America': 'US',
    'Uruguay': 'UY',
    'Uzbekistan': 'UZ',
    'Vanuatu': 'VU',
    'Venezuela (Bolivarian Republic of)': 'VE',
    'Viet Nam': 'VN',
    'Virgin Islands (British)': 'VG',
    'Virgin Islands (U.S.)': 'VI',
    'Wallis and Futuna': 'WF',
    'Western Sahara': 'EH',
    'Yemen': 'YE',
    'Zambia': 'ZM',
    'Zimbabwe': 'ZW',
}


class CodeType(int, Enum):
    alpha2 = 1
    alpha3 = 2
    numeric_code = 3
    country_name = 4


class Country(_repr.Representation):
    _name: str
    _official_name: str
    _alpha2_code: constr(min_length=2, max_length=2)  # type: ignore
    _alpha3_code: constr(min_length=3, max_length=3)  # type: ignore
    _numeric: constr(min_length=3, max_length=3)  # type: ignore

    def __init__(self, args: Union[str, Union[Tuple[str, bool], Dict[str, Any]]]):
        """
        args should be one of the following:
            * args:str => (US/United States/840)
            * args:tuple(str, bool) => (US, True)
            * args: dict(str, Union(str, Optional[bool])) => {'value': 'US', 'sensitive': False}

        if sensitive isn't activated the code will automatically ignore brackets:
        United States of America (the) -> United States of America
        besides, it will capitalize the words to fit the country name pattern
        """
        if isinstance(args, str):
            value, sensitive = args, False

        elif isinstance(args, tuple):
            if len(args) != 2:
                raise TypeError('__init__ method has one/two parameters only')
            value, sensitive = args

        elif isinstance(args, dict):
            value, sensitive = args.get('value', ''), args.get('sensitive', False)
        else:
            raise PydanticCustomError(
                'country_code_error', f'"{type(args).__name__}" is not a valid ISO 3166-1 type. Must be a string/tuple.'
            )
        source, self._alpha2_code = self.__get_type_and_alpha2(value, sensitive)
        country_data = BY_ALPHA2.get(self.alpha2_code)

        if country_data is None:
            raise PydanticCustomError('country_code_error', f'"{value}" is not a valid {source.name} ISO 3166-1 value')
        self._name, self._official_name, self._alpha3_code, self._numeric_code = country_data

    @staticmethod
    def __clean_country_name(country_name: str) -> str:
        # Remove anything in parentheses and leading/trailing white space
        country_name = re.sub(r'\s*\(.*?\)\s*', '', country_name).strip()
        # Split the country name into words
        words = country_name.split()
        # Capitalize all words except for 'and' and 'the' (that aren't the first word)
        for i in range(1, len(words)):
            if words[i].lower() not in ['and', 'the', 'of']:
                words[i] = words[i].capitalize()

        # Join the words back together into a string (works also for one word)
        words[0] = words[0].capitalize()
        country_name = ' '.join(words)
        return country_name

    @staticmethod
    def __get_type_and_alpha2(value: str, sensitive: bool) -> Tuple[CodeType, Optional[str]]:
        if value.isnumeric():
            return CodeType.numeric_code, BY_NUMERIC.get(value)
        if len(value) >= 3:
            if len(value) == 3:
                return CodeType.alpha3, BY_ALPHA3.get(value if sensitive else value.upper())
            return CodeType.country_name, BY_COUNTRY.get(value if sensitive else Country.__clean_country_name(value))
        return CodeType.alpha2, value if sensitive else value.upper()

    @classmethod
    def __get_pydantic_core_schema__(cls, **_kwargs: Any) -> core_schema.FunctionPlainSchema:
        return core_schema.function_plain_schema(cls._validate, serialization=core_schema.to_string_ser_schema())

    @classmethod
    def _validate(cls, *__input_values: Any, **_kwargs: Any) -> 'Country':
        return cls(*__input_values)

    @property
    def country_name(self) -> str:
        return self._name

    @property
    def official_name(self) -> str:
        return self._official_name

    @property
    def alpha2_code(self) -> str:
        return self._alpha2_code

    @property
    def alpha3_code(self) -> str:
        return self._alpha3_code

    @property
    def numeric_code(self) -> str:
        return self._numeric_code

    def __str__(self) -> str:
        return (
            f'country_name="{self.country_name}" official_name="{self.official_name}"'
            f' alpha2_code="{self.alpha2_code}" alpha3_code="{self.alpha3_code}"'
            f' numeric_code="{self.numeric_code}"'
        )

    def __repr_args__(self) -> '_repr.ReprArgs':
        return [
            (None, self.alpha2_code),
            ('country_name', self.country_name),
            ('official_name', self.official_name),
            ('alpha3_code', self.alpha3_code),
            ('numeric_code', self.numeric_code),
        ]

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, Country) and other.alpha2_code == self.alpha2_code

    def __ne__(self, other: Any) -> bool:
        return not self == other

    def __hash__(self) -> int:
        return hash(self.alpha2_code)
