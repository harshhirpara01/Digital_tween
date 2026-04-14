from datetime import datetime, timedelta, timezone
import json
import os
import re
import smtplib
import ssl
import traceback
import uuid
from base64 import b64decode
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import cryptography.fernet
import jwt
import mandrill
import pymongo
import requests
import sendgrid
from cryptography.fernet import Fernet
from dotenv import load_dotenv
from fastapi import Depends, security, HTTPException
from fastapi.security import OAuth2PasswordBearer, HTTPAuthorizationCredentials
from jose import JWTError
from jwt import InvalidTokenError,ExpiredSignatureError
from nacl.secret import SecretBox
from sendgrid import Mail
from slowapi import Limiter
from slowapi.util import get_ipaddr
from starlette import status

from common.responses import HEM_INTERNAL_SERVER_ERROR
# from shared.db import mdb, conn

limiter = Limiter(key_func=get_ipaddr)
rate_limit = "10/minute"

load_dotenv(dotenv_path=os.environ.get("envipath"))

"""
    MANDRILL
"""
SMTP_HOST = os.environ.get("SMTP_HOST")
SMTP_PORT = os.environ.get("SMTP_PORT")
SMTP_USERNAME = os.environ.get("SMTP_USERNAME")
SMTP_PASSWORD = os.environ.get("SMTP_PASSWORD")

mailchimp_sender_email = os.environ.get("mailchimp_sender_email")
mailchimp_from_name = os.environ.get("mailchimp_from_name")
MANDRILL_API_KEY = os.environ.get("mailchimp_apikey")

JWT_SECRET = os.environ.get("JWT_SECRET")
JWT_SECRET_ADMIN = os.environ.get("JWT_SECRET_ADMIN")

register_token_minutes = os.environ.get("register_token_minutes")
temp_login_token_hours = os.environ.get("temp_login_token_hours")
login_token_hours = os.environ.get("login_token_hours")
from_email = os.environ.get("send_grid_from_email")
sendgridapikey = os.environ.get("send_grid_api_key")
regiterlinkurl = os.environ.get("regiterlinkurl")
strippaycurrency = os.environ.get("strippaycurrency")
strip_secret_key = os.environ.get("strip_secret_key")
sendmailtype = os.environ.get("sendmailtype")

nicehashurl = os.environ.get("nicehashurl")
ipaccesskey = os.environ.get("ipaccesskey")

# host = 'https://api-test.nicehash.com'
organisation_id = 'da4d5bae-2bc6-4999-9912-6cfab7f2fe99'
key = 'f7326239-c128-4b22-90f9-e1f6de1f609a'
secret = '915f2a65-93fa-4c68-9f1d-bbd551b3fe08cc889a6d-8997-481c-a500-da34c69ffdd1'

aipriceapikey = os.environ.get("aipriceapikey")

ordertype = os.environ.get("ordertype")
algorithm = os.environ.get("algorithm")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/account/create_token")

token_store = {}

