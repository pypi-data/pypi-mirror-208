from enaml.qt.qt_application import QtApplication
import enaml
with enaml.imports():
    from .main_window import AggregationWindow


def main_aggregate():
    app = QtApplication()
    view = AggregationWindow()
    view.show()
    app.start()
    return True
