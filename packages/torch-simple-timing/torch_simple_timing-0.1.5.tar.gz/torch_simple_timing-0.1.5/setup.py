# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['torch_simple_timing']

package_data = \
{'': ['*']}

install_requires = \
['torch>=1.11']

setup_kwargs = {
    'name': 'torch-simple-timing',
    'version': '0.1.5',
    'description': 'A simple package to time CPU/GPU/Multi-GPU ops',
    'long_description': '<p align="center">\n<strong><a href="https://github.com/vict0rsch/torch_simple_timing" target="_blank">💻&nbsp;&nbsp;Code</a></strong>\n<strong>&nbsp;&nbsp;•&nbsp;&nbsp;</strong>\n<strong><a href="https://torch-simple-timing.readthedocs.io/" target="_blank">Docs&nbsp;&nbsp;📑</a></strong>\n</p>\n\n<p align="center">\n    <a>\n\t    <img src=\'https://img.shields.io/badge/python-3.8%2B-blue\' alt=\'Python\' />\n\t</a>\n\t<a href=\'https://torch-simple-timing.readthedocs.io/en/latest/?badge=latest\'>\n    \t<img src=\'https://readthedocs.org/projects/torch-simple-timing/badge/?version=latest\' alt=\'Documentation Status\' />\n\t</a>\n    <a href="https://github.com/psf/black">\n\t    <img src=\'https://img.shields.io/badge/code%20style-black-black\' />\n\t</a>\n    <a href="https://pytorch.org">\n        <img src="https://img.shields.io/badge/PyTorch-%23EE4C2C.svg?logo=PyTorch&logoColor=white"/>\n    </a>\n    <a href="https://pypi.org/project/torch-simple-timing/">\n        <img src="https://badge.fury.io/py/torch_simple_timing.svg" alt="PyPI version" height="20">\n    </a>\n</p>\n<br/>\n\n\n# Torch Simple Timing\n\nA simple yet versatile package to time CPU/GPU/Multi-GPU ops.\n\n1. "*I want to time operations once*"\n   1. That\'s what a `Clock` is for\n2. "*I want to time the same operations multiple times*"\n   1. That\'s what a `Timer` is for\n\nIn simple terms:\n\n* A `Clock` is an object (and context-manager) that will compute the ellapsed time between its `start()` (or `__enter__`) and `stop()` (or `__exit__`)\n* A `Timer` will internally manage clocks so that you can focus on readability and not data structures\n\n## Installation\n\n```\npip install torch_simple_timing\n```\n\n## How to use\n\n### A `Clock`\n\n```python\nfrom torch_simple_parsing import Clock\nimport torch\n\nt = torch.rand(2000, 2000)\ngpu = torch.cuda.is_available()\n\nwith Clock(gpu=gpu) as context_clock:\n    torch.inverse(t @ t.T)\n\nclock = Clock(gpu=gpu).start()\ntorch.inverse(t @ t.T)\nclock.stop()\n\nprint(context_clock.duration) # 0.29688501358032227\nprint(clock.duration)         # 0.292896032333374\n```\n\nMore examples, including bout how to easily share data structures using a `store` can be found in the [documentation](https://torch-simple-timing.readthedocs.io/en/latest/autoapi/torch_simple_timing/clock/index.html).\n\n### A `Timer`\n\n```python\nfrom torch_simple_timing import Timer\nimport torch\n\ndevice = torch.device("cuda" if torch.cuda.is_available() else "cpu")\n\nX = torch.rand(5000, 5000, device=device)\nY = torch.rand(5000, 100, device=device)\nmodel = torch.nn.Linear(5000, 100).to(device)\noptimizer = torch.optim.Adam(model.parameters())\n\ngpu = device.type == "cuda"\ntimer = Timer(gpu=gpu)\n\nfor epoch in range(10):\n    timer.clock("epoch").start()\n    for b in range(50):\n        x = X[b*100: (b+1)*100]\n        y = Y[b*100: (b+1)*100]\n        optimizer.zero_grad()\n        with timer.clock("forward", ignore=epoch>0):\n            p = model(x)\n        loss = torch.nn.functional.cross_entropy(p, y)\n        with timer.clock("backward", ignore=epoch>0):\n            loss.backward()\n        optimizer.step()\n    timer.clock("epoch").stop()\n\nstats = timer.stats()\n# use stats for display and/or logging\n# wandb.summary.update(stats)\nprint(timer.display(stats=stats, precision=5))\n```\n\n```\nepoch    : 0.25064 ± 0.02728 (n=10)\nforward  : 0.00226 ± 0.00526 (n=50)\nbackward : 0.00209 ± 0.00387 (n=50)\n```\n\n### A decorator\n\nYou can also use a decorator to time functions without much overhead in your code:\n\n```python\nfrom torch_simple_timing import timeit, get_global_timer, reset_global_timer\nimport torch\n\n# Use the function name as the timer name\n@timeit(gpu=True)\ndef train():\n    x = torch.rand(1000, 1000, device="cuda" if torch.cuda.is_available() else "cpu")\n    return torch.inverse(x @ x)\n\n# Use a custom name\n@timeit("test")\ndef test_cpu():\n    return torch.inverse(torch.rand(1000, 1000) @ torch.rand(1000, 1000))\n\nif __name__ == "__main__":\n    for _ in range((epochs := 10)):\n        train()\n\n    test_cpu()\n\n    timer = get_global_timer()\n    print(timer.display())\n\n    reset_global_timer()\n```\n\nPrints:\n\n```text\ntrain : 0.045 ± 0.007 (n=10)\ntest  : 0.046         (n= 1)\n```\n\nBy default the `@timeit` decodrator takes at least a `name`, will use `gpu=False` and use the global timer (`torch_simple_timing.TIMER`). You can pass your own timer with `@timeit(name, timer=timer)`.\n\nSee [in the docs]([https://](https://torch-simple-timing.readthedocs.io/en/latest/autoapi/torch_simple_timing/index.html)).\n',
    'author': 'vict0rsch',
    'author_email': 'vsch@pm.me',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'None',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8.1,<4.0.0',
}


setup(**setup_kwargs)