countryinfo = [
    {"code": "AD", "label": "Andorra", "phone": "376", "phoneLength": 6},
    {"code": "AE", "label": "United Arab Emirates", "phone": "971", "phoneLength": 9},
    {"code": "AF", "label": "Afghanistan", "phone": "93", "phoneLength": 9},
    {"code": "AG", "label": "Antigua and Barbuda", "phone": "1-268", "phoneLength": 10},
    {"code": "AI", "label": "Anguilla", "phone": "1-264", "phoneLength": 10},
    {"code": "AL", "label": "Albania", "phone": "355", "phoneLength": 9},
    {"code": "AM", "label": "Armenia", "phone": "374", "phoneLength": 6},
    {"code": "AO", "label": "Angola", "phone": "244", "phoneLength": 9},
    {"code": "AQ", "label": "Antarctica", "phone": "672", "phoneLength": 6},
    {"code": "AR", "label": "Argentina", "phone": "54", "phoneLength": [6, 7, 8]},
    {"code": "AS", "label": "American Samoa", "phone": "1-684", "phoneLength": 10},
    {"code": "AT", "label": "Austria", "phone": "43", "phoneLength": [10, 11]},
    {"code": "AU", "label": "Australia", "phone": "61", "suggested": True, "phoneLength": 9},
    {"code": "AW", "label": "Aruba", "phone": "297", "phoneLength": 7},
    {"code": "AX", "label": "Alland Islands", "phone": "358", "min": 7, "max": 10},
    {"code": "AZ", "label": "Azerbaijan", "phone": "994", "phoneLength": 9},
    {"code": "BA", "label": "Bosnia and Herzegovina", "phone": "387", "phoneLength": 8},
    {"code": "BB", "label": "Barbados", "phone": "1-246", "phoneLength": 10},
    {"code": "BD", "label": "Bangladesh", "phone": "880", "phoneLength": 10},
    {"code": "BE", "label": "Belgium", "phone": "32", "phoneLength": 9},
    {"code": "BF", "label": "Burkina Faso", "phone": "226", "phoneLength": 8},
    {"code": "BG", "label": "Bulgaria", "phone": "359", "phoneLength": 9},
    {"code": "BH", "label": "Bahrain", "phone": "973", "phoneLength": 8},
    {"code": "BI", "label": "Burundi", "phone": "257", "phoneLength": 8},
    {"code": "BJ", "label": "Benin", "phone": "229", "phoneLength": 8},
    {"code": "BL", "label": "Saint Barthelemy", "phone": "590", "phoneLength": 9},
    {"code": "BM", "label": "Bermuda", "phone": "1-441", "phoneLength": 10},
    {"code": "BN", "label": "Brunei Darussalam", "phone": "673", "phoneLength": 7},
    {"code": "BO", "label": "Bolivia", "phone": "591", "phoneLength": 9},
    {"code": "BR", "label": "Brazil", "phone": "55", "phoneLength": 11},
    {"code": "BS", "label": "Bahamas", "phone": "1-242", "phoneLength": 10},
    {"code": "BT", "label": "Bhutan", "phone": "975", "phoneLength": 7},
    {"code": "BV", "label": "Bouvet Island", "phone": "47", "phoneLength": 10},
    {"code": "BW", "label": "Botswana", "phone": "267", "phoneLength": 7},
    {"code": "BY", "label": "Belarus", "phone": "375", "phoneLength": 9},
    {"code": "BZ", "label": "Belize", "phone": "501", "phoneLength": 7},
    {"code": "CA", "label": "Canada", "phone": "1", "suggested": True, "phoneLength": 10},
    {"code": "CC", "label": "Cocos (Keeling) Islands", "phone": "61", "phoneLength": 10},
    {"code": "CD", "label": "Congo, Democratic Republic of the", "phone": "243", "phoneLength": 7},
    {"code": "CF", "label": "Central African Republic", "phone": "236", "phoneLength": 8},
    {"code": "CG", "label": "Congo, Republic of the", "phone": "242", "phoneLength": 9},
    {"code": "CH", "label": "Switzerland", "phone": "41", "phoneLength": 9},
    {"code": "CI", "label": "Cote d'Ivoire", "phone": "225", "phoneLength": 8},
    {"code": "CK", "label": "Cook Islands", "phone": "682", "phoneLength": 5},
    {"code": "CL", "label": "Chile", "phone": "56", "phoneLength": 9},
    {"code": "CM", "label": "Cameroon", "phone": "237", "phoneLength": 9},
    {"code": "CN", "label": "China", "phone": "86", "phoneLength": 11},
    {"code": "CO", "label": "Colombia", "phone": "57", "phoneLength": 10},
    {"code": "CR", "label": "Costa Rica", "phone": "506", "phoneLength": 8},
    {"code": "CU", "label": "Cuba", "phone": "53", "phoneLength": 8},
    {"code": "CV", "label": "Cape Verde", "phone": "238", "phoneLength": 7},
    {"code": "CW", "label": "Curacao", "phone": "599", "phoneLength": 7},
    {"code": "CX", "label": "Christmas Island", "phone": "61", "phoneLength": 9},
    {"code": "CY", "label": "Cyprus", "phone": "357", "phoneLength": 8},
    {"code": "CZ", "label": "Czech Republic", "phone": "420", "phoneLength": 9},
    {"code": "DE", "label": "Germany", "phone": "49", "suggested": True, "phoneLength": 10},
    {"code": "DJ", "label": "Djibouti", "phone": "253", "phoneLength": 10},
    {"code": "DK", "label": "Denmark", "phone": "45", "phoneLength": 8},
    {"code": "DM", "label": "Dominica", "phone": "1-767", "phoneLength": 10},
    {"code": "DO", "label": "Dominican Republic", "phone": "1-809", "phoneLength": 10},
    {"code": "DZ", "label": "Algeria", "phone": "213", "phoneLength": 9},
    {"code": "EC", "label": "Ecuador", "phone": "593", "phoneLength": 9},
    {"code": "EE", "label": "Estonia", "phone": "372", "phoneLength": 8},
    {"code": "EG", "label": "Egypt", "phone": "20", "phoneLength": 10},
    {"code": "EH", "label": "Western Sahara", "phone": "212", "phoneLength": 9},
    {"code": "ER", "label": "Eritrea", "phone": "291", "phoneLength": 7},
    {"code": "ES", "label": "Spain", "phone": "34", "phoneLength": 9},
    {"code": "ET", "label": "Ethiopia", "phone": "251", "phoneLength": 9},
    {"code": "FI", "label": "Finland", "phone": "358", "min": 9, "max": 11},
    {"code": "FJ", "label": "Fiji", "phone": "679", "phoneLength": 7},
    {"code": "FK", "label": "Falkland Islands (Malvinas)", "phone": "500", "phoneLength": 5},
    {"code": "FM", "label": "Micronesia, Federated States of", "phone": "691", "phoneLength": 7},
    {"code": "FO", "label": "Faroe Islands", "phone": "298", "phoneLength": 5},
    {"code": "FR", "label": "France", "phone": "33", "suggested": True, "phoneLength": 9},
    {"code": "GA", "label": "Gabon", "phone": "241", "phoneLength": 7},
    {"code": "GB", "label": "United Kingdom", "phone": "44", "phoneLength": 10},
    {"code": "GD", "label": "Grenada", "phone": "1-473", "phoneLength": 10},
    {"code": "GE", "label": "Georgia", "phone": "995", "phoneLength": 9},
    {"code": "GF", "label": "French Guiana", "phone": "594", "phoneLength": 9},
    {"code": "GG", "label": "Guernsey", "phone": "44", "phoneLength": 10},
    {"code": "GH", "label": "Ghana", "phone": "233", "phoneLength": 9},
    {"code": "GI", "label": "Gibraltar", "phone": "350", "phoneLength": 8},
    {"code": "GL", "label": "Greenland", "phone": "299", "phoneLength": 6},
    {"code": "GM", "label": "Gambia", "phone": "220", "phoneLength": 7},
    {"code": "GN", "label": "Guinea", "phone": "224", "phoneLength": 9},
    {"code": "GP", "label": "Guadeloupe", "phone": "590", "phoneLength": 9},
    {"code": "GQ", "label": "Equatorial Guinea", "phone": "240", "phoneLength": 9},
    {"code": "GR", "label": "Greece", "phone": "30", "phoneLength": 10},
    {"code": "GS", "label": "South Georgia and the South Sandwich Islands", "phone": "500", "phoneLength": 5},
    {"code": "GT", "label": "Guatemala", "phone": "502", "phoneLength": 8},
    {"code": "GU", "label": "Guam", "phone": "1-671", "phoneLength": 10},
    {"code": "GW", "label": "Guinea-Bissau", "phone": "245", "phoneLength": 9},
    {"code": "GY", "label": "Guyana", "phone": "592", "phoneLength": 7},
    {"code": "HK", "label": "Hong Kong", "phone": "852", "phoneLength": 8},
    {"code": "HM", "label": "Heard Island and McDonald Islands", "phone": "672", "phoneLength": 10},
    {"code": "HN", "label": "Honduras", "phone": "504", "phoneLength": 8},
    {"code": "HR", "label": "Croatia", "phone": "385", "phoneLength": 9},
    {"code": "HT", "label": "Haiti", "phone": "509", "phoneLength": 8},
    {"code": "HU", "label": "Hungary", "phone": "36", "phoneLength": 9},
    {"code": "ID", "label": "Indonesia", "phone": "62", "phoneLength": 11},
    {"code": "IE", "label": "Ireland", "phone": "353", "phoneLength": 9},
    {"code": "IL", "label": "Israel", "phone": "972", "phoneLength": 9},
    {"code": "IM", "label": "Isle of Man", "phone": "44", "phoneLength": 10},
    {"code": "IN", "label": "India", "phone": "91", "phoneLength": 10},
    {"code": "IO", "label": "British Indian Ocean Territory", "phone": "246", "phoneLength": 7},
    {"code": "IQ", "label": "Iraq", "phone": "964", "phoneLength": 10},
    {"code": "IR", "label": "Iran, Islamic Republic of", "phone": "98", "phoneLength": 11},
    {"code": "IS", "label": "Iceland", "phone": "354", "phoneLength": 7},
    {"code": "IT", "label": "Italy", "phone": "39", "phoneLength": 10},
    {"code": "JE", "label": "Jersey", "phone": "44", "phoneLength": 10},
    {"code": "JM", "label": "Jamaica", "phone": "1-876", "phoneLength": 10},
    {"code": "JO", "label": "Jordan", "phone": "962", "phoneLength": [8, 9]},
    {"code": "JP", "label": "Japan", "phone": "81", "suggested": True},
    {"code": "KE", "label": "Kenya", "phone": "254", "phoneLength": 10},
    {"code": "KG", "label": "Kyrgyzstan", "phone": "996", "phoneLength": 9},
    {"code": "KH", "label": "Cambodia", "phone": "855", "phoneLength": 9},
    {"code": "KI", "label": "Kiribati", "phone": "686", "phoneLength": 8},
    {"code": "KM", "label": "Comoros", "phone": "269", "phoneLength": 7},
    {"code": "KN", "label": "Saint Kitts and Nevis", "phone": "1-869", "phoneLength": 10},
    {"code": "KP", "label": "Korea, Democratic People's Republic of", "phone": "850", "phoneLength": [4, 6, 7, 13]},
    {"code": "KR", "label": "Korea, Republic of", "phone": "82", "phoneLength": [7, 8]},
    {"code": "KW", "label": "Kuwait", "phone": "965", "phoneLength": 8},
    {"code": "KY", "label": "Cayman Islands", "phone": "1-345", "phoneLength": 7},
    {"code": "KZ", "label": "Kazakhstan", "phone": "7", "phoneLength": 10},
    {"code": "LA", "label": "Lao People's Democratic Republic", "phone": "856", "phoneLength": [8, 9]},
    {"code": "LB", "label": "Lebanon", "phone": "961", "phoneLength": [7, 8]},
    {"code": "LC", "label": "Saint Lucia", "phone": "1-758", "phoneLength": 7},
    {"code": "LI", "label": "Liechtenstein", "phone": "423", "phoneLength": 7},
    {"code": "LK", "label": "Sri Lanka", "phone": "94", "phoneLength": 7},
    {"code": "LR", "label": "Liberia", "phone": "231", "phoneLength": [8, 9]},
    {"code": "LS", "label": "Lesotho", "phone": "266", "phoneLength": 8},
    {"code": "LT", "label": "Lithuania", "phone": "370", "phoneLength": 8},
    {"code": "LU", "label": "Luxembourg", "phone": "352", "phoneLength": 9},
    {"code": "LV", "label": "Latvia", "phone": "371", "phoneLength": 8},
    {"code": "LY", "label": "Libya", "phone": "218", "phoneLength": 10},
    {"code": "MA", "label": "Morocco", "phone": "212", "phoneLength": 9},
    {"code": "MC", "label": "Monaco", "phone": "377", "phoneLength": 8},
    {"code": "MD", "label": "Moldova, Republic of", "phone": "373", "phoneLength": 8},
    {"code": "ME", "label": "Montenegro", "phone": "382", "phoneLength": 8},
    {"code": "MF", "label": "Saint Martin (French part)", "phone": "590", "phoneLength": 6},
    {"code": "MG", "label": "Madagascar", "phone": "261", "phoneLength": 7},
    {"code": "MH", "label": "Marshall Islands", "phone": "692", "phoneLength": 7},
    {"code": "MK", "label": "Macedonia, the Former Yugoslav Republic of", "phone": "389", "phoneLength": 8},
    {"code": "ML", "label": "Mali", "phone": "223", "phoneLength": 8},
    {"code": "MM", "label": "Myanmar", "phone": "95", "min": 7, "max": 10},
    {"code": "MN", "label": "Mongolia", "phone": "976", "phoneLength": 8},
    {"code": "MO", "label": "Macao", "phone": "853", "phoneLength": 8},
    {"code": "MP", "label": "Northern Mariana Islands", "phone": "1-670", "phoneLength": 7},
    {"code": "MQ", "label": "Martinique", "phone": "596", "phoneLength": 9},
    {"code": "MR", "label": "Mauritania", "phone": "222", "phoneLength": 8},
    {"code": "MS", "label": "Montserrat", "phone": "1-664", "phoneLength": 10},
    {"code": "MT", "label": "Malta", "phone": "356", "phoneLength": 8},
    {"code": "MU", "label": "Mauritius", "phone": "230", "phoneLength": 8},
    {"code": "MV", "label": "Maldives", "phone": "960", "phoneLength": 7},
    {"code": "MW", "label": "Malawi", "phone": "265", "phoneLength": [7, 8, 9]},
    {"code": "MX", "label": "Mexico", "phone": "52", "phoneLength": 10},
    {"code": "MY", "label": "Malaysia", "phone": "60", "phoneLength": 7},
    {"code": "MZ", "label": "Mozambique", "phone": "258", "phoneLength": 12},
    {"code": "NA", "label": "Namibia", "phone": "264", "phoneLength": 7},
    {"code": "NC", "label": "New Caledonia", "phone": "687", "phoneLength": 6},
    {"code": "NE", "label": "Niger", "phone": "227", "phoneLength": 8},
    {"code": "NF", "label": "Norfolk Island", "phone": "672", "phoneLength": 6},
    {"code": "NG", "label": "Nigeria", "phone": "234", "phoneLength": 8},
    {"code": "NI", "label": "Nicaragua", "phone": "505", "phoneLength": 8},
    {"code": "NL", "label": "Netherlands", "phone": "31", "phoneLength": 9},
    {"code": "NO", "label": "Norway", "phone": "47", "phoneLength": 8},
    {"code": "NP", "label": "Nepal", "phone": "977", "phoneLength": 10},
    {"code": "NR", "label": "Nauru", "phone": "674", "phoneLength": 7},
    {"code": "NU", "label": "Niue", "phone": "683", "phoneLength": 4},
    {"code": "NZ", "label": "New Zealand", "phone": "64", "phoneLength": [8, 9]},
    {"code": "OM", "label": "Oman", "phone": "968", "phoneLength": 8},
    {"code": "PA", "label": "Panama", "phone": "507", "phoneLength": 8},
    {"code": "PE", "label": "Peru", "phone": "51", "phoneLength": 9},
    {"code": "PF", "label": "French Polynesia", "phone": "689", "phoneLength": 8},
    {"code": "PG", "label": "Papua New Guinea", "phone": "675", "phoneLength": 8},
    {"code": "PH", "label": "Philippines", "phone": "63", "phoneLength": 10},
    {"code": "PK", "label": "Pakistan", "phone": "92", "phoneLength": 10},
    {"code": "PL", "label": "Poland", "phone": "48", "phoneLength": 9},
    {"code": "PM", "label": "Saint Pierre and Miquelon", "phone": "508", "phoneLength": 6},
    {"code": "PN", "label": "Pitcairn", "phone": "870", "phoneLength": 9},
    {"code": "PR", "label": "Puerto Rico", "phone": "1", "phoneLength": 10},
    {"code": "PS", "label": "Palestine, State of", "phone": "970", "phoneLength": 9},
    {"code": "PT", "label": "Portugal", "phone": "351", "phoneLength": 9},
    {"code": "PW", "label": "Palau", "phone": "680", "phoneLength": 7},
    {"code": "PY", "label": "Paraguay", "phone": "595", "phoneLength": 9},
    {"code": "QA", "label": "Qatar", "phone": "974", "phoneLength": 8},
    {"code": "RE", "label": "Reunion", "phone": "262", "phoneLength": 10},
    {"code": "RO", "label": "Romania", "phone": "40", "phoneLength": 10},
    {"code": "RS", "label": "Serbia", "phone": "381", "phoneLength": 9},
    {"code": "RU", "label": "Russian Federation", "phone": "7", "phoneLength": 10},
    {"code": "RW", "label": "Rwanda", "phone": "250", "phoneLength": 9},
    {"code": "SA", "label": "Saudi Arabia", "phone": "966", "phoneLength": 9},
    {"code": "SB", "label": "Solomon Islands", "phone": "677", "phoneLength": 7},
    {"code": "SC", "label": "Seychelles", "phone": "248", "phoneLength": 7},
    {"code": "SD", "label": "Sudan", "phone": "249", "phoneLength": 7},
    {"code": "SE", "label": "Sweden", "phone": "46", "phoneLength": 7},
    {"code": "SG", "label": "Singapore", "phone": "65", "phoneLength": 8},
    {"code": "SH", "label": "Saint Helena", "phone": "290", "phoneLength": 4},
    {"code": "SI", "label": "Slovenia", "phone": "386", "phoneLength": 9},
    {"code": "SJ", "label": "Svalbard and Jan Mayen", "phone": "47", "phoneLength": 8},
    {"code": "SK", "label": "Slovakia", "phone": "421", "phoneLength": 9},
    {"code": "SL", "label": "Sierra Leone", "phone": "232", "phoneLength": 8},
    {"code": "SM", "label": "San Marino", "phone": "378", "phoneLength": 10},
    {"code": "SN", "label": "Senegal", "phone": "221", "phoneLength": 9},
    {"code": "SO", "label": "Somalia", "phone": "252", "phoneLength": [8, 9]},
    {"code": "SR", "label": "Suriname", "phone": "597", "phoneLength": [6, 7]},
    {"code": "SS", "label": "South Sudan", "phone": "211", "phoneLength": 7},
    {"code": "ST", "label": "Sao Tome and Principe", "phone": "239", "phoneLength": 7},
    {"code": "SV", "label": "El Salvador", "phone": "503", "phoneLength": 8},
    {"code": "SX", "label": "Sint Maarten (Dutch part)", "phone": "1-721", "phoneLength": 10},
    {"code": "SY", "label": "Syrian Arab Republic", "phone": "963", "phoneLength": 7},
    {"code": "SZ", "label": "Swaziland", "phone": "268", "phoneLength": 8},
    {"code": "TC", "label": "Turks and Caicos Islands", "phone": "1-649", "phoneLength": 10},
    {"code": "TD", "label": "Chad", "phone": "235", "phoneLength": 6},
    {"code": "TF", "label": "French Southern Territories", "phone": "262", "phoneLength": 10},
    {"code": "TG", "label": "Togo", "phone": "228", "phoneLength": 8},
    {"code": "TH", "label": "Thailand", "phone": "66", "phoneLength": 9},
    {"code": "TJ", "label": "Tajikistan", "phone": "992", "phoneLength": 9},
    {"code": "TK", "label": "Tokelau", "phone": "690", "phoneLength": 5},
    {"code": "TL", "label": "Timor-Leste", "phone": "670", "phoneLength": 7},
    {"code": "TM", "label": "Turkmenistan", "phone": "993", "phoneLength": 8},
    {"code": "TN", "label": "Tunisia", "phone": "216", "phoneLength": 8},
    {"code": "TO", "label": "Tonga", "phone": "676", "phoneLength": 5},
    {"code": "TR", "label": "Turkey", "phone": "90", "phoneLength": 11},
    {"code": "TT", "label": "Trinidad and Tobago", "phone": "1-868", "phoneLength": 7},
    {"code": "TV", "label": "Tuvalu", "phone": "688", "phoneLength": 5},
    {"code": "TW", "label": "Taiwan, Province of China", "phone": "886", "phoneLength": 9},
    {"code": "TZ", "label": "United Republic of Tanzania", "phone": "255", "phoneLength": 7},
    {"code": "UA", "label": "Ukraine", "phone": "380", "phoneLength": 9},
    {"code": "UG", "label": "Uganda", "phone": "256", "phoneLength": 7},
    {"code": "US", "label": "United States", "phone": "1", "suggested": True, "phoneLength": 10},
    {"code": "UY", "label": "Uruguay", "phone": "598", "phoneLength": 8},
    {"code": "UZ", "label": "Uzbekistan", "phone": "998", "phoneLength": 9},
    {"code": "VA", "label": "Holy See (Vatican City State)", "phone": "379", "phoneLength": 10},
    {"code": "VC", "label": "Saint Vincent and the Grenadines", "phone": "1-784", "phoneLength": 7},
    {"code": "VE", "label": "Venezuela", "phone": "58", "phoneLength": 7},
    {"code": "VG", "label": "British Virgin Islands", "phone": "1-284", "phoneLength": 7},
    {"code": "VI", "label": "US Virgin Islands", "phone": "1-340", "phoneLength": 10},
    {"code": "VN", "label": "Vietnam", "phone": "84", "phoneLength": 9},
    {"code": "VU", "label": "Vanuatu", "phone": "678", "phoneLength": 5},
    {"code": "WF", "label": "Wallis and Futuna", "phone": "681", "phoneLength": 6},
    {"code": "WS", "label": "Samoa", "phone": "685", "phoneLength": [5, 6, 7]},
    {"code": "XK", "label": "Kosovo", "phone": "383", "phoneLength": 8},
    {"code": "YE", "label": "Yemen", "phone": "967", "phoneLength": 9},
    {"code": "YT", "label": "Mayotte", "phone": "262", "phoneLength": 9},
    {"code": "ZA", "label": "South Africa", "phone": "27", "phoneLength": 9},
    {"code": "ZM", "label": "Zambia", "phone": "260", "phoneLength": 9},
    {"code": "ZW", "label": "Zimbabwe", "phone": "263", "phoneLength": 9}
]


