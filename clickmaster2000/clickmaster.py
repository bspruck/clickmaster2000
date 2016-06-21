#!/usr/bin/env python
# -*- coding: utf-8 -*-
# clickmaster: click things, get counts!
# Copyright(c) 2016 by wave++ "Yuri D'Elia" <wavexx@thregr.org>
from __future__ import print_function, division, generators, unicode_literals, absolute_import

import io, os, sys
import argparse
import math
from PyQt4 import QtCore, QtGui, uic

if hasattr(sys, '_MEIPASS'):
    RC_PATH = sys._MEIPASS
else:
    RC_PATH = os.path.dirname(__file__)

APP_NAME = "ClickMaster2000"
APP_DESC = "A tally counter for images"
APP_HELP = open(os.path.join(RC_PATH, 'clickmaster.html')).read()
APP_URL = 'https://www.thregr.org/~wavexx/software/clickmaster2000/'
APP_VER = '1.0'


if sys.version_info.major < 3:
    # Python 2.7 shim
    str = unicode
else:
    basestring = str
    file = io.FileIO


def load_ui(obj, file):
    cwd = os.getcwd()
    try:
        # chdir to the "ui" directory to preserve icon paths
        os.chdir(RC_PATH)

        # setup the form and attach it to obj
        form, _ = uic.loadUiType(file)
        ret = form()
        ret.setupUi(obj)
    finally:
        # switch back
        os.chdir(cwd)
    return ret



class CtrlWidget(QtGui.QWidget):
    colorChanged = QtCore.pyqtSignal(int, QtGui.QColor)
    countReset = QtCore.pyqtSignal(int)
    setCurrent = QtCore.pyqtSignal(int)

    def __init__(self, idx, color):
        super(QtGui.QWidget, self).__init__()
        self.idx = idx
        layout = QtGui.QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self.setMaximumWidth(250)
        self._color = color
        self._check = QtGui.QRadioButton()
        self._check.setToolTip("Select color {}".format(idx + 1))
        self._check.clicked.connect(lambda x: self.setCurrent.emit(self.idx))
        self._ccnt = QtGui.QToolButton()
        self._ccnt.setMinimumWidth(50)
        self._ccnt.setToolTip("Change color {}".format(idx + 1))
        self._ccnt.clicked.connect(self._on_ccnt)
        self._reset = QtGui.QToolButton()
        self._reset.setIcon(self.style().standardIcon(QtGui.QStyle.SP_DialogCancelButton))
        self._reset.setToolTip("Clear color {}".format(idx + 1))
        self._reset.clicked.connect(self._on_reset)
        layout.addWidget(self._check)
        layout.addWidget(self._ccnt)
        layout.addWidget(self._reset)
        self.setLayout(layout)
        self.reset()

    def _on_ccnt(self, ev):
        color = QtGui.QColorDialog.getColor(self._color, self)
        if color.isValid():
            self._color = color
            self._update()
            self.colorChanged.emit(self.idx, self._color)

    def _on_reset(self, ev):
        self.reset()
        self.countReset.emit(self.idx)

    def reset(self):
        self._count = 0
        self._update()

    def incr(self):
        self._count += 1
        self._update()

    def decr(self):
        self._count -= 1
        self._update()

    def count(self):
        return self._count

    def color(self):
        return self._color

    def setChecked(self, value):
        self._check.setChecked(value)

    def _update(self):
        self._ccnt.setText("{:4}".format(self._count))
        bg = self._color.name()
        if QtGui.qGray(self._color.rgb()) >= 127:
            fg = "#000000"
        else:
            fg = "#FFFFFF"
        self._ccnt.setStyleSheet('QToolButton {{ font-family: Consolas, monospace; font-weight: bold;'
                                 'background-color: {}; color: {}; }}'.format(bg, fg))


class QInvertedGraphicsLineItem(QtGui.QGraphicsLineItem):
    def __init__(self, *args, **kwargs):
        super(QInvertedGraphicsLineItem, self).__init__(*args, **kwargs)

    def paint(self, painter, *args, **kwargs):
        painter.setCompositionMode(QtGui.QPainter.CompositionMode_Xor)
        super(QInvertedGraphicsLineItem, self).paint(painter, *args, **kwargs)
        painter.setCompositionMode(QtGui.QPainter.CompositionMode_Clear)


