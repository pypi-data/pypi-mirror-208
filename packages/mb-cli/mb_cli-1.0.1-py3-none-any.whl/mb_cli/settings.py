import json
import os
import site

from dotenv import load_dotenv

load_dotenv()

TOR_PROXY = os.environ.get('TOR_PROXY')
TOR_ADDRESS = os.environ.get('TOR_ADDRESS')
CLEAR_DOMAIN = os.environ.get('CLEAR_DOMAIN')

VERSION = os.environ.get('VERSION')

COIN_LIST = os.environ.get('COIN_LIST').split(',')  # to easily update supported coins list

if site.ENABLE_USER_SITE:
    REGEX_LIST = json.load(open(f'{site.getusersitepackages()}/mb_cli/regex.json'))
else:
    REGEX_LIST = json.load(open(f'{site.getsitepackages()[0]}/mb_cli/regex.json'))

MB_REFERRAL = os.environ.get('MB_REFERRAL')