def check_string(exestring):
    """
        function for check in execution string has '<','>', '/'
    """
    if '>' in exestring:
        return False
    elif '<' in exestring:
        return False
    elif '/' in exestring:
        return False
    else:
        return True


def check_string1(exestring):
    """
        function for check in execution string has '<','>'
    """
    if '>' in exestring:
        return False
    elif '<' in exestring:
        return False
    else:
        return True


def encrypt_str(msg):
    """
        function for encrypt the string and return encrypted string
    """
    try:
        key = "cElqKQXJ2J2JjXbo3yvNnu5KDUs1dMJXy9PQxf-6bfU="
        fernet = Fernet(key)
        encMessage = fernet.encrypt(msg.encode())
        return {
            "code": 200,
            "converted_value": encMessage,
        }
    except Exception as e:
        err_send_telegram(e)
        return {
            "code": 500,
            "status": "error",
            "message": "Exception {} occurred while encrypt_str.".format(e)
        }


def encrypt_str_link(msg):
    """
        function for encrypt the string and return encrypted string
    """
    key = "cElqKQXJ2J2JjXbo3yvNnu5KDUs1dMJXy9PQxf-6bfU="
    fernet = Fernet(key)
    encMessage = fernet.encrypt(msg.encode())
    return {
        "code": 200,
        "converted_value": str(encMessage),
    }


