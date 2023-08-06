# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['langchain_visualizer',
 'langchain_visualizer.agents',
 'langchain_visualizer.chains',
 'langchain_visualizer.embeddings',
 'langchain_visualizer.llms',
 'langchain_visualizer.prompts']

package_data = \
{'': ['*']}

install_requires = \
['gorilla>=0.4.0,<0.5.0', 'langchain>=0.0.161,<0.1', 'ought-ice>=0.5.0,<0.6.0']

setup_kwargs = {
    'name': 'langchain-visualizer',
    'version': '0.0.22',
    'description': 'Visualization and debugging tool for LangChain workflows',
    'long_description': '# LangChain Visualizer\n\nAdapts [ICE](https://github.com/oughtinc/ice) for use with [LangChain](https://github.com/hwchase17/langchain) so that you can view LangChain interactions with a beautiful UI.\n\n![Screenshot of an execution run](screenshots/serp_screenshot.png "SERP agent demonstration")\n\nYou can now\n\n- See the full prompt text being sent with every interaction with the LLM\n- Tell from the coloring which parts of the prompt are hardcoded and which parts are templated substitutions\n- Inspect the execution flow and observe when each function goes up the stack\n- See the costs of each LLM call, and of the entire run, if you are using OpenAI\'s `text-davinci-003` model\n\n## Quickstart\n\nInstall this library:\n\n```bash\npip install langchain-visualizer\n```\n\nThen:\n\n1. Add `import langchain_visualizer` as **the first import** in your Python entrypoint file\n2. Write an async function to visualize whichever workflow you\'re running\n3. Call `langchain_visualizer.visualize` on that function\n\nFor an example, see below instructions on reproducing the screenshot.\n\n\n### Running the example screenshot\n\nTo run the example you see in the screenshot, first install this library and optional dependencies:\n\n```bash\npip install langchain-visualizer google-search-results openai\n```\n\nIf you haven\'t yet set up your [OpenAI API keys](https://openai.com/api/) or SERP API keys, you can [replay the recorded interactions](https://github.com/amosjyng/vcr-langchain) by cloning this repository and running\n\n```bash\npython tests/agents/test_langchain_getting_started.py\n```\n\nIf you have set them up, you can run the following script (adapted from [LangChain docs](https://langchain.readthedocs.io/en/latest/modules/agents/getting_started.html)):\n\n```python\nimport langchain_visualizer\nimport asyncio\nfrom langchain.agents import initialize_agent, load_tools\nfrom langchain.llms import OpenAI\n\nllm = OpenAI(temperature=0.7)\ntools = load_tools(["serpapi", "llm-math"], llm=llm)\nagent = initialize_agent(tools, llm, agent="zero-shot-react-description", verbose=True)\nasync def search_agent_demo():\n    return agent.run(\n        "Who is Olivia Wilde\'s boyfriend? What is his current age raised to the 0.23 "\n        "power?"\n    )\n\nlangchain_visualizer.visualize(search_agent_demo)\n```\n\nA browser window will open up, and you can actually see the agent execute happen in real-time!\n\n### Jupyter notebook support\n\nJupyter notebooks are now supported! To use this inside a Jupyter notebook, **make sure to import the `visualize` function from `langchain_visualizer.jupyter` instead.**\n\nPlease look at [the demo notebook](/tests/demo.ipynb) to see an example of how it can be used in Jupyter.\n\n### Visualizing embeddings\n\nIf you want to also visualize documents being chunked up for embeddings, you can now do so by calling the `visualize_embeddings` function before you visualize the main chain:\n\n```python\nfrom langchain_visualizer import visualize, visualize_embeddings\n\nasync def run_chain():\n    ...\n\nvisualize_embeddings()\nvisualize(run_chain)\n```\n\n## Why not just use LangChain\'s built-in tracer?\n\nFor me personally:\n\n- I prefer the ICE UI. In particular:\n    - I like the colored highlighting of parts of the prompt that are filled-in template variables\n    - I like the ability to quickly inspect different LLM calls without leaving the trace page\n- I prefer the visualization of my agent logic to remain static when LLM calls are cached\n- I prefer seeing when the tool (e.g. `PythonREPL`) actually gets called, rather than just the high-level execution of the chain (e.g. `LLMMathChain`)\n\nThat being said, LangChain\'s tracer is definitely better supported. **Please note that there is a lot of langchain functionality that I haven\'t gotten around to hijacking for visualization.** If there\'s anything you need to show up in the execution trace, please open a PR or issue.\n\n## My other projects\n\nPlease check out [VCR LangChain](https://github.com/amosjyng/vcr-langchain), a library that lets you record LLM interactions for your tests and demos!\n',
    'author': 'Amos Jun-yeung Ng',
    'author_email': 'me@amos.ng',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'None',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
