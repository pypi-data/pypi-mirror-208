from PySide6.QtWidgets import QFileDialog, QWidget
from PySide6.QtGui import QDesktopServices
from PySide6.QtCore import QUrl
import tempfile
import os


async def select_dir(
        parent: QWidget = None,
        caption: str = 'Select directory',
        directory: str = '.'
) -> str | None:
    dialog = QFileDialog(parent, caption, directory)
    dialog.setOption(QFileDialog.Option.ShowDirsOnly)
    return dialog.getExistingDirectory()


async def explore_dir(directory: str):
    if os.path.isdir(directory):
        os.startfile(directory)


async def select_file(
        parent: QWidget = None,
        caption: str = 'Select file',
        directory: str = '.',
        filters: str = ''
) -> str | None:
    dialog = QFileDialog(parent, caption, directory, filters)
    dialog.setFileMode(QFileDialog.FileMode.ExistingFile)
    if dialog.exec():
        return dialog.selectedFiles()[0]


async def explore_file(

):
    ...


async def explore_bytes(
    filename: str, extension: str, bytes: bytes
) -> None:
    file = tempfile.NamedTemporaryFile(prefix=filename, suffix=extension, delete=True)
    file.write(eval(bytes))
    file.close()
    QDesktopServices.openUrl(QUrl('file:///' + file.name))
