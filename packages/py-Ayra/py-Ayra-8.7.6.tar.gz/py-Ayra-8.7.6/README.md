# py-Ultroid Library

Core library of [The Ultroid](https://github.com/naya1503/Ayra), a python based telegram userbot.

[![CodeFactor](https://www.codefactor.io/repository/github/naya1503/pyayra/badge)](https://www.codefactor.io/repository/github/naya1503/pyayra)
[![PyPI - Version](https://img.shields.io/pypi/v/py-Ultroid?style=round)](https://pypi.org/project/py-Ultroid)    
[![PyPI - Downloads](https://img.shields.io/pypi/dm/py-Ultroid?label=DOWNLOADS&style=round)](https://pypi.org/project/py-Ultroid)    
[![Maintenance](https://img.shields.io/badge/Maintained%3F-yes-green.svg)](https://github.com/naya1503/Ayra/graphs/commit-activity)
[![Open Source Love svg2](https://badges.frapsoft.com/os/v2/open-source.svg?v=103)](https://github.com/naya1503/Ayra)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg?style=flat-square)](https://makeapullrequest.com)

# Installation
```bash
pip3 install -U py-Ayra
```

# Documentation 
[![Documentation](https://img.shields.io/badge/Documentation-Ayrq-blue)](http://ayra.tech/)

# Usage
- Create folders named `plugins`, `addons`, `assistant` and `resources`.   
- Add your plugins in the `plugins` folder and others accordingly.   
- Create a `.env` file with following mandatory Environment Variables
   ```
   API_ID
   API_HASH
   SESSION
   MONGO_URI
   ```
- Check
[`.env.sample`](https://github.com/naya1503/Ayra/blob/main/.env.sample) for more details.   
- Run `python3 -m Ayra` to start the bot.   

## Creating plugins
 - ### To work everywhere

```python
@ultroid_cmd(
    pattern="start"
)   
async def _(e):   
    await e.eor("Ayra Started!")   
```

- ### To work only in groups

```python
@ultroid_cmd(
    pattern="start",
    groups_only=True,
)   
async def _(e):   
    await eor(e, "Ayra Started.")   
```

- ### Assistant Plugins 👇

```python
@asst_cmd("start")   
async def _(e):   
    await e.reply("Ayra Started.")   
```

See more working plugins on [the offical repository](https://github.com/naya1503/Ayra)!

> Made with 💕 by [Kynan](https://t.me/Rizzvbss).    


# License
[![License](https://www.gnu.org/graphics/agplv3-155x51.png)](LICENSE)   
Ultroid is licensed under [GNU Affero General Public License](https://www.gnu.org/licenses/agpl-3.0.en.html) v3 or later.

# Credits
* [![Kynan-Devs](https://img.shields.io/static/v1?label=Kynan&message=devs&color=critical)](https://t.me/Rizzvbss)
* [Lonami](https://github.com/Lonami) for [Telethon](https://github.com/LonamiWebs/Telethon)
