from textual.app import App, ComposeResult

from feathers.widgets import Help


class DemoApp(App):
    def compose(self) -> ComposeResult:
        yield Help()
