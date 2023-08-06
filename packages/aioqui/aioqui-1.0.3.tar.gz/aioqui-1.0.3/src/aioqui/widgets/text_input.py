from PySide6.QtWidgets import QTextEdit, QWidget, QSizePolicy

from ..objects import ContextObj


class TextInput(ContextObj, QTextEdit):
    def __init__(self, parent: QWidget, name: str, visible: bool = True):
        QTextEdit.__init__(self, parent)
        ContextObj.__init__(self, parent, name, visible)

    async def init(
            self, *,
            placeholder: str = '', text: str = '', textchanged: callable = None,
            policy: tuple[QSizePolicy, QSizePolicy] = None
    ) -> 'TextInput':
        self.setText(text)
        self.setPlaceholderText(placeholder)
        if textchanged:
            self.textChanged.connect(textchanged)
        if policy:
            self.setSizePolicy(*policy)
        return self
