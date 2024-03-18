import requests, base64
import json

class Github_Reader():
	def __init__(self, owner, repo, token):
		self.owner = owner
		self.repo = repo
		self._headers = {
			"Authorization": f'Bearer {token}',
			"Accept": "application/vnd.github.v3+json"
		}
		return

	def set_repo(self, owner, repo):
		self.owner = owner
		self.repo = repo
		return

	def get_file(self, file_path):
		url = f'https://api.github.com/repos/{self.owner}/{self.repo}/contents/{file_path}'
		response = requests.get(url, headers=self._headers)

		if response.status_code == 200:
			file_content = response.json()['content']
			file_content = base64.b64decode(file_content).decode('utf-8')
			return file_content
		else:
			print("Error:", response.status_code)
			return ''

	def get_raw_file(self, file_path):
		url = f'https://raw.githubusercontent.com/{self.owner}/{self.repo}/main/{file_path}'
		response = requests.get(url, headers=self._headers)

		if response.status_code == 200:
			file_content = response.text
			return file_content
		else:
			print("Error:", response.status_code)
			return ''
