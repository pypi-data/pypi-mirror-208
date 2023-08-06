import PyQt5.QtWidgets as Qt
import PyQt5.QtGui as QtGui
import PyQt5.QtCore as QtCore
import logging

'''
The next two widgets (QTextEditLogger and LoggerTextArea) are used to create a textarea which also acts as handler for the logger objects created by the logging module
'''

class QTextEditLogger(logging.Handler):
#Code of this class was adapted from https://stackoverflow.com/questions/28655198/best-way-to-display-logs-in-pyqt
    def __init__(self, textwidget, basic_format):
        super().__init__()
        formatter = Formatter(fmt=basic_format)
        self.setFormatter(formatter)
        self.textwidget = textwidget

    def emit(self, record):
        msg = self.format(record)
        self.textwidget.appendHtml(msg)

class Formatter(logging.Formatter):
    COLORS = {logging.INFO: QtGui.QColor("black"),
              logging.ERROR: QtGui.QColor("red"),
              logging.WARNING: QtGui.QColor("orange")}

    #def formatException(self, ei):
    #    result = super(Formatter, self).formatException(ei)
    #    return result

    def __init__(self, fmt="%(levelno)d: %(msg)s"):
        logging.Formatter.__init__(self, fmt=fmt)

    def format(self, record):
        # Save the original format configured by the user
        # when the logger formatter was instantiated
        format_orig = self._style._fmt
        # Replace the original format with one customized by logging level
        for level in self.COLORS.keys():
            if record.levelno == level:
                self._style._fmt = "<font color=\"{}\">{}</font>".format(self.COLORS[level].name(),format_orig)
        # Call the original formatter class to do the grunt work
        result = super().format(record)
        # Restore the original format configured by the user
        self._style._fmt = format_orig
        return result

        #s = super(Formatter, self).format(record)
        #if record.exc_text:
        #    s = s.replace('\n', '')
        #return s

class LoggerTextArea(Qt.QWidget):
#Code of this class was adapted from https://stackoverflow.com/questions/28655198/best-way-to-display-logs-in-pyqt
    def __init__(self):
        super().__init__()

        self.widget = Qt.QPlainTextEdit()
        self.widget.setReadOnly(True)

        layout = Qt.QVBoxLayout()
        # Add the new logging box widget to the layout
        layout.addWidget(self.widget)
        self.setLayout(layout)
        self.widget.textChanged.connect(self.change_text)
        #self.ensureCursorVisible()

    def add_logger(self,logger):
        logTextBox = QTextEditLogger(self.widget, basic_format = logger.handlers[0].formatter._fmt)
        #if len(logger.handlers)>0:
        #    logTextBox.setFormatter(logger.handlers[0].formatter)
        logger.addHandler(logTextBox)

    def change_text(self):
        self.widget.verticalScrollBar().setValue(self.widget.verticalScrollBar().maximum())
