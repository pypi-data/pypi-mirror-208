# ChatCMD #
#### **ChatCMD** is an AI-driven CLI-based command lookup using ChatGPT to lookup relevant CLI commands based on user input. ####

#### Boost Your Productivity, ***Say Goodbye*** to Manual Searches ####

## Features
- CLI-based command lookup using ChatGPT.
- Auto copy command to clipboard.
- Store Data in Sqlite Database.
- Add or update ChatGPT API key.
- Validate ChatGPT API key.
- Display ChatGPT API Key.
- Display last command.
- Display last {number} of commands.
- Delete last Command.
- Delete last {number} of commands.
- Display the total number of commands.
- Clear all history records.
- Display the database file size.
- Clear and validate user inputs.
- Clear and validate lookup results to ensure only valid CLI commands are returned.
- Error handling
- Display library information.

## Requirements
    Python >= 3.8.9
    OpenAI account and valid API key
    https://platform.openai.com/signup
## Installation
    python3 -m pip install chatcmd

    Collecting chatcmd
    Using cached chatcmd-1.0.14-py3-none-any.whl (6.8 kB)
    Installing collected packages: chatcmd
    Successfully installed chatcmd-1.0.14

### Uninstall ###
    python3 -m pip uninstall chatcmd
## Usage

```
Usage:

chatcmd [options]
  
Options:
  -k, --set-key                     set or update ChatGPT API key.
  -o, --get-key                     display ChatGPT API key.
  -g, --get-cmd                     display the last command.
  -G, --get-last=<value>            display the last [number] of commands.
  -d, --delete-cmd                  delete the last command.
  -D, --delete-last-cmd=<value>     delete the last [number] of commands.
  -t, --cmd-total                   display the total number of commands.
  -c, --clear-history               clear all history records.
  -s, --db-size                     display the database size.
  -h, --help                        display this screen.
  -v, --version                     display ChatCMD version.
  -i, --library-info                display library information.

```

## Screenshots
### Help screen: ###
<img src="https://github.com/naifalshaye/chatcmd/raw/master/chatcmd/images/help.png" alt="Help Screen" style="width:550px;"/>

### Library Info: ###
<img src="https://github.com/naifalshaye/chatcmd/raw/master/chatcmd/images/library-info.png" alt="Lookup Screen" style="width:500px;"/>

### Command Lookup screen: ###
<img src="https://github.com/naifalshaye/chatcmd/raw/master/chatcmd/images/lookup.png" alt="Lookup Screen" style="width:500px;"/>

## Error Codes
Include an exception message for each error if occurs.

| Code |             Description             |
|------|:-----------------------------------:|
| 1001 |          General exception          |
| 1002 |    Failed to connect to database    |
| 1003 | Failed to get API key from database |
| 1004 |      Failed to output API key       |
| 1005 | Failed to save API key to database  |
| 1006 |       Invalid ChatGPT API key       |
| 1007 |      Failed requesting API key      |
| 1008 |        Failed to add command        |
| 1009 |    API key is invalid or missing    |
| 1010 |      OpenAI API error occurred      |
| 1011 |      Lookup exception occurred      |
| 1012 |        Failed to add command        |
| 1013 |     Failed to get last command      |
| 1014 |    Failed to get list of command    |
| 1015 |    Failed deleting last command     |
| 1016 |     Failed to get last command      |
| 1017 |       Failed clearing history       |
| 1018 |       Failed to copy command        |

## Support
[New Issue](https://github.com/naifalshaye/chatcmd/issues/new)\
[naif@naif.io](mailto:naif@naif.io)

Developed by: [Naif Alshaye](https://naif.io)
## License
The MIT License (MIT). Please see License File [MIT License](https://choosealicense.com/licenses/mit/) for more information.