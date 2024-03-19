import requests, base64
import json

class Github_Reader():
	def __init__(self, owner, repo, token):
		self.owner = owner
		self.repo = repo
		self._headers = {
			"Authorization": f'Bearer {token}',
			#"Accept": "application/vnd.github.v3+json"
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

	def download_file(self, file_path_in_repo, save_file_name, raw=True):
		url = f'https://raw.githubusercontent.com/{self.owner}/{self.repo}/main/{file_path_in_repo}'
		response = requests.get(url, headers=self._headers)

		if response.status_code == 200:
			if raw:
				save_mode = 'wb'
				file_content = response.content
			else:
				save_mode = 'w'
				file_content = response.text

			with open(save_file_name, save_mode) as f:
				f.write(file_content)
			return None
		else:
			error = f'Error: {response.status_code}'
			print(error)
			return error
