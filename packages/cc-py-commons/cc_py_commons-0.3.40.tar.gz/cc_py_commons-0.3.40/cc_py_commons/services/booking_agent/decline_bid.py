import requests

from cc_py_commons.utils.logger import logger
from .constants import BOOKING_AGENT_TOKEN, BOOKING_AGENT_URL


def execute(bid_id):
  url = f"{BOOKING_AGENT_URL}/quote/-/bid/{bid_id}/decline"
  token = f"Bearer {BOOKING_AGENT_TOKEN}"
  headers = {
    "Authorization": token
  }

  logger.debug(f"Declining bid {bid_id} in booking-agent: {url}, {headers}")
  response = requests.post(url, headers=headers)

  if response.status_code == 200:
    logger.debug(f"Successfully declined the bid: {bid_id}")
  else:
    logger.warning(f'Failed to decline bid {response.status_code}:{response.text}')

  return response
