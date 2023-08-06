import sys

from rich.syntax import Syntax
from rich.traceback import Traceback

from textual import events
from textual.app import App, ComposeResult
from textual.containers import Container, VerticalScroll, Horizontal
from textual.reactive import var
from textual.widgets import DirectoryTree, Footer, Header, Static, RadioSet, RadioButton

from devblaze.textual_utils.constants import PROJECT_TYPE_OPTIONS


class BaseApp(App):
    CSS_PATH = "../static/test.css"

    def compose(self) -> ComposeResult:
        """Compose our UI."""
        yield Header()
        with Container():
            with Horizontal():
                with RadioSet():
                    RadioButton("django")
                    RadioButton("ddd", id="ddd")
        yield Footer()

    def on_mount(self, event: events.Mount) -> None:
        self.query_one(RadioSet).focus()

    def on_radio_set_change(self, event: RadioSet.Changed) -> None:
        """Called when the user clicks a radio button."""
        print(event.value)
        event.stop()

    def on_radio_set_submit(self, event: RadioButton.Changed) -> None:
        """Called when the user presses enter on a radio button."""
        print(event.value)
        event.stop()


if __name__ == "__main__":
    BaseApp().run()

