import requests

from cc_py_commons.utils.logger import logger
from .constants import C4_API_AUTH_TOKEN, C4_API_URL


def execute(account_id, integration_type):
	url = f"{C4_API_URL}/integrations"
	token = f"Bearer {C4_API_AUTH_TOKEN}"
	headers = {
		"Authorization": token
	}
	params = {
		'accountId': account_id,
		'integrationType': integration_type
	}
	response = requests.get(url, headers=headers, params=params)

	if response.status_code != 200:
		logger.warning(f"Request to get account integration failed with status code: "
									 f"{response.status_code}")
		return None

	json = response.json()

	if json['code'] != 200:
		logger.warning(f"notifications: Unable to find {integration_type} integration for account Id: {account_id}")
		return False

	return json
