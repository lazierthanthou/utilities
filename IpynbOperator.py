# Class IpynbOperator
import json, os
import nbformat
from nbconvert.preprocessors import ExecutePreprocessor
from nbconvert import HTMLExporter

class IpynbOperator:
	def __init__(self, blank_ipynb_file, pdf_creator='brave'):
		self.blank_ipynb_file = blank_ipynb_file

		if pdf_creator == 'brave':
			brave = os.path.join(os.sep, 'Applications', 'Brave\ Browser.app',
								 'Contents', 'MacOS', 'Brave\ Browser')
			if os.name == 'nt':
				brave = os.path.join('C:', os.sep, 'Program Files', 'BraveSoftware',
									 'Brave-Browser', 'Application', 'brave.exe')
			self.pdf_creator = brave
		return

	def ipynb_output_to_html(self, html_file_name):
		'''
		This function is equivalent to running the following 2 commands
			1. jupyter nbconvert --to notebook --inplace --execute <ipynb_file>
			2. jupyter nbconvert --to html --no-input  --allow-errors 
				--ExecutePreprocessor.timeout=-1 <ipynb_file> --output <html_file_name>
			There is one difference: this function doesn't create output in .ipynb file
				which the first jupyter nbconvert command does.
			References:
				 - https://nbconvert.readthedocs.io/en/latest/execute_api.html#module-nbconvert.preprocessors
				 - https://stackoverflow.com/questions/75896364/export-jupyter-notebook-to-html-while-running
		'''

		# read source notebook
		with open(self.blank_ipynb_file) as f:
			nb = nbformat.read(f, as_version=4)

		# execute notebook
		ep = ExecutePreprocessor(timeout=-1, kernel_name='python3')
		ep.preprocess(nb)

		# export to html
		html_exporter = HTMLExporter()
		html_exporter.exclude_input = True
		html_data, resources = html_exporter.from_notebook_node(nb)

		# write to output file
		with open(html_file_name, 'w', encoding='utf-8') as f:
			f.write(html_data)

		return

	def ipynb_to_html(self, source, html_file_name):
		self.edit_ipynb(source)
		self.ipynb_output_to_html(html_file_name)
		return

	def edit_ipynb(self, source):
		# read blank_ipynb_file as a json
		with open(self.blank_ipynb_file, 'r') as f:
			data = json.load(f)

		# find the first code cell and edit it with values from params
		for idx, cell in enumerate(data['cells']):
			if cell['cell_type'] == 'code':
				data['cells'][idx]['source'] = source
				break

		with open(self.blank_ipynb_file, 'w') as f:
			json.dump(data, f)
		return

	def html_to_pdf(self, html_file, pdf_file):
		'''
			Reference:
			https://peter.sh/experiments/chromium-command-line-switches/
		'''
		cmd = [
			self.pdf_creator, '--headless', '--enable-logging', f'--print-to-pdf="{pdf_file}"',
			'--disable-extensions',
			'--disable-popup-blocking', '--run-all-compositor-stages-before-draw',
			'--disable-checker-imaging', html_file,
		] #'--no-pdf-header-footer',

		ret_val = os.system(' '.join(cmd))
		return ret_val