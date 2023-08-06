# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['text_generation']

package_data = \
{'': ['*']}

install_requires = \
['aiohttp>=3.8,<4.0', 'huggingface-hub>=0.12,<1.0', 'pydantic>=1.10,<2.0']

setup_kwargs = {
    'name': 'text-generation',
    'version': '0.5.2',
    'description': 'Hugging Face Text Generation Python Client',
    'long_description': '# Text Generation\n\nThe Hugging Face Text Generation Python library provides a convenient way of interfacing with a\n`text-generation-inference` instance running on\n[Hugging Face Inference Endpoints](https://huggingface.co/inference-endpoints) or on the Hugging Face Hub.\n\n## Get Started\n\n### Install\n\n```shell\npip install text-generation\n```\n\n### Inference API Usage\n\n```python\nfrom text_generation import InferenceAPIClient\n\nclient = InferenceAPIClient("bigscience/bloomz")\ntext = client.generate("Why is the sky blue?").generated_text\nprint(text)\n# \' Rayleigh scattering\'\n\n# Token Streaming\ntext = ""\nfor response in client.generate_stream("Why is the sky blue?"):\n    if not response.token.special:\n        text += response.token.text\n\nprint(text)\n# \' Rayleigh scattering\'\n```\n\nor with the asynchronous client:\n\n```python\nfrom text_generation import InferenceAPIAsyncClient\n\nclient = InferenceAPIAsyncClient("bigscience/bloomz")\nresponse = await client.generate("Why is the sky blue?")\nprint(response.generated_text)\n# \' Rayleigh scattering\'\n\n# Token Streaming\ntext = ""\nasync for response in client.generate_stream("Why is the sky blue?"):\n    if not response.token.special:\n        text += response.token.text\n\nprint(text)\n# \' Rayleigh scattering\'\n```\n\nCheck all currently deployed models on the Huggingface Inference API with `Text Generation` support:\n\n```python\nfrom text_generation.inference_api import deployed_models\n\nprint(deployed_models())\n```\n\n### Hugging Face Inference Endpoint usage\n\n```python\nfrom text_generation import Client\n\nendpoint_url = "https://YOUR_ENDPOINT.endpoints.huggingface.cloud"\n\nclient = Client(endpoint_url)\ntext = client.generate("Why is the sky blue?").generated_text\nprint(text)\n# \' Rayleigh scattering\'\n\n# Token Streaming\ntext = ""\nfor response in client.generate_stream("Why is the sky blue?"):\n    if not response.token.special:\n        text += response.token.text\n\nprint(text)\n# \' Rayleigh scattering\'\n```\n\nor with the asynchronous client:\n\n```python\nfrom text_generation import AsyncClient\n\nendpoint_url = "https://YOUR_ENDPOINT.endpoints.huggingface.cloud"\n\nclient = AsyncClient(endpoint_url)\nresponse = await client.generate("Why is the sky blue?")\nprint(response.generated_text)\n# \' Rayleigh scattering\'\n\n# Token Streaming\ntext = ""\nasync for response in client.generate_stream("Why is the sky blue?"):\n    if not response.token.special:\n        text += response.token.text\n\nprint(text)\n# \' Rayleigh scattering\'\n```\n\n### Types\n\n```python\n# Prompt tokens\nclass PrefillToken:\n    # Token ID from the model tokenizer\n    id: int\n    # Token text\n    text: str\n    # Logprob\n    # Optional since the logprob of the first token cannot be computed\n    logprob: Optional[float]\n\n\n# Generated tokens\nclass Token:\n    # Token ID from the model tokenizer\n    id: int\n    # Token text\n    text: str\n    # Logprob\n    logprob: float\n    # Is the token a special token\n    # Can be used to ignore tokens when concatenating\n    special: bool\n\n\n# Generation finish reason\nclass FinishReason(Enum):\n    # number of generated tokens == `max_new_tokens`\n    Length = "length"\n    # the model generated its end of sequence token\n    EndOfSequenceToken = "eos_token"\n    # the model generated a text included in `stop_sequences`\n    StopSequence = "stop_sequence"\n\n\n# Additional sequences when using the `best_of` parameter\nclass BestOfSequence:\n    # Generated text\n    generated_text: str\n    # Generation finish reason\n    finish_reason: FinishReason\n    # Number of generated tokens\n    generated_tokens: int\n    # Sampling seed if sampling was activated\n    seed: Optional[int]\n    # Prompt tokens\n    prefill: List[PrefillToken]\n    # Generated tokens\n    tokens: List[Token]\n\n\n# `generate` details\nclass Details:\n    # Generation finish reason\n    finish_reason: FinishReason\n    # Number of generated tokens\n    generated_tokens: int\n    # Sampling seed if sampling was activated\n    seed: Optional[int]\n    # Prompt tokens\n    prefill: List[PrefillToken]\n    # Generated tokens\n    tokens: List[Token]\n    # Additional sequences when using the `best_of` parameter\n    best_of_sequences: Optional[List[BestOfSequence]]\n\n\n# `generate` return value\nclass Response:\n    # Generated text\n    generated_text: str\n    # Generation details\n    details: Details\n\n\n# `generate_stream` details\nclass StreamDetails:\n    # Generation finish reason\n    finish_reason: FinishReason\n    # Number of generated tokens\n    generated_tokens: int\n    # Sampling seed if sampling was activated\n    seed: Optional[int]\n\n\n# `generate_stream` return value\nclass StreamResponse:\n    # Generated token\n    token: Token\n    # Complete generated text\n    # Only available when the generation is finished\n    generated_text: Optional[str]\n    # Generation details\n    # Only available when the generation is finished\n    details: Optional[StreamDetails]\n\n# Inference API currently deployed model\nclass DeployedModel:\n    model_id: str\n    sha: str\n```',
    'author': 'Olivier Dehaene',
    'author_email': 'olivier@huggingface.co',
    'maintainer': 'Olivier Dehaene',
    'maintainer_email': 'olivier@huggingface.co',
    'url': 'https://github.com/huggingface/text-generation-inference',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