def decrypt_str(encrypted_str: str):
    """
        function for decrypt the encrypted string and return decrypted string
    """
    try:
        key = "cElqKQXJ2J2JjXbo3yvNnu5KDUs1dMJXy9PQxf-6bfU="
        fernet = Fernet(key.encode())
        decMessage = fernet.decrypt(encrypted_str.encode()).decode()
        return {
            "code": 200,
            "decMessage": decMessage
        }
    except cryptography.fernet.InvalidToken as e:
        err_send_telegram(e)
        return {
            "code": 400,
            "error": "Invalid Token."
        }

    except TypeError as TE:
        err_send_telegram(TE)
        return {
            "code": 400,
            "error": "Type error. Please check your input."
        }
    except ValueError as ve:
        err_send_telegram(ve)
        return {
            "code": 400,
            "error": str(ve)
        }
    except KeyError as ke:
        err_send_telegram(ke)
        return {
            "code": 400,
            "error": str(ke)
        }


def dec_password(enc_str):
    """
    function for decrypt password with js
    """
    try:
        secret_key = 'WSVUBLO9ZovEhOw2GVwy5ElSj2xOPPaX'  # secrate key of js(front-react)
        encrypted = enc_str.split(':')
        nonce = b64decode(encrypted[0])
        encrypted = b64decode(encrypted[1])
        box = SecretBox(bytes(secret_key, encoding='utf8'))
        decrypted = box.decrypt(encrypted, nonce).decode('utf-8')
        return {
            "code": "success",
            "message": "ok",
            "decrypted": decrypted
        }
    except TypeError as TE:
        err_send_telegram(TE)
        return {
            "code": 400,
            "error": "Input type error. Please check your input."
        }
    except ValueError as ve:
        err_send_telegram(ve)

        return {
            "code": 400,
            "error": str(ve)
        }
    except KeyError as ke:
        err_send_telegram(ke)

        return {
            "code": 400,
            "error": str(ke)
        }


