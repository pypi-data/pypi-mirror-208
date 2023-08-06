import os
import shutil
import sys
from pathlib import Path

from PySide6.QtGui import QAction
from PySide6.QtWidgets import QMainWindow, QMessageBox, QInputDialog

from je_editor.pyside_ui.shell_process.shell_exec import shell_manager


def set_venv_menu(ui_we_want_to_set: QMainWindow):
    # Create an venv
    ui_we_want_to_set.venv_menu.create_venv_action = QAction("Create Venv")
    ui_we_want_to_set.venv_menu.create_venv_action.setShortcut(
        "Ctrl+v"
    )
    ui_we_want_to_set.venv_menu.create_venv_action.triggered.connect(
        lambda: create_venv(ui_we_want_to_set)
    )
    ui_we_want_to_set.venv_menu.addAction(ui_we_want_to_set.venv_menu.create_venv_action)
    # PIP a package
    ui_we_want_to_set.venv_menu.pip_action = QAction("pip package")
    ui_we_want_to_set.venv_menu.pip_action.setShortcut(
        "Ctrl+p"
    )
    ui_we_want_to_set.venv_menu.pip_action.triggered.connect(
        lambda: pip_install_package(ui_we_want_to_set)
    )
    ui_we_want_to_set.venv_menu.addAction(ui_we_want_to_set.venv_menu.pip_action)


def create_venv(ui_we_want_to_set: QMainWindow):
    venv_path = Path(os.getcwd() + "/venv")
    if not venv_path.exists():
        shell_manager.exec_shell("python -m virtualenv venv")
        print("Creating venv please waiting for shell exit code.")
    else:
        message_box = QMessageBox()
        message_box.setText("venv already exists.")
        message_box.exec()


def pip_install_package(ui_we_want_to_set: QMainWindow):
    venv_path = Path(os.getcwd() + "/venv")
    if not venv_path.exists():
        message_box = QMessageBox()
        message_box.setText("Please create venv first.")
        message_box.exec()
    else:
        ask_package_dialog = QInputDialog()
        package_text, press_ok = ask_package_dialog.getText(
            ui_we_want_to_set, "Install Package", "What Package you want to install"
        )
        if press_ok:
            if sys.platform in ["win32", "cygwin", "msys"]:
                venv_path = Path(os.getcwd() + "/venv/Scripts")
            else:
                venv_path = Path(os.getcwd() + "/venv/bin")
            if venv_path.is_dir() and venv_path.exists():
                compiler_path = shutil.which(
                    cmd="python3",
                    path=str(venv_path)
                )
            else:
                compiler_path = shutil.which(cmd="python3")
            if compiler_path is None:
                compiler_path = shutil.which(
                    cmd="python",
                    path=str(venv_path)
                )
            else:
                compiler_path = shutil.which(cmd="python")
            shell_manager.exec_shell(f"{compiler_path} -m pip install {package_text}")
