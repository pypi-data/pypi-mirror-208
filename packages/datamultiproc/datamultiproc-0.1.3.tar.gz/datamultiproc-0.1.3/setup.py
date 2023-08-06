# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['datamultiproc']

package_data = \
{'': ['*']}

install_requires = \
['PyYAML>=6.0,<7.0',
 'assertpy>=1.1,<2.0',
 'numpy>=1.24.3,<2.0.0',
 'pydantic-yaml>=0.11.2,<0.12.0',
 'pydantic>=1.10.7,<2.0.0',
 'pytest>=7.3.1,<8.0.0']

setup_kwargs = {
    'name': 'datamultiproc',
    'version': '0.1.3',
    'description': 'A Python multiprocessing library for data processing with pipelines.',
    'long_description': '# datamultiproc: A Python multiprocessing data pipeline library\n\nCreate Processors, compose them into pipelines and process your data using Python\'s \nmultiprocessing library. \n\n## Concepts\n\n### Sample\n\nA Sample is a data object that is passed through the pipeline.\nA custom sample can be simply implemented by inheriting from `BaseSample` and adding \nthe desired data fields. Note that an `def __init__(self, ...)` method is not required. \n\'BaseSample\' is build in top of Pydantics `BaseModel` and inherits its functionality.\nFor more information, see [Pydantic](https://docs.pydantic.dev/latest/).\n\nData fields can be of any type and also Optional. The latter is especially handy when they are filled \nduring the execution of the pipeline.\n\n```python\nimport numpy as np\nfrom datamultiproc import BaseSample\nfrom typing import Optional\n\n\nclass CustomSample(BaseSample):\n    data: int\n    optional_data: Optional[str] = None\n    array: np.ndarray\n```\n\n`BaseSample` has two special fields (`id` and `processing_history`). \nThe first has to be filled during instantiation of a `Sample`, the latter is appended to during execution\nof the pipeline, in order to keep track of all processing steps.\n\n```python\nclass BaseSample(Aggregate):\n    processing_history: List[Tuple[str, str]] = []\n    id: str\n```\n\n### Processor\n\nA `Processor` carries out an actual processing step on a `Sample`. \nTo implement a custom `Processor`, you simply inherit from the `Processor`class and implement the `process()` method.\n\n```python\n# Processor without arguments\nclass CustomProcessor(Processor):\n    def process(self, sample: Sample) -> Sample:\n        # do something with sample, e.g.\n        sample.data = sample.date + 1\n        return sample\n\n    \n# Processor with arguments\nclass CustomProcessor(Processor):\n    step_size: int\n    _hidden_arg: int = 1\n\n    def process(self, sample: Sample) -> Sample:\n        # do something with sample, e.g.\n        sample.data = sample.date + self.step_size + self._hidden_arg\n        return sample\n```\n\n\n### Compose\n\nCompose chains multiple `Processor` together. \nThey are executed in the order they are passed to the `Compose` constructor.\n\n```python\nprocess = Compose(\n    CustomProcessor(),\n    CustomProcessor(step_size=2),\n    CustomProcessor(step_size=3),\n)\n\nsamples = [...] # some list of samples\n\nprocessed_samples = [process(s) for s in samples]\n```\n\n\n### Cache and Save\n\n`Cache` and `Save` are special `Processors` that can be used to store intermediate results.\n`Cache` stores `Samples`after the processing step, that it is wrapped around as a \'.pickle\' file.\nThe files are stored inside a subfolder of the specified `save_to_dir` folder. \nThe subfolder is named after the "Processor" class.\nIf the pipeline is executed again, `Cache` will first check if the file already exists\nand if so, it will load the `Samples` from the file instead of executing the wrapped `Processor` again.\n\n`Save` works similarly, but does not load samples from file, if they already exist.\n\n`Cache` is especially useful for storing intermediate results, that are expensive to compute.\n`Save` is useful for storing the final results of a pipeline.\n\n```python\nprocess = Compose(\n    Cache(\n        processor=CustomProcessor(),\n        cache_dir="path/to/cache"\n    ),\n    CustomProcessor(step_size=2),\n    CustomProcessor(step_size=3),\n    Save(save_to_dir="path/to/save"),\n)\n```\n\n## Multiprocessing\n\nThe library can be used with Python\'s `multiprocessing` library, as follows.\nA full working example can be found in `example.py`.\n\n```python\nfrom multiprocessing import Process, Queue\n\n# number of processor cores of your machine\nNUM_PROCESSES = 8\n\n# list of samples\nsamples = [...]\n\nprocess = Compose([SomeProcessor(), \n                   AnotherProcessor(), \n                   Save(save_to_dir="path/to/save"),\n                   ])\n\n# put the samples into a multiprocessing Queue\nsamples_queue = Queue()\nfor s in samples:\n    samples_queue.put(s)\n    \n\ndef do_processing(process: Callable, queue: Queue):\n    while not queue.empty():\n        sample = queue.get()\n        try:\n            sample = process(sample)\n        except ProcessingError:\n            print(f"failed processing: {sample.id}")\n    \nprocesses = []\nfor _ in range(NUM_PROCESSES):\n    p = Process(target=do_processing, args=(process, samples_queue))\n    p.start()\n    processes.append(p)\n\nfor p in processes:\n    p.join()\n\n\n\n```\n',
    'author': 'Magnus Glasder',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/mglasder/datamultiproc',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
