# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['highrise']

package_data = \
{'': ['*']}

install_requires = \
['aiohttp>=3.8.4',
 'cattrs>=22.2.0,<23.0.0',
 'click>=8.1.3',
 'quattro>=22.1.0,<23.0.0']

entry_points = \
{'console_scripts': ['highrise = highrise.__main__:run']}

setup_kwargs = {
    'name': 'highrise-bot-sdk',
    'version': '23.1.0b10',
    'description': 'The Highrise Bot SDK, for running Highrise bots written in Python.',
    'long_description': "# The Highrise Python Bot SDK\n\n---\n\nThe Highrise Python Bot SDK is a python library for writing and running Highrise bots.\n\nFirst, install the library (preferably in a virtual environment):\n\n```shell\n$ pip install highrise-bot-sdk==23.1.0b10\n```\n\nIn the [`Settings` section of the Highrise website](https://highrise.game/account/settings), create a bot and generate the API token. You'll need the token to start your bot later.\nYou will also need a room ID for your bot to connect to; the room needs to be owned by you or your bot user needs to have designer rights to enter it.\n\nOpen a new file, and paste the following to get started (into `mybot.py` for example):\n\n```python\nfrom highrise import BaseBot\n\nclass Bot(BaseBot):\n    pass\n```\n\nOverride methods from `BaseBot` as needed.\n\nWhen you're ready, run the bot from the terminal using the SDK, giving it the Python path to the Bot class:\n\n```\n$ highrise mybot:Bot <room ID> <API token>\n```\n\n## Changelog\n\n### 23.1.0b10 (2023-05-12)\n\n-- Fix bug with handling of error responses.\n\n### 23.1.0b9 (2023-05-11)\n\n-- Add support for moving bot to an anchor in walk_to command (`self.highrise.walk_to(AnchorPosition)`).\n-- Change the way client ws messages are parsed, return error if message is not valid json.\n\n### 23.1.0b8 (2023-04-25)\n\n- Add support for moving users to another room (`self.highrise.move_user_to_room(user_id, room_id)`).\n- Add handler that is triggered when user moves inside a room  (`self.on_user_move(user_id, position)`).) \n- Expand session_metadata information with information about client rates\n- Expand session_metadata with information about sdk versions if client uses skd\n\n### 23.1.0b6 (2023-04-17)\n\n- Add Python 3.10 support\n\n### 23.1.0b5 (2023-04-11)\n\n- Add support for getting room permissions for users (`self.highrise.get_room_privilege(user_id)`).\n- Add support changing room permissions for users (`self.highrise.set_room_privilege(user_id, privilege)`).\n- Add support for moderating rooms (`self.highrise.moderate_room(user_id, moderate_action, action_length)`). \n- Rework how keepalive is handled\n\n### 23.1.0b4 (2023-04-05)\n\n- Methods mapping to requests with empty responses (`chat`, `send_whisper`, `send_emote`, `react`, `set_indicator`, `send_channel`, `walk_to`, `teleport`) now return `None`, and raise a `highrise.ResponseError` on an error response.\n- Fix the emote API.\n- Internally rework request handling to improve robustness.\n\n### 23.1.0b3 (2023-04-03)\n\n- Fix the chatting API.\n\n### 23.1.0b2 (2023-04-03)\n\n- Add support for receiving and sending reactions.\n- Fix support for hidden channels.\n- Migrate to the new message for avatars leaving.\n- Improve concurrency when awaiting bot methods.\n- Fix issues with teleporting users.\n- Fix issues with user coordinates.\n- Add support for fetching the bot wallet (`self.highrise.get_wallet()`).\n\n### 23.1.0b1 (2023-03-28)\n\n- Add support for emotes and hidden channel messages.\n\n### 23.1.0b0 (2023-03-10)\n\n- Initial beta release.\n",
    'author': 'Pocket Worlds Inc',
    'author_email': 'server@high.rs',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'None',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
