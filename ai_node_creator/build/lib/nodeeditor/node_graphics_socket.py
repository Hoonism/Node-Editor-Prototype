from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *


class QDMGraphicsSocket(QGraphicsItem):
    def __init__(self, socket, socket_type):
        self.socket = socket
        super().__init__(socket.node.grNode)

        self.setZValue(-1)
        self.socket_type = socket_type
        self.radius = 6.0
        self.outline_width = 1.0
        self._colors = [QColor("#FFFF7700"), QColor("#FF52e220"), QColor("#FF0056a6"), QColor("#FFa86db1"), QColor("#FFb54747"), QColor("FFdbe220")]

        self._color_background = self._colors[self.socket_type]
        self._color_outline = QColor("#FF000000")

        self._pen = QPen(self._color_outline)
        self._brush = QBrush(self._color_background)

    def paint(self, painter, QStyleOptionGraphicsItem, widget=None):
        # painting circle
        painter.setBrush(self._brush)
        painter.setPen(self._pen)
        painter.drawEllipse(-self.radius, -self.radius, 2 * self.radius, 2 * self.radius)

    def boundingRect(self):
        return QRectF(
            -self.radius - self.outline_width,
            -self.radius - self.outline_width,
            2 * (self.radius + self.outline_width),
            2 * (self.radius + self.outline_width),
        )