# def resultset(cursor):
#     """"
#     function for get all result set with key-value pair from table
#     """
#     sets = []
#     while True:
#         names = [c[0] for c in cursor.description]
#         set_ = []
#         while True:
#             row_raw = cursor.fetchone()
#             if row_raw is None:
#                 break
#             row = dict(zip(names, row_raw))
#             set_.append(row)
#         sets.append(list(set_))
#         if cursor.nextset() is None or cursor.description is None:
#             break
#     return sets

def resultset(cursor, type="fetchall"):
    '''
    Add Header to mysql query output

    :param cursor:
    :param type optional[fetchone]:
    :return dictionary or list with header:
    '''

    if type == "fetchall":
        fetch_data = cursor.fetchall()
        if not fetch_data:
            return []
        column_names = [column[0] for column in cursor.description]
        data = []
        for i in fetch_data:
            x = {}
            for k, j in enumerate(column_names):
                x.update({j: i[k]})
            data.append(x)

    elif type == "fetchone":
        fetch_data = cursor.fetchone()
        if not fetch_data:
            return {}
        column_names = [column[0] for column in cursor.description]
        data = {}
        for k, j in enumerate(column_names):
            data.update({j: fetch_data[k]})

    return data


# def resultset(cursor, type="fetchall"):
#     '''
#     Add Header to mysql query output
#
#     :param cursor:
#     :param type optional[fetchone]:
#     :return dictionary or list with header:
#     '''
#
#     if type == "fetchall":
#         fetch_data = cursor.fetchall()
#         if not fetch_data:
#             return []
#         column_names = [column[0] for column in cursor.description]
#         data = []
#         for i in fetch_data:
#             x = {}
#             for k, j in enumerate(column_names):
#                 x.update({j: i[k]})
#             data.append(x)
#
#     else:
#         fetch_data = cursor.fetchone()
#         if not fetch_data:
#             return {}
#         column_names = [column[0] for column in cursor.description]
#         data = {}
#         for k, j in enumerate(column_names):
#             data.update({j: fetch_data[k]})
#
#     return data

