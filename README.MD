# goodworker

Python bot that works hard

# Dependencies

Run `python3 -m pip install -r requirements.pip` from project folder

# Usage

Run as admin
`python3 goodworker.pyw`

Default shortcut to start session `ctrl + shift + < + >`

Shortcut to terminate program `ctrl + shift + k + l`

# Config

File with name `config` with no extension should be placed in project folder with following content:

```
{
"telegram": {
  "chat_id": <chat_id>,
  "token": "11111111:XXXXXXXXXXXXXXXXX-XXXXXXXXXXXXXXXXX"
},
"actions": [{
    "name" : "scroll",
    "frequency" : 20
    },
      {
      "name" : "click",
      "frequency" : 80
      }],
"notifications_every": 10,
"hotkeys": {
  "status_change": "s + t",
  "terminate": "k + l"
}
}
```

-   telegram (optional):
    -   `chat_id`
        -   format: `int`
        -   description: notifications will be sent to this chat
    -   `token`:
        -   description: can be obtained in @BotFather
-   actions (required at least one):
    -   format: Array of objects `{name: action_name, frequency: int}`
    -   supported actions are: `scroll`, `click`
    -   all specified actions should have total frequency of 100 (`int`)
        _Example: scroll 30 and click 70. 70% clicks and 30% scroll_
-   notifications_every:

    -   format: `int`
    -   description: how often to send notifications if telegram was configured

-   hotkeys (optional):
    -   status_change (optional):
        -   format: `string`
        -   description: custom hotkey can be specified in order to start /
            pause bot session.
    -   terminate (optional):
        -   format: `string`
        -   description: hotkey to terminate process completely.

# Compiling executable

Make sure that everything works by running the script before compiling.

[Pyinstaller](https://pyinstaller.readthedocs.io) can be used for compiling an executable.

```
pyinstaller -F -w \
    -n="NAME" \
    --add-data="emojies.txt:." \
    --add-data="code:." \
    -i=icon.icns \
    goodworker.pyw
```

_icon on mac should be in '.icns' format. '.ico' for Windows_
