import os
import requests as rq
import logging
import sentry_sdk

import time
from dotenv import load_dotenv

sentry_sdk.init("https://112f0bcd65ad40ad938a287a0d4ff8b9@o335977.ingest.sentry.io/5250334")

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

IS_HEROKU = os.environ.get('IS_HEROKU', False)
if IS_HEROKU:
    print('HEROKU IS  DETECTED ')
else:
    print('HEROKU IS NOT DETECTED. LOAD ENVIRONMENT FROM .ENV ')
    load_dotenv()