#
# def create_token(email, uid):
#     """
#     function for create token
#     """
#     try:
#
#         cursor = conn.cursor()
#         uniq_key = uuid.uuid4().hex
#         execstring = f"exec SP_update_publickey @mode='WEB', @publickey= '{uniq_key}', @email= '{email}'"
#         cursor.execute(execstring)
#
#         expire = (datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=10))
#
#         token_details = {
#             "email": email,
#             "public_key": uniq_key,
#             "userid": uid,
#             "exp": expire,
#             "login_type": 'register'
#         }
#         print("=========================", token_details)
#         access_token = jwt.encode(token_details, JWT_SECRET, algorithm='HS256')
#         # acc = encrypt_str(access_token)
#         return {
#             "code": 200,
#             "status": "success",
#             "access_token": access_token,
#             "token_type": "bearer",
#         }
#     except jwt.ExpiredSignatureError:
#         return {
#             "code": 401,
#             "status": "error",
#             "message": "JWT has expired."
#         }
#     except jwt.InvalidTokenError:
#         return {
#             "code": 400,
#             "status": "error",
#             "message": "Invalid token. Please check and try again."
#         }
#     except Exception as e:
#         return {
#             "code": 500,
#             "status": "error",
#             "message": HEM_INTERNAL_SERVER_ERROR
#         }




