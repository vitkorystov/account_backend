import requests
from time import sleep
import logging

logger = logging.getLogger('cron job for hold')
logger.setLevel(logging.INFO)
ch = logging.StreamHandler()
formatter = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)

"""скрипт запускается через крон каждые 10 минут для очистки холдов"""


def run():
    logger.info('start..')
    try:
        url = 'http://localhost:8000/api/accounts/'
        response = requests.get(url=url)
        unique_ids = [row['unique_id'] for row in response.json()]
        if unique_ids:
            for unique_id in unique_ids:
                data = {'unique_id': unique_id}
                url = 'http://localhost:8000/api/hold/'
                r = requests.put(url=url, data=data)
                logger.info(f'status_code: {r.status_code}')
                sleep(5)
        logger.info('hold operations done successfully')
    except Exception as ex:
        logger.exception(f'error: {ex}')
        sleep(10)


if __name__ == '__main__':
    run()
