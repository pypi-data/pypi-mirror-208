# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['deprl',
 'deprl.env_wrappers',
 'deprl.utils',
 'deprl.vendor',
 'deprl.vendor.tonic',
 'deprl.vendor.tonic.agents',
 'deprl.vendor.tonic.environments',
 'deprl.vendor.tonic.explorations',
 'deprl.vendor.tonic.replays',
 'deprl.vendor.tonic.tensorflow',
 'deprl.vendor.tonic.tensorflow.agents',
 'deprl.vendor.tonic.tensorflow.models',
 'deprl.vendor.tonic.tensorflow.normalizers',
 'deprl.vendor.tonic.tensorflow.updaters',
 'deprl.vendor.tonic.torch',
 'deprl.vendor.tonic.torch.agents',
 'deprl.vendor.tonic.torch.models',
 'deprl.vendor.tonic.torch.normalizers',
 'deprl.vendor.tonic.torch.updaters',
 'deprl.vendor.tonic.utils']

package_data = \
{'': ['*'], 'deprl': ['param_files/*']}

install_requires = \
['gym==0.13.0',
 'jax>=0.4.8,<0.5.0',
 'jaxlib>=0.4.7,<0.5.0',
 'numpy>=1.22.4,<2.0.0',
 'pyyaml>=6.0,<7.0',
 'termcolor>=2.2.0,<3.0.0',
 'torch>=1.13.1']

entry_points = \
{'console_scripts': ['log = deprl.vendor.tonic.log:main']}

