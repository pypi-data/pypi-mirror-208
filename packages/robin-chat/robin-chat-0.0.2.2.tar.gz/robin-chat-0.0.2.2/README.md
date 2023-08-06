# robin-chat

Custom streamlit component. Prototype use only.

## Installation

Install `robin-chat` with pip
```bash
pip install robin-chat 
```

usage, import the `message` function from `robin_chat`
```py
import streamlit as st
from robin_chat import message

message("Hey I'm Robin copilot, how can I help?") 
message("Hello Robin!", is_user=True)  # align's the message to the right
```
