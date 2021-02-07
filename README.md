# Simple Tic Tac Toe Discord Bot
This was just a project that I did in 3 hours, unlikely gonna get maintained.
It uses a JSON. So, it definitely doesn't scale.
You can alternatively use any db, preferably RDBMS.

<img src="http://storage.norizon.cloudns.asia/ss/2021-02-08_01-19-41.png">

This app uses [minimax](https://en.wikipedia.org/wiki/Minimax) algorithm
and is written with [discord.py](https://github.com/rapptz/discord.py) library to integrate with Discord API.

## Requirements
- A Discord application
- What's listed in requirements.txt
- Python 3.8+ (for backward compatibility, remove all walrus operators)
- A file named `config.json` in the root directory that contains `token` key

## Running
After having all the requirements, just run the main file.
```
# Unix
python3 main.py

# Windows
py -3 main.py
```

## Credits
This project uses Open Source components. You can find the source code
of their open source projects along with license information below.

- Repo: https://github.com/rapptz/RoboDanny \
  License (MPL-2.0) https://github.com/Rapptz/RoboDanny/blob/rewrite/LICENSE.txt
- Repo: https://github.com/Cledersonbc/tic-tac-toe-minimax \
  License (GPL-3.0) https://github.com/Cledersonbc/tic-tac-toe-minimax/blob/master/LICENSE
