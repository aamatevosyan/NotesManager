import logging
import sys

import jsonpickle
import qdarkstyle
from PyQt5.QtCore import QObject, pyqtSignal, Qt
from PyQt5.QtWidgets import QApplication, QMessageBox

from notes.ui.MainWindow import MainWindow

# basic logger functionality
log = logging.getLogger(__name__)
handler = logging.StreamHandler(stream=sys.stdout)
log.addHandler(handler)


def show_exception_box(log_msg):
    """Checks if a QApplication instance is available and shows a messagebox with the exception message.
    If unavailable (non-console application), log an additional notice.
    """
    if QApplication.instance() is not None:
        errorbox = QMessageBox()
        errorbox.setIcon(QMessageBox.Critical)
        errorbox.setWindowFlags(Qt.Dialog | Qt.CustomizeWindowHint | Qt.WindowTitleHint | Qt.WindowCloseButtonHint)
        errorbox.setWindowTitle("Error!!!")
        errorbox.setText("Oops. An unexpected error occured:\n{0}".format(log_msg))
        errorbox.exec_()
    else:
        log.debug("No QApplication instance available.")


class UncaughtHook(QObject):
    _exception_caught = pyqtSignal(object)

    def __init__(self, *args, **kwargs):
        super(UncaughtHook, self).__init__(*args, **kwargs)

        # this registers the exception_hook() function as hook with the Python interpreter
        sys.excepthook = self.exception_hook

        # connect signal to execute the message box function always on main thread
        self._exception_caught.connect(show_exception_box)

    def exception_hook(self, exc_type, exc_value, exc_traceback):
        """Function handling uncaught exceptions.
        It is triggered each time an uncaught exception occurs.
        """
        if issubclass(exc_type, KeyboardInterrupt):
            # ignore keyboard interrupt to support console applications
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
        else:
            exc_info = (exc_type, exc_value, exc_traceback)
            log_msg = '\n'.join([  # ''.join(traceback.format_tb(exc_traceback)),
                '{0}: {1}'.format(exc_type.__name__, exc_value)])
            log.critical("Uncaught exception:\n {0}".format(log_msg), exc_info=exc_info)

            # trigger message box show
            self._exception_caught.emit(log_msg)


def main():
    qt_exception_hook = UncaughtHook()

    app = QApplication(sys.argv)

    window = MainWindow(None)

    app_settings_path = "app_settings.json"

    with open(app_settings_path, "r") as f:
        app_settings = jsonpickle.decode(f.read())

    if app_settings["app_theme"] == "dark":
        app.setStyleSheet(qdarkstyle.load_stylesheet(qt_api='pyqt5'))

    window.show()

    app.exec_()


if __name__ == "__main__":
    jsonpickle.set_encoder_options('json', sort_keys=True, indent=4)
    main()
