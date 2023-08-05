# PyTorch-NLP-chatbot
NLP and its uses in creating an intelligent responsive chatbot to interact with users.

![Apache Liscence](https://img.shields.io/github/license/KoroIsCoding/PyTorch-NLP-chatbot)![Issue](https://img.shields.io/github/issues/KoroIsCoding/PyTorch-NLP-chatbot)



## Overview
`PyTorch-NLP-chatbot` is a Python library for user to easily build their own chatbot based on their interest and focus.

Users can create chatbot with different fields and improve the accuracy by NLP algorithm.


## Python Search Engine Library

This Python library is a simple implementation of a search engine using the Google Search API. This library was developed by Koro_Is_Coding and is licensed under Apache v2.0.

### Prerequisites

Before you begin, ensure you have met the following requirements:

- You have a `Windows/Linux/Mac` machine running Python 3.6+.
- You have installed the `requests`, and `scikit-learn` libraries.

### Installation

1. Clone this repository on your local machine:

```bash
git clone https://github.com/KoroIsCoding/PyTorch-NLP-chatbot
```

2. Navigate to the cloned repository:

```bash
cd PyTorch-NLP-chatbot
```

3. Install the required dependencies:

```bash
pip install requests scikit-learn
```

### Using the Search Engine Library

The `SearchEngineStruct` class is the main class for the search engine. It requires a Google API key and a Google Engine key for initialization. 

Here's a simple usage example:

```python
from search_engine import SearchEngineStruct

# Initialize the search engine
search_engine = SearchEngineStruct(google_api_key='YOUR_API_KEY', google_engine_key='YOUR_ENGINE_KEY')

# Define your query
search_engine.query = 'Your search query'

# Run the search engine (this is a simplified example, actual implementation may require more steps)
search_engine.run()
```

Please replace `'YOUR_API_KEY'` and `'YOUR_ENGINE_KEY'` with your actual Google API key and Google Engine key respectively.

### Contributing

If you want to contribute to this library, please check out the `CONTRIBUTING.md` file.

### License

This project uses the following license: [Apache v2.0](https://apache.org/licenses/LICENSE-2.0).