JWT_SECRET =os.getenv("JWT_SECRET")
ALGORITHM = os.getenv("ALGORITHM")


def create_token(email, uid):
    try:
        uniq_key = uuid.uuid4().hex
        now = datetime.utcnow()
        expire = now + timedelta(minutes=30)
        token_details = {
            "email": email,
            "id": uid,
            "iat": now,
            "exp": expire,
            "public_key": uniq_key,
            "login_type": 'WEB'
        }

        access_token = jwt.encode(token_details, JWT_SECRET, algorithm=ALGORITHM)
        return access_token

    except Exception as e:
        return {"code": 500, "status": "error", "message": f"Exception occurred while creating token: {e}"}



def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    token = credentials.credentials

    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[ALGORITHM])

        user_id = payload.get("id")
        email = payload.get("email")

        if user_id is None or email is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
        return {
            "id": user_id,
            "email": email,

        }

    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired"
        )

    except InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token is invalid or expired"
        )
def send_mail(email, html, subject, preview_text=None):
    send_mail_type = str(sendmailtype)

    if send_mail_type == 'sendgrid':
        """
        function for send_mail using Sendgrid
        """

        message = Mail(
            from_email=from_email,
            to_emails=email,
            subject=subject,
            html_content=html)
        try:
            sg = sendgrid.SendGridAPIClient(sendgridapikey)
            response = sg.send(message)
            """ add logger for print """
        except Exception as e:
            pass

    elif send_mail_type == 'smtp':
        sender_email = "sarvopari16@gmail.com"
        password = "okhp klyn kugv mmvi"
        message = MIMEMultipart("alternative")
        message["Subject"] = str(subject)
        message["From"] = sender_email
        message["To"] = email
        part1 = MIMEText(html, "html")
        message.attach(part1)

        context = ssl.create_default_context()
        try:
            with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
                server.login(sender_email, password)
                server.sendmail(
                    sender_email, email, message.as_string()
                )
        except Exception as e:
            pass

    elif send_mail_type == 'mailchimp':
        try:
            client = mandrill.Mandrill(MANDRILL_API_KEY)
            message = {
                "from_email": mailchimp_sender_email,
                "from_name": mailchimp_from_name,
                "to": [
                    {"email": str(email)}
                ],
                "subject": subject,
                "html": html,
                "text": preview_text,  # Plain text version (Preview text)
                "important": True,  # Mark email as important (optional)

            }
            result = client.messages.send(message=message)
            print("result-->>>", result)

        except mandrill.Error as e:
            print("=====", e)
            pass


"""
    function for check apikey and apidomain 
"""


def check_api_key_2(apikey, apidomain):
    try:
        apikey_data = list(mdb.ApiData.find({}))
        print("check_api_key_2 ----------")
        if apikey_data[0]['apikey'] == str(apikey):

            # if apikey_data[0]['apidomain'] == str(apidomain):
            # if str(apidomain) in apikey_data[0]["apidomain"]:
            #     print("---newcheckapifunction---")
            #     json_data = {
            #         "message": "",
            #         "status": "success",
            #         "code": 200
            #     }
            #     return json_data
            # else:
            #     json_data = {
            #         "message": "Please Check your Domain",
            #         "status": "fail",
            #         "code": 400
            #     }
            #     return json_data,
            json_data = {
                "message": "",
                "status": "success",
                "code": 200
            }
            return json_data
        else:
            json_data = {
                "message": "Please Check your apikey",
                "status": "fail",
                "code": 400
            }
            return json_data,
    except pymongo.errors as e:
        return {
            "message": "Something Went Wrong Please try Again",
            "status": "fail",
            "code": 400
        }


async def authenticate_user_check_token(email):
    """
        function for get private_key  and id for token
    """
    try:
        cursor = conn.cursor()
        execstring = f"exec SP_Login @mode='GETTOKENINFO',@loginid='{email}',@password='',@loginip='',@loginbrowser='',@loglocation='',@userid=0"
        cursor.execute(execstring)
        data = resultset(cursor)
        cursor.close()

        return data[0]
    except Exception as e:
        return []


async def get_current_user(access_token: str = Depends(oauth2_scheme)):
    """
    function for check token valid or not
    """
    print("access_token", access_token)
    try:
        payload = jwt.decode(str(access_token), JWT_SECRET, algorithms=['HS256'])
        expiration_time = datetime.datetime.fromtimestamp(payload.get('exp'), datetime.timezone.utc)
        current_time = datetime.datetime.now(datetime.timezone.utc)
        if current_time >= expiration_time:
            return {
                "code": 401,
                "message": "Token expired"
            }
        else:
            print("Login Process Start Token Is Valid")
            data = await authenticate_user_check_token(payload.get('email'))
            print("------------------------------", data)

            if str(payload.get("public_key")) == str(data['publickey']):
                return {
                    "status": 200,
                    "userid": payload.get('userid'),
                    "email": payload.get('email')
                }
            else:
                return {
                    "code": 401,
                    "message": "Token expired"
                }

    except IndexError as d:
        traceback.print_exc()
        return {
            "code": 401,
            "message": "Token expired"
        }

    except KeyError as ek:
        traceback.print_exc()
        return {
            "code": 401,
            "message": "Something Went wrong please Try again."
        }

    except jwt.exceptions.ExpiredSignatureError as es:
        traceback.print_exc()
        return {
            "code": 401,
            "message": "Token expired"
        }

    except jwt.exceptions.InvalidSignatureError as s:
        traceback.print_exc()
        return {
            "code": 401,
            "message": "Invalid Token"
        }

    except jwt.DecodeError:
        traceback.print_exc()
        return {
            "code": 401,
            "message": "Token expired"
        }


