==============
Python Client Library for Neuri
==============

This is the official Python client library for Neuri. It allows you to easily integrate Neuri into your Python applications.

++++++++++++
Installation
++++++++++++

To get started with the Neuri Python Client Library, you need to first install the library using pip:

.. code-block:: python

  pip install neuri

+++++
Import and initialize the library
+++++

First you have to import the module and set up the client with your API key and service details, as shown below.
.. code-block:: python

    import neuri

    config = {
        "service": "translate",
        "lang": "en",
        "temperature": 0.5,
        "api_key": "YOUR_API_KEY_HERE",
        "translate_to": "es" # optional
    }

    client = neuri.initialize_client(config)

+++++
Import and initialize the library
+++++

The Neuri Client Library currently supports three services: **audio_file**, **audio_url**, and **text**. Each service has its own set of parameters and returns a JSON containing the results of the processing.

* **neuri.audio_file()**: Audio File.
* **neuri.audio_url()**: Audio URL.
* **neuri.text()**: Text

+++++
Audio File
+++++
Process audio files stored locally on your system using the audio_file service.

.. code-block:: python

    result = client.audio_file(file_path=[
        os.path.join(os.path.dirname(__file__), "examples/girl_phone_call.wav"),
        os.path.join(os.path.dirname(__file__), "examples/noise_man_question.wav")
    ])

Replace the file paths in the file_path list with the actual paths to your audio files. The audio_file service will process the audio files and return the results in a JSON format.

+++++
Audio URL
+++++

Process audio files from a remote URL using the **audio_url** service.

.. code-block:: python

    result = client.audio_url(url="https://neuri-storage.s3.amazonaws.com/public_data/girl_phone_call.wav?AWSAccessKeyId=AKIAQFECGXRQOTIJ2FUV&Signature=GjrMz1NkMtQgFd0etJUCiQg4WNI%3D&Expires=1995267608")

Replace the file paths in the url list with the actual paths to your audio files. The audio_url service will process the audio files and return the results in a JSON format.

+++++
Text
+++++
Process text using the text service.

.. code-block:: python

    result = client.text(text="Hello, how are you?")

Replace the text in the text parameter with the actual text you want to process. The text service will process the text and return the results in a JSON format.