setup_kwargs = {
    'name': 'deprl',
    'version': '0.0.7',
    'description': 'DEP-RL, a method for robust control of musculoskeletal systems.',
    'long_description': '# DEP-RL: Embodied Exploration for Reinforcement Learning in Overactuated and Musculoskeletal Systems\n\n This repo contains the code for the paper [DEP-RL: Embodied Exploration for Reinforcement Learning in Overactuated and Musculoskeletal Systems](https://openreview.net/forum?id=C-xa_D3oTj6) paper, published at ICLR 2023 with perfect review scores (8, 8, 8, 10) and a notable-top-25% rating. See [here](https://sites.google.com/view/dep-rl) for videos.\n\nThe work was performed by Pierre Schumacher, Daniel F.B. Haeufle, Dieter Büchler, Syn Schmitt and Georg Martius.\n\nIf you just want to see the code for DEP, take a look at `deprl/dep_controller.py`, `deprl/custom_agents.py` and `deprl/env_wrapper/wrappers.py`\n\n<p align="center">\n<img src=https://user-images.githubusercontent.com/24903880/229783811-44c422e9-3cc3-42e4-b657-d21be9af6458.gif width=250>\n<img src=https://user-images.githubusercontent.com/24903880/229783729-d068e87c-cb0b-43c7-91d5-ff2ba836f05b.gif width=214>\n\n <img src=https://user-images.githubusercontent.com/24903880/229783370-ee95b9c3-06a0-4ef3-9b60-78e88c4eae38.gif width=214>\n</p>\n\n\n## Abstract\nMuscle-actuated organisms are capable of learning an unparalleled diversity of\ndexterous movements despite their vast amount of muscles. Reinforcement learning (RL) on large musculoskeletal models, however, has not been able to show\nsimilar performance. We conjecture that ineffective exploration in large overactuated action spaces is a key problem. This is supported by our finding that common\nexploration noise strategies are inadequate in synthetic examples of overactuated\nsystems. We identify differential extrinsic plasticity (DEP), a method from the\ndomain of self-organization, as being able to induce state-space covering exploration within seconds of interaction. By integrating DEP into RL, we achieve fast\nlearning of reaching and locomotion in musculoskeletal systems, outperforming\ncurrent approaches in all considered tasks in sample efficiency and robustness.\n\n\n## Installation\n\nWe provide a python package for easy installation:\n```\npip install deprl\n```\nIf you would like to use `jax` with CUDA support, which significantly speeds up learning, we recommend running:\n```\npip install --upgrade "jax[cuda12_pip]" -f https://storage.googleapis.com/jax-releases/jax_cuda_releases.html\n```\nor similar afterwards.\n\nThe humanreacher environment can be installed with\n```\npip install git+https://github.com/P-Schumacher/warmup.git\n```\n\nOstrichRL can be installed from [here](https://github.com/vittorione94/ostrichrl).\n\n\n## Experiments\n\nThe major experiments (humanreacher reaching and ostrich running) can be repeated with the config files.\nSimply run from the root folder:\n```\npython -m deprl.main experiments/ostrich_running_dep.json\npython -m deprl.main experiments/humanreacher.json\n```\nto train an agent. Model checkpoints will be saved in the `output` directory.\nThe progress can be monitored with:\n```\npython -m tonic.plot --path output/folder/\n```\n\nTo execute a trained policy, use:\n\n```\npython -m deprl.play --path output/folder/\n```\n\nSee the [TonicRL](https://github.com/fabiopardo/tonic) documentation for details.\n\nBe aware that ostrich training can be seed-dependant, as seen in the plots of the original publication.\n\n## Pure DEP\nIf you want to see pure DEP in action, just run the following bash files after installing the ostrichrl and warmup environments.\n```\nbash play_files/play_dep_humanreacher.sh\nbash play_files/play_dep_ostrich.sh\nbash play_files/play_dep_dmcontrol_quadruped.sh\n```\n\nYou might see a more interesting ostrich behavior by disabling episode resets in the ostrich environment first.\n## Environments\n\nThe ostrich environment can be found [here](https://github.com/vittorione94/ostrichrl) and is installed automatically via poetry.\n\nThe arm-environment [warmup](https://github.com/P-Schumacher/warmup) is also automatically installed by poetry and can be used like any other gym environment:\n\n```\nimport gym\nimport warmup\n\nenv = gym.make("humanreacher-v0")\n\nfor ep in range(5):\n     ep_steps = 0\n     state = env.reset()\n     while True:\n         next_state, reward, done, info = env.step(env.action_space.sample())\n         env.render()\n         if done or (ep_steps >= env.max_episode_steps):\n             break\n         ep_steps += 1\n\n```\n\nThe humanoid environments were simulated with [SCONE](https://scone.software/doku.php?id=start). A ready-to-use RL package will be released in cooperation with GOATSTREAM at a later date.\n\n## Source Code Installation\n\nWe recommend an installation with [poetry](https://python-poetry.org/) to ensure reproducibility.\nWhile [TonicRL](https://github.com/fabiopardo/tonic) with PyTorch is used for the RL algorithms, DEP itself is implemented in JAX. We *strongly* recommend GPU-usage to speed up the computation of DEP. On systems without GPUs, give the tensorflow version of TonicRL a try! We alternatively provide a pip_requirements file.\n1. Make sure to install poetry and deactivate all virtual environments.\n2. Clone the environment\n```\ngit clone https://github.com/martius-lab/depRL\n```\n\n3. Go to the root folder and run\n```\npoetry install\npoetry shell\n```\n\nThat\'s it!\n\nThe build has been tested with:\n```\nUbuntu 20.04 and Ubuntu 22.04\nCUDA 12.0\npoetry 1.4.0\n```\n### Troubleshooting\n* A common error with poetry is a faulty interaction with the python keyring, resulting in a `Failed to unlock the collection!`-error. It could also happen that the dependency solving takes very long (more than 60s), this is caused by the same error.\n  If it happens, try to append\n```\nexport PYTHON_KEYRING_BACKEND=keyring.backends.null.Keyring\n```\nto your bashrc. You can also try to prepend it to the poetry command: `PYTHON_KEYRING_BACKEND=keyring.backends.null.Keyring poetry install`.\n* If you have an error related to your `ptxas` version, this means that your cuda environment is not setup correctly and you should install the cuda-toolkit. The easiest way is to do this via conda if you don\'t have admin rights on your workstation.\n  I recommend running\n```\nconda install -c conda-forge cudatoolkit-dev\n```\n* In any other case, first try to delete the `poetry.lock` file and the virtual env `.venv`, then run `poetry install` again.\n\n\nFeel free to open an issue if you encounter any problems.\n\n## Citation\n\nPlease use the following citation if you make use of our work:\n\n```\n@inproceedings{schumacher2023:deprl,\n  title = {DEP-RL: Embodied Exploration for Reinforcement Learning in Overactuated and Musculoskeletal Systems},\n  author = {Schumacher, Pierre and Haeufle, Daniel F.B. and B{\\"u}chler, Dieter and Schmitt, Syn and Martius, Georg},\n  booktitle = {Proceedings of the Eleventh International Conference on Learning Representations (ICLR)},\n  month = may,\n  year = {2023},\n  doi = {},\n  url = {https://openreview.net/forum?id=C-xa_D3oTj6},\n  month_numeric = {5}\n}\n```\n',
    'author': 'Pierre Schumacher',
    'author_email': 'pierre.schumacher@tuebingen.mpg.de',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'None',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<3.11',
}


setup(**setup_kwargs)
