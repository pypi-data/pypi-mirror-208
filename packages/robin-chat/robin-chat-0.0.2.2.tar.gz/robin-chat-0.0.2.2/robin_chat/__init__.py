import streamlit.components.v1 as components
import os
from typing import Optional, Union

try:
    from typing import Literal
except ImportError:
    from typing_extensions import Literal


_RELEASE = True
COMPONENT_NAME = "robin_chat"

# use the build instead of development if release is true
if _RELEASE:
    root_dir = os.path.dirname(os.path.abspath(__file__))
    build_dir = os.path.join(root_dir, "frontend/build")

    _robin_chat = components.declare_component(
        COMPONENT_NAME,
        path = build_dir
    )
else:
    _robin_chat = components.declare_component(
        COMPONENT_NAME,
        url = "http://localhost:3000"
    )


def message(message: str, 
            is_user: Optional[bool] = False, 
            key: Optional[str] = None):
    """
    Creates a new instance of streamlit-chat component

    Parameters
    ----------
    message: str
        The message to be displayed in the component
    is_user: bool 
        if the sender of the message is user, if `True` will align the 
        message to right, default is False.
    key: str or None
        An optional key that uniquely identifies this component. If this is
        None, and the component's arguments are changed, the component will
        be re-mounted in the Streamlit frontend and lose its current state.

    Returns: None
    """
    _robin_chat(message=message, isUser=is_user, key=key)


if not _RELEASE:
    import streamlit as st  

    if 'generated' not in st.session_state:
        st.session_state['generated'] = []

    if 'past' not in st.session_state:
        st.session_state['past'] = []

    user_input = input_text = st.text_input("You: ", key="input")

    if user_input:
        st.session_state.past.append(user_input)
        st.session_state.generated.append("I am still a robot")

    if st.session_state['generated']:

        for i in range(len(st.session_state['generated'])-1, -1, -1):
            message(st.session_state["generated"][i], key=str(i))
            message(st.session_state['past'][i], is_user=True, key=str(i) + '_user')


