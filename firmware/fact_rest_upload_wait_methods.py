import json
import time
from urllib.parse import quote
import os
import hashlib

import requests

TARGET_HOST = 'http://localhost:5000'
UPLOAD_TIMEOUT = 30  # Wait after upload before starting to poll if finished
POLL_TIMEOUT = 60
KEY = ''  # Leave the api key empty if not needed
PLUGINS = {
	'cpu_architecture', 'crypto_material', 'cve_lookup', 'device_tree', 'elf_analysis', 'exploit_mitigations',
	'hardware_analysis', 'information_leaks', 'interesting_uris', 'ip_and_uri_finder', 'kernel_config', 'known_vulnerabilities',
	'printable_strings', 'software_components', 'users_and_passwords'
} # change based on your needs. This is my default set.
META_PATH = '/home/user/PycharmProjects/FWScraper/scraper/output/'

def create_url(web_path):
	return f'{TARGET_HOST}{web_path}'

def check_progress(uid: str) -> bool:
	# Check if currently running analysis is finished
	response = requests.get(f'{TARGET_HOST}/rest/status')
	status = response.json()
	recently_finished = status["system_status"]["backend"]["analysis"]["recently_finished_analyses"]
	current_analyses = status["system_status"]["backend"]["analysis"]["current_analyses"]
	return uid in recently_finished or current_analyses == {}

def upload_firmware(upload_dict: dict) -> str:
	response = requests.put(f'{TARGET_HOST}/rest/firmware', json=upload_dict).json()
	try:
		return response['uid']
	except KeyError:
		print(f'[ERROR]\t{response}')
		exit(1)

def read_meta_data() -> list[tuple[str, dict]]:
	fact_upload_data = []

	for filename in os.listdir(META_PATH):
		if filename.endswith(".json"):
			json_path = os.path.join(META_PATH, filename)
			with open(json_path, "r") as file:
				json_data = json.load(file)
				binary_bytes = json_data['binary'].encode("utf-8")
				file_sha = hashlib.sha256(binary_bytes).hexdigest()
				fact_upload_data.append(
						(
						f'{file_sha}_{len(binary_bytes)}',  # That's your FACT UID
						json_data
						)
					)				
	return fact_upload_data


def analysis_already_done(uid: str) -> bool:
	return requests.get(create_url(f'/rest/firmware/{uid}')).status_code == 200


def main():
	counter = 1
	try:
		file_id = None
		firmware = read_meta_data()
		print(f'Transfering {len(firmware)} firmware images')
		for file_id, meta in firmware:
			if analysis_already_done(file_id):  # handy if you cancel the script and continue later (or if some error occurs)
				print(f'[{counter}/{len(firmware)}]\t Skipped analysis of {file_id}. Already present.')
				counter += 1
				continue
			uid = upload_firmware(meta)
			print(f'[{counter}/{len(firmware)}]\t Started analysis of {uid}')
			counter += 1
			time.sleep(UPLOAD_TIMEOUT)
			while not check_progress(uid):
				time.sleep(POLL_TIMEOUT)
	except requests.exceptions.ConnectionError:
		print('Connection failed. Is host up?')
	except json.decoder.JSONDecodeError as e:
		print(e)
		print(f'Bad response from host, check for authentication and proxy.\nid={file_id}')
	return 0

if __name__ == '__main__':
	exit(main())
