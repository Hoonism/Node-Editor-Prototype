import math
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from nodeeditor.node_socket import *

EDGE_CP_ROUNDNESS = 100


class QDMGraphicsEdge(QGraphicsPathItem):
    def __init__(self, edge, parent=None):
        super().__init__(parent)

        self.edge = edge

        # init our flags
        self._last_selected_state = False

        # init variables
        self.posSource = [0, 0]
        self.posDestination = [200, 100]

        self.initAssets()
        self.initUI()

    def initUI(self):
        self.setFlag(QGraphicsItem.ItemIsSelectable)
        self.setZValue(-1)

    def initAssets(self):
        self._color = QColor("#001000")
        self._color_selected = QColor('#c1c1c1')
        # self.grad1 = QLinearGradient(self.posSource[0], self.posSource[1], self.posDestination[0], self.posDestination[1])
        # self.grad1.setColorAt(0.0, self._color)
        # self.grad1.setColorAt(1.0, self._color)
        self._pen = QPen(self._color, 2.0)
        self._pen_selected = QPen(self._color_selected, 2.0)
        self._pen_dragging = QPen(self._color_selected, 2.0)

    def onSelected(self):
        self.edge.scene.grScene.itemSelected.emit()

    def mouseReleaseEvent(self, event):
        super().mouseReleaseEvent(event)
        if self._last_selected_state != self.isSelected():
            self.node.scene.resetLastSelectedStates()
            self._last_selected_state = self.isSelected()
            self.onSelected()

    def setSource(self, x, y):
        self.posSource = [x, y]

    def setDestination(self, x, y):
        self.posDestination = [x, y]

    def boundingRect(self):
        return self.shape().boundingRect()

    def shape(self):
        return self.updatePath()

    def paint(self, painter, QStyleOptionGraphicsItem, widget=None):
        self.setPath(self.updatePath())

        if self.edge.end_socket is None:
            painter.setPen(self._pen_dragging)
        else:
            painter.setPen(self._pen if not self.isSelected() else self._pen_selected)
        painter.setBrush(Qt.NoBrush)
        painter.drawPath(self.path())

    def intersectsWith(self, p1, p2):
        cutpath = QPainterPath(p1)
        cutpath.lineTo(p2)
        path = self.updatePath()
        return cutpath.intersects(path)

    def updatePath(self):
        # will handle drawing QPainterPath from point A to B
        raise NotImplemented("This method has to be overridden in a child class")


class QDMGraphicsEdgeDirect(QDMGraphicsEdge):
    def updatePath(self, selected=False):
        # self.grad1 = QLinearGradient(self.posSource[0], self.posSource[1], self.posDestination[0], self.posDestination[1])
        # for edge in self.grScene.scene.edges:
        # if selected == True:
        #     self.grad1.setColorAt(0.0, self._color)
        #     self.grad1.setColorAt(1.0, self._color)
        #     self._pen = QPen(self.grad1, 2.0)
        # else:
        #     self.grad1.setColorAt(0.0, self._color_selected)
        #     self.grad1.setColorAt(0.4, self._color)
        #     self._pen = QPen(self.grad1, 2.0)
        path = QPainterPath(QPointF(self.posSource[0], self.posSource[1]))
        path.lineTo(self.posDestination[0], self.posDestination[1])
        return path
