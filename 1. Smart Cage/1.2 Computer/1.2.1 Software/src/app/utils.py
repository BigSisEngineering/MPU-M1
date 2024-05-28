from abc import ABC, abstractmethod
import streamlit as st

# ------------------------------------------------------------------------------------------------ #
from src import app
from src import setup


class Page(ABC):
    @abstractmethod
    def write(self):
        pass

    def update(self):
        pass


def main_display(func):
    def inner1(*args, **kwargs):
        # ====================================== Tab config ====================================== #
        page_tittle: str = "BigSis" if setup.CAGE_ID is None else f"BigSis {setup.CAGE_ID}"
        st.set_page_config(
            page_title=page_tittle,
            page_icon="🐝",
            layout="wide",
        )

        func(*args, **kwargs)

    return inner1