def ipcheck(ip):
    """
    """
    try:
        address_url = f'https://api.ipapi.com/api/{ip}?access_key={ipaccesskey}'
        PG_url = requests.post(address_url)
        res = json.loads(PG_url.content.decode('utf-8'))

        return {
            "code": "success",
            "data": res
        }
    except Exception as e:
        return {
            "code": "error",
            "message": "Error {} occurred while get_details_by_ip_new.".format(e)
        }


def email_notification_log(email_description: str, email_type: str, emailid, userid=0):
    """
    function for save email log
    """
    try:
        new_content = email_description.replace("'", ' " ')
        cursor = conn.cursor()
        execstring = f"exec Sp_email_notification_log {userid},'{new_content}','{email_type}','{emailid}'"
        cursor.execute(execstring)
        data = resultset(cursor)
        return data
    except Exception as e:
        return e


def btcprice():
    """
        https://api.coinmarketcap.com/data-api/v3/cryptocurrency/market-pairs/latest?slug=bitcoin
    """
    url2 = "https://api.coinmarketcap.com/data-api/v3/cryptocurrency/market-pairs/latest?slug=bitcoin"

    payload = {}
    headers = {}

    response2 = requests.request("GET", url2, headers=headers, data=payload)
    res2 = json.loads(response2.content.decode('utf-8'))
    print(res2['data']['marketPairs'][0]['price'])

    return res2['data']['marketPairs'][0]['price']


EMAIL_REGEX = r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"
PASSWORD_REGEX = r"^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&\s]{8,12}$"  # Min 8 characters, at least 1 uppercase, 1 lowercase, 1 digit, and 1 special character
VERIFYCODED_REGEX = r"^\d+$"
NAME_REGEX = r'[A-Za-z]+'
MOBILE_REGEX = r"^\+?[1-9]\d{1,14}$"  # This is for international mobile format
GOOGLE_ID_REGEX = r"^[A-Za-z0-9-_]{20,}$"  # A general regex for Google IDs (length >= 20 alphanumeric characters


def validate_email(email):
    if not re.match(EMAIL_REGEX, email):
        return False
    return True


def validate_name(name, namedesc):
    if not re.fullmatch(NAME_REGEX, name):
        return False
    return True


def validate_mobile(mobile):
    if not re.match(MOBILE_REGEX, mobile):
        return False
    return True


def validate_verify_code(v):
    if not re.match(VERIFYCODED_REGEX, v):  # regex for digits only
        return False
    return True


import hashlib
import hmac

secret_key = 'e8ae5c5d5cd7f0f1bec2303ad04a7c80f09f'


def validate_signature(payload: dict, signature: str) -> bool:
    """
    # Convert the payload to a JSON string, matching the client's serialization format
    """
    payload_string = json.dumps(payload, separators=(',', ':'))
    computed_signature = hmac.new(secret_key.encode(), payload_string.encode(), hashlib.sha256).hexdigest()
    return computed_signature == signature


def dec_payload(enc_str):
    """
    function for decrypt password with js
    """
    try:
        secret_key = 'djzlJ7awmcDSO0pkjoTfeeBue7YnqLPX'  # secrate key of js(front-react)
        encrypted = enc_str.split(':')
        nonce = b64decode(encrypted[0])
        encrypted = b64decode(encrypted[1])
        box = SecretBox(bytes(secret_key, encoding='utf8'))
        decrypted = box.decrypt(encrypted, nonce).decode('utf-8')
        return {
            "code": "success",
            "message": "ok",
            "decrypted": decrypted
        }
    except Exception as e:
        return {
            "code": "error",
            "message": "Error {} occurred while dec_password.".format(e)
        }


def validate_password(password):
    if len(password) < 8:
        return "Password must be min 8 character."

    if not any(char.isupper() for char in password):
        return "Password must contain at least one uppercase letter."

    if not any(char.islower() for char in password):
        return "Password must contain at least one lowercase letter."

    if not any(char.isdigit() for char in password):
        return "Password must contain at least one digit."

    special_characters = "#@$!%*?^&"
    if not any(char in special_characters for char in password):
        return "Password must contain at least one special character (#@$!%*?^&)."

    return True


# def check_credential(apikey, apidomain):
#     try:
#         apikeydata = check_api_key_2(
#             str(apikey),
#             str(apidomain)
#         )
#         if apikeydata["status"].lower() != 'success':
#             return False, apikeydata["message"]
#
#         return True, apikeydata["message"]
#     except (TypeError, KeyError) as e:
#         return False, f"Missing required header: {e}"


def err_send_telegram(msg):
    url = "https://errorbot.niqox.com/sendErr"
    error_formate = {
        "error": msg,
        "time": str(datetime.datetime.now()),
        "project_name": "omnes"
    }
    data = {
        "msg": json.dumps(error_formate),
        "project": "Admin_omnes_py_API"
    }
    response = requests.post(url, json=data)
    return response.json()  # Optional: Return response for debuggin
