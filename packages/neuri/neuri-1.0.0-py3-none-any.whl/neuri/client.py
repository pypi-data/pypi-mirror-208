import os
import json
import requests
from .exceptions import InvalidConfigException, InvalidDataTypeException, FileNotFoundException

AVAILABLE_SERVICES = [
	'transcribe',
	"textcat",
	"translate",
	"textcat-ner",
	"full",
	"full-translate"
]
AVAILABLE_LANGS = [
	'en',
	'es'
]


def initialize_client(config):
	if not isinstance(config, dict):
		raise InvalidConfigException(
			f'The config ({config}) must be a dictionary.')
	return Client(config)

class Client:
	"""
		This is the main class of the client. It is used to initialize the client and to make requests to the server.
		The client can be initialized with a config file or with a dictionary.

		The config file must be a json file with the following structure:
			{
				service: str,
				lang: str,
				temperature: float,
				api_key: str
			}

		Parameters:
			config (dict): A dictionary with the configuration of the client.

		Attributes:
			api_key (str): The api key of the client.
			service (str): The service requested.
			lang (str): The language of the audio input.
			temperature (float): grade of confidence of the model.
			p (pyaudio.PyAudio): The pyaudio object.
			stream (pyaudio.Stream): The pyaudio stream.
			URL (str): The url of the server.

		methods:
			realtime: This method is used to make a request to the server with a realtime audio input.
			audio_file: This method is used to make a request to the server with an audio file.
			audio_url: This method is used to make a request to the server with an audio url.
			text: This method is used to make a request to the server with a text input.
	"""

	def __init__(self, config):

		self.translate_to = ""
		if config['service'] not in AVAILABLE_SERVICES:
			raise InvalidConfigException(
				f'The service ({config["service"]}) requested is not available.')

		if config['lang'] not in AVAILABLE_LANGS:
			raise InvalidConfigException(
				f'The language ({config["lang"]}) requested is not available.')

		if not isinstance(config['temperature'], float):
			raise InvalidConfigException(
				f'The temperature ({config["temperature"]}) must be a float.')

		if config['temperature'] < 0 or config['temperature'] > 1:
			raise InvalidConfigException(
				f'The temperature ({config["temperature"]}) must be between 0 and 1.')

		if 'translate_to' in config:
			if config['translate_to'] not in AVAILABLE_LANGS:
				raise InvalidConfigException(
					f'The language ({config["translate_to"]}) requested is not available.')
			self.translate_to = config['translate_to']

		self.api_key = config['api_key']
		self.service = config['service']
		self.lang = config['lang']
		self.temperature = config['temperature']

	def __validate_file_type(self, dato) -> bool:
		if not isinstance(dato, str) and not isinstance(dato, list):
			raise InvalidDataTypeException(f"The data type ({type(dato)}) is not valid.")

	def audio_file(self, file_path, service=None) -> dict:
		"""Validate the audio file path and make a request to the server.

		Args:
				file_path (str | list): The path of the audio file or a list of paths.
				service (_type_, optional): The service requested. Defaults to None.

		Returns:
				dict: The response of the server.
		"""
		self.__URL = f"https://api.neuri.ai/api/v1/service/audio/batch?lang={self.lang}&service={service if service else self.service}&temperature={self.temperature}&translate_to={self.translate_to}"

		# validate filetype path
		if self.__validate_file_type(file_path):
			raise InvalidDataTypeException(f'The file path ({file_path}) must be a string.')

		# if filepath is a string check if the file exists otherwise if it is a list check if all the files exists
		if isinstance(file_path, str):
			if not os.path.isfile(file_path):
				raise FileNotFoundException(f'The file ({file_path}) does not exists.')
		else:
			for file in file_path:
				if not os.path.isfile(file):
					raise FileNotFoundException(f'The file ({file}) does not exists.')

		#! send request to the server
		headers = {
			'Authorization': f'Bearer {self.api_key}'
		}

		files = []
		if isinstance(file_path, str):
			files.append(
				('files', (file_path.split('/')[-1], open(file_path, 'rb'), 'audio/wav')))
		else:
			for file in file_path:
				files.append(
					('files', (file.split('/')[-1], open(file, 'rb'), 'audio/wav')))

		headers = {
			'Authorization': 'Bearer s21FZ-ffdMbqfY3EAS6-vKOrHLI52dnZPw'
		}
		response = requests.request(
			"POST", self.__URL, headers=headers, files=files)
		try:
			return json.loads(response.text)
		except Exception as e:
			return "Something went wrong. Please try again later."

	def audio_url(self, url, service=None) -> dict:
		self.__URL = f"https://api.neuri.ai/api/v1/service/audio/batch_url"
		params = {
			"service": service if service else self.service,
			"translate_to": self.translate_to,
			"lang": self.lang,
			"temperature": self.temperature,
			"url": []
		}

		if self.__validate_file_type(url):
			raise InvalidDataTypeException(f'The file path ({url}) must be a string.')

		# if list check if all elements are strings
		if isinstance(url, list):
			for element in url:
				if not isinstance(element, str):
					raise InvalidDataTypeException(f'The element ({element}) must be a string.')

		# send request to the server
		headers = {
			'Content-Type': 'application/json',
			'Authorization': f'Bearer {self.api_key}'
		}

		params['url'] = url

		response = requests.request(
			"POST", self.__URL, headers=headers, data=json.dumps(params))

		try:
			return json.loads(response.text)
		except Exception as e:
			return "Something went wrong. Please try again later."

	def text(self, text, service=None) -> dict:
		self.__URL = f"https://api.neuri.ai/api/v1/service/text/"
		params = {
			"service": service if service else self.service,
			"translate_to": self.translate_to,
			"lang": self.lang,
			"temperature": self.temperature,
		}

		if self.__validate_file_type(text):
			raise InvalidDataTypeException(f'The file path ({text}) must be a string.')

		# if list merge all elements in a single string
		if isinstance(text, list):
			text = " ".join(text)

		params['text'] = text

		headers = {
			'Content-Type': 'application/json',
			'Authorization': f'Bearer {self.api_key}'
		}

		response = requests.request(
			"POST", self.__URL, headers=headers, data=json.dumps(params))
		try:
			return json.loads(response.text)
		except Exception as e:
			return "Something went wrong. Please try again later."