class QInvertedGraphicsRectItem(QtGui.QGraphicsRectItem):
    def __init__(self, *args, **kwargs):
        super(QInvertedGraphicsRectItem, self).__init__(*args, **kwargs)

    def paint(self, painter, *args, **kwargs):
        painter.setCompositionMode(QtGui.QPainter.CompositionMode_Xor)
        super(QInvertedGraphicsRectItem, self).paint(painter, *args, **kwargs)


# main application
class MainWindow(QtGui.QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self._ui = load_ui(self, "clickmaster.ui")

        # signals and events
        self._ui.actionOpen.triggered.connect(self.on_load)
        self._ui.actionClear.triggered.connect(self.on_clear)
        self._ui.actionHelp.triggered.connect(self.on_help)
        self._ui.actionGrid.triggered.connect(self.on_grid)
        self._ui.view.wheelEvent = self.on_wheel
        self._ui.view.mousePressEvent = self.on_press
        self._ui.view.mouseReleaseEvent = self.on_release
        self._ui.view.mouseMoveEvent = self.on_move
        self._ui.view.keyPressEvent = self.on_key

        # grid size
        self._gridSlider = QtGui.QSlider(QtCore.Qt.Horizontal)
        self._gridSlider.setMaximumWidth(200)
        self._gridSlider.setToolTip('Grid size')
        self._gridSlider.valueChanged.connect(self.on_grid_size)
        self._ui.toolBar.insertWidget(None, self._gridSlider)

        # point sizes
        self._ui.toolBar.insertSeparator(None)
        self._sizeSlider = QtGui.QSlider(QtCore.Qt.Horizontal)
        self._sizeSlider.setRange(10, 100)
        self._sizeSlider.setMaximumWidth(200)
        self._sizeSlider.setToolTip('Point size')
        self._size = 25
        self._sizeSlider.setValue(self._size)
        self._sizeSlider.valueChanged.connect(self.resize_points)
        self._ui.toolBar.insertWidget(None, self._sizeSlider)

        # counts
        self._counts = []
        self._ui.toolBar.insertSeparator(None)
        count = CtrlWidget(0, QtGui.QColor("red"))
        self._counts.append(count)
        self._ui.toolBar.insertWidget(None, count)
        self._ui.toolBar.insertSeparator(None)
        count = CtrlWidget(1, QtGui.QColor("blue"))
        self._counts.append(count)
        self._ui.toolBar.insertWidget(None, count)
        self._points = [set() for _ in range(len(self._counts))]
        for count in self._counts:
            count.setCurrent.connect(self.set_current)
            count.countReset.connect(self.count_reset)
            count.colorChanged.connect(self.color_changed)

        # scene
        self._scene = QtGui.QGraphicsScene(self)
        self._scene_pixmap = self._scene.createItemGroup([])
        self._scene_grid = self._scene.createItemGroup([])
        self._scene_points = self._scene.createItemGroup([])
        self._ui.view.setScene(self._scene)

        # initial state
        self._pixmap = None
        self._size = None
        self._gridSize = None
        self.set_current(0)
        self.reset()


    def reset(self):
        self._dragged = False
        self._last_pos = None
        self._last_btn = None
        self.clear()
        for child in self._scene_pixmap.childItems():
            self._scene.removeItem(child)


    def count_reset(self, pset):
        for point in self._points[pset]:
            self._scene.removeItem(point)
        self._points[pset].clear()
        self.update_grid()


    def color_changed(self, pset, color):
        for point in self._points[pset]:
            point.setBrush(QtGui.QBrush(color))
            point.setPen(QtGui.QPen(color))


    def _generate_grid(self):
        step = self._gridSize
        width = self._pixmap.width()
        height = self._pixmap.height()
        scale = self._ui.view.mapToScene(width, 0).x() / width
        border = scale * 10
        for x in range(1, width // step + 1):
            item = QInvertedGraphicsLineItem(x * step, 0, x * step, height, self._scene_grid)
            item.setPen(QtGui.QColor(255, 255, 255, 127))
        for y in range(1, height // step + 1):
            item = QInvertedGraphicsLineItem(0, y * step, width, y * step, self._scene_grid)
            item.setPen(QtGui.QColor(255, 255, 255, 127))
        for x in range(0, width // step + 1):
            for y in range(0, height // step + 1):
                rect = QtCore.QRectF(x * step, y * step, step, step)
                if rect.x() + rect.width() > width:
                    rect.setWidth(width % step)
                if rect.y() + rect.height() > height:
                    rect.setHeight(height % step)
                if rect.width() < border or rect.height() < border * 2:
                    continue
                empty = True
                found = self._scene.items(rect)
                for item in found:
                    for pset in self._points:
                        if item in pset and rect.contains(item.pos()):
                            empty = False
                            break
                if empty:
                    rect = QtCore.QRectF(rect.x() + border / 2, rect.y() + border / 2,
                                         rect.width() - border, rect.height() - border)
                    item = QInvertedGraphicsRectItem(rect, self._scene_grid)
                    item.setPen(QtGui.QPen(QtGui.QColor(255, 255, 255, 25), border))


    def update_grid(self):
        for child in self._scene_grid.childItems():
            self._scene.removeItem(child)
        visible = self._ui.actionGrid.isChecked()
        if visible and self._pixmap is not None:
            self._generate_grid()
        self._scene_grid.setVisible(visible)


    def on_grid(self, ev):
        self.update_grid()


    def clear(self):
        for count in self._counts:
            count.reset()
        for pset in range(len(self._points)):
            self.count_reset(pset)


    def load_pixmap(self, pixmap):
        self.reset()
        self._pixmap = pixmap
        self._scene.setSceneRect(-pixmap.width() / 2, -pixmap.height() / 2,
                                 pixmap.width() * 2, pixmap.height() * 2)
        QtGui.QGraphicsPixmapItem(pixmap, self._scene_pixmap)
        self._ui.view.fitInView(0, 0, pixmap.width(), pixmap.height(),
                                mode=QtCore.Qt.KeepAspectRatio)
        initial = self._gridSize is None
        self._gridSlider.setRange(min(pixmap.width(), pixmap.width() // 20),
                                  max(pixmap.width(), pixmap.height()) // 2)
        self._sizeSlider.setRange(min(pixmap.width(), pixmap.width() // 200),
                                  max(pixmap.width(), pixmap.height()) // 10)
        if initial:
            self._gridSlider.setValue(pixmap.width() // 5)
            self._sizeSlider.setValue(pixmap.width() // 100)
        self.update_grid()


    def on_wheel(self, ev):
        scale = ev.delta() / 100.
        if scale < 0:
            scale = 1. / -scale
        if ev.modifiers() & QtCore.Qt.ControlModifier:
            new_size = self._size * scale
            new_size = min(self._sizeSlider.maximum(), max(self._sizeSlider.minimum(), new_size))
            self._sizeSlider.setValue(new_size)
        elif ev.modifiers() & QtCore.Qt.ShiftModifier:
            new_size = self._gridSize * scale
            new_size = min(self._gridSlider.maximum(), max(self._gridSlider.minimum(), new_size))
            self._gridSlider.setValue(new_size)
        else:
            sp = self._ui.view.mapToScene(QtCore.QPoint(ev.x(), ev.y()))
            cp = self._ui.view.mapToScene(QtCore.QPoint(self._ui.view.width() // 2,
                                                        self._ui.view.height() // 2))
            self._ui.view.scale(scale, scale)
            self._ui.view.centerOn(cp + (sp - cp) / 4 * math.copysign(1, ev.delta()))
            self.update_grid()


    def on_press(self, ev):
        self._dragged = False
        self._last_pos = (ev.globalPos().x(), ev.globalPos().y())
        self._last_btn = ev.button()


    def on_key(self, ev):
        if ev.text() in [str(x + 1) for x in range(len(self._counts))]:
            ev.accept()
            self.set_current(int(ev.text()) - 1)
        elif ev.text() == 'x':
            ev.accept()
            self.set_current((self._current + 1) % len(self._counts))
        elif ev.text() == 'o':
            ev.accept()
            self.on_load()
        elif ev.text() == 'g':
            ev.accept()
            self._ui.actionGrid.trigger()
        elif ev.text() == '?':
            ev.accept()
            self.on_help()
        elif ev.key() == QtCore.Qt.Key_C:
            ev.accept()
            clipboard = QtGui.QApplication.instance().clipboard()
            clipboard.setText(str(self._counts[self._current].count()))


    def _add_point(self, sx, sy):
        point = QtGui.QGraphicsEllipseItem(-self._size / 2, -self._size / 2,
                                           self._size, self._size,
                                           scene=self._scene)
        point.setPos(sx, sy)
        color = QtGui.QColor(self._counts[self._current].color())
        color.setAlphaF(0.7)
        point.setBrush(QtGui.QBrush(color))
        point.setPen(QtGui.QPen(color))
        self._points[self._current].add(point)
        self._counts[self._current].incr()
        self.update_grid()


    def _delete_point(self, pset, item):
        self._counts[pset].decr()
        self._points[pset].remove(item)
        self._scene.removeItem(item)
        self.update_grid()


    def _find_point(self, sx, sy):
        found = self._scene.items(
            QtCore.QRectF(sx - self._size / 2, sy - self._size / 2,
                          self._size, self._size))
        for item in found:
            for i, pset in enumerate(self._points):
                if item in pset:
                    dist = math.sqrt((sx - item.x()) ** 2 + (sy - item.y()) ** 2)
                    if dist < self._size / 2:
                        return i, item
        return None


    def set_current(self, current):
        self._current = current
        for pset, count in enumerate(self._counts):
            count.setChecked(pset == self._current)


    def on_release(self, ev):
        if self._dragged or self._pixmap is None: return
        sp = self._ui.view.mapToScene(QtCore.QPoint(ev.x(), ev.y()))
        ex = self._find_point(sp.x(), sp.y())
        if ev.button() == 1:
            if ex is not None or \
               not (0 <= sp.x() < self._pixmap.width()) or \
               not (0 <= sp.y() < self._pixmap.height()):
                QtGui.QApplication.beep()
            else:
                self._add_point(sp.x(), sp.y())
        elif ev.button() == 2 and ex is not None:
            self._delete_point(ex[0], ex[1])


    def on_move(self, ev):
        if self._last_pos is not None and self._last_btn == 2:
            dx = ev.globalPos().x() - self._last_pos[0]
            dy = ev.globalPos().y() - self._last_pos[1]
            if not self._dragged and (abs(dx) > 5 or abs(dy) > 5):
                self._dragged = True
            if self._dragged:
                sx = self._ui.view.horizontalScrollBar().value()
                sy = self._ui.view.verticalScrollBar().value()
                self._ui.view.horizontalScrollBar().setValue(sx - dx)
                self._ui.view.verticalScrollBar().setValue(sy - dy)
                self._last_pos = (ev.globalPos().x(), ev.globalPos().y())


    def resize_points(self, size):
        self._size = size
        for pset in self._points:
            for point in pset:
                point.setRect(-size / 2, -size / 2, size, size)


    def on_grid_size(self, size):
        self._gridSize = size
        self.update_grid()
        self._ui.actionGrid.setChecked(True)


    def load(self, path):
        pixmap = QtGui.QPixmap(path)
        if not pixmap.isNull():
            self.load_pixmap(pixmap)
        else:
            QtGui.QMessageBox.critical(self, "Load error", "Cannot open: " + path)


    def on_clear(self, ev):
        self.clear()


    def on_load(self, ev=None):
        path = QtGui.QFileDialog.getOpenFileName(
            self, "Load Image", "", "Images (*.bmp *.png *.gif *.jpg *.jpeg *.tif *.tiff)")
        if path:
            self.load(str(path))


    def on_help(self, ev=None):
        mb = QtGui.QMessageBox()
        mb.setWindowTitle('Help')
        mb.setTextFormat(QtCore.Qt.RichText)
        mb.setText(APP_HELP.format(APP_VER=APP_VER, APP_URL=APP_URL))
        mb.exec_()



# main application
class Application(QtGui.QApplication):
    def __init__(self, args):
        super(Application, self).__init__(args)

        # command-line flags
        ap = argparse.ArgumentParser(description=APP_DESC)
        ap.add_argument('--version', action='version', version='{} {}'.format(APP_NAME, APP_VER))
        ap.add_argument('file', nargs='?', help='Image to load')
        args = ap.parse_args(map(str, args[1:]))

        # initialize
        self.main_window = MainWindow()
        self.main_window.show()
        if args.file:
            self.main_window.load(args.file)
        else:
            self.main_window.on_load()

def main():
    return Application(sys.argv).exec_()

if __name__ == '__main__':
    sys.exit(main())
