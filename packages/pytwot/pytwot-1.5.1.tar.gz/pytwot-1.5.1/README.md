<h2 align="center">pytwot</h2>
<p>This project is a fork of the now archived <a href="https://github.com/PyTweet/PyTweet">PyTweet</a></p>
<p><b>VERY IMPORTANT</b>: This project is approved by the PyTweet devs themselves.</p>
<p><b>Another note:</b> the support server given is support server for the original PyTweet as this is approved by the devs they requested the support server stay the same</p>

<div>
<img src="https://img.shields.io/pypi/v/pytwot?logo=pypi&style=plastic">  

<img src="https://img.shields.io/badge/code%20style-black-000000.svg">  


<img src="https://img.shields.io/github/commit-activity/m/sengolda/pytwot?color=turquoise&logo=github&logoColor=black">


<img src="https://img.shields.io/github/issues-pr/sengolda/pytwot?color=yellow&label=Pull%20Requests&logo=github&logoColor=black">


<img src="https://img.shields.io/discord/858312394236624957?color=blue&label=pytwot&logo=discord">


<img src='https://readthedocs.org/projects/pytwot/badge/?version=latest' alt='Documentation Status' />



</div>
<br>
<br>
<p align="center">pytwot is a synchronous Python API wrapper for the Twitter API. It is filled with rich features and is very easy to use.</p>

## Installation

### Windows

```bash
py -m pip install pytwot
```

### Linux/MacOS

```bash
python3 -m pip install pytwot
```

## Usage

Before using pytwot you have to setup an application [here](https://apps.twitter.com). For a more comfortable experience, you can create an application inside a project. Most endpoints require the client to have `read`, `write` and `direct_messages` app permissions and elevated access type. For more accessibility you can create a dev environment to support events and other premium endpoints. If you have any questions, please open an issue or ask in the official [pytwot Discord](https://discord.gg/nxZCE9EbVr).

```py
import pytwot

client = pytwot.Client(
    "Your Bearer Token Here!!!", 
    consumer_key="Your consumer key here", 
    consumer_secret="Your consumer secret here", 
    access_token="Your access token here", 
    access_token_secret="Your access token secret here",
) #Before using pytwot, make sure to create an application in https://apps.twitter.com.

client.tweet("Hello world, Hello twitter!") #This requires read & write app permissions also elevated access type.
```

You can check in the `examples` directory for more example code.

# Links

- [Documentation](https://pytwot.readthedocs.io/en/latest/)

- [Support Server](https://discord.gg/XHBhg6A4jJ)

- [GitHub](https://github.com/sengolda/pytwot)

- [PyPi](https://pypi.org/project/pytwot)

# Contribute

You can Contribute or open an issue regarding pytwot in our [GitHub repository](https://github.com/sengolda/pytwot)!

# Licence & Copyright

All files of this repo are protected and licensed with the [MIT License](https://opensource.org/licenses/MIT), [LICENSE File](LICENSE)
