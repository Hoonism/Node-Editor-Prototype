from PyQt5.QtWidgets import QGraphicsView, QApplication
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from node_graphics_socket import QDMGraphicsSocket
from node_graphics_edge import QDMGraphicsEdge
from node_edge import Edge
from node_graphics_cutline import QDMCutLine

MODE_NOOP = 1
MODE_EDGE_DRAG = 2
MODE_EDGE_REASSIGN = 3
MODE_EDGE_CUT = 4


class QDMGraphicsView(QGraphicsView):
    scenePosChanged = pyqtSignal(int, int)

    def __init__(self, grScene, parent=None):
        super().__init__(parent)
        self.grScene = grScene
        self.initUI()

        self.setScene(self.grScene)

        self.mode = MODE_NOOP
        self.editingFlag = False

        self.zoomInFactor = 1.25
        self.zoomClamp = True
        self.zoom = 10
        self.zoomStep = 1
        self.zoomRange = [0, 20]
        self.edge_center = None

        # cutLine
        self.cutline = QDMCutLine()
        self.grScene.addItem(self.cutline)

# adds antialiasing & deletes scroll bar
    def initUI(self):
        self.setRenderHints(QPainter.Antialiasing | QPainter.HighQualityAntialiasing | QPainter.TextAntialiasing | QPainter.SmoothPixmapTransform)

        self.setViewportUpdateMode(QGraphicsView.FullViewportUpdate)

        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setDragMode(QGraphicsView.RubberBandDrag)

# sets mouse press events
    def mousePressEvent(self, event):
        if event.button() == Qt.MiddleButton:
            self.middleMouseButtonPress(event)
        elif event.button() == Qt.LeftButton:
            self.leftMouseButtonPress(event)
        elif event.button() == Qt.RightButton:
            self.rightMouseButtonPress(event)
        else:
            super().mousePressEvent(event)
# sets mouse release events

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MiddleButton:
            self.middleMouseButtonRelease(event)
        elif event.button() == Qt.LeftButton:
            self.leftMouseButtonRelease(event)
        elif event.button() == Qt.RightButton:
            self.rightMouseButtonRelease(event)
        else:
            super().mouseReleaseEvent(event)

# fakes middlemousebutton for left mouse click for both presses and releases
    def middleMouseButtonPress(self, event):
        releaseEvent = QMouseEvent(QEvent.MouseButtonRelease, event.localPos(), event.screenPos(), Qt.LeftButton, Qt.NoButton, event.modifiers())
        super().mouseReleaseEvent(releaseEvent)
        self.setDragMode(QGraphicsView.ScrollHandDrag)
        fakeEvent = QMouseEvent(event.type(), event.localPos(), event.screenPos(), Qt.LeftButton, event.buttons() | Qt.LeftButton, event.modifiers())
        super().mousePressEvent(fakeEvent)

    def middleMouseButtonRelease(self, event):
        fakeEvent = QMouseEvent(event.type(), event.localPos(), event.screenPos(), Qt.LeftButton, event.buttons() | Qt.LeftButton, event.modifiers())
        super().mouseReleaseEvent(fakeEvent)
        self.setDragMode(QGraphicsView.RubberBandDrag)

# starts dragging edge if socket is clicked
    def leftMouseButtonPress(self, event):
        item = self.getItemAtMousePos(event)

        # logic
        if hasattr(item, "node") or isinstance(item, QDMGraphicsEdge) or item is None:
            if event.modifiers() & Qt.ShiftModifier:
                event.ignore()
                fakeEvent = QMouseEvent(QEvent.MouseButtonPress, event.localPos(), event.screenPos(), Qt.LeftButton, event.button() | Qt.LeftButton, event.modifiers() | Qt.ControlModifier)
                super().mousePressEvent(fakeEvent)
                return

        if type(item) is QDMGraphicsSocket:
            print(item.socket, item.socket.edges)
            self.last_item_clicked = [item, item.socket_type]
            if len(item.socket.edges) > 0 and item.socket_type == 0:
                if self.mode != MODE_EDGE_REASSIGN:
                    self.mode = MODE_EDGE_REASSIGN
                    self.edgeDragStart(item)
                    return
            else:
                if self.mode != MODE_EDGE_DRAG:
                    self.mode = MODE_EDGE_DRAG
                    self.edgeDragStart(item)
                    return

        if item is None:
            if event.modifiers() & Qt.ControlModifier:
                self.mode = MODE_EDGE_CUT
                fakeEvent = QMouseEvent(QEvent.MouseButtonRelease, event.localPos(), event.screenPos(), Qt.LeftButton, Qt.NoButton, event.modifiers())
                super().mouseReleaseEvent(fakeEvent)
                QApplication.setOverrideCursor(Qt.CrossCursor)
                return

        super().mousePressEvent(event)

# ends dragging edge if left mouse button released
    def leftMouseButtonRelease(self, event):
        item = self.getItemAtMousePos(event)

        # logic
        if hasattr(item, "node") or isinstance(item, QDMGraphicsEdge) or item is None:
            if event.modifiers() & Qt.ShiftModifier:
                event.ignore()
                fakeEvent = QMouseEvent(event.type(), event.localPos(), event.screenPos(), Qt.LeftButton, Qt.NoButton, event.modifiers() | Qt.ControlModifier)
                super().mouseReleaseEvent(fakeEvent)
                return

        if self.mode == MODE_EDGE_DRAG or self.mode == MODE_EDGE_REASSIGN:
            res = self.edgeDragEnd(item)
            self.mode = MODE_NOOP
            return res
        if self.mode == MODE_EDGE_CUT:
            self.cutIntersectingEdges()
            self.cutline.line_points = []
            self.cutline.update()
            QApplication.setOverrideCursor(Qt.ArrowCursor)
            self.mode = MODE_NOOP
            return

        if self.dragMode() == QGraphicsView.RubberBandDrag:
            self.grScene.scene.history.storeHistory('Selection changed')

        super().mouseReleaseEvent(event)

    def rightMouseButtonPress(self, event):
        super().mousePressEvent(event)

    def rightMouseButtonRelease(self, event):
        super().mouseReleaseEvent(event)

    def getItemAtMousePos(self, event):
        pos = event.pos()
        obj = self.itemAt(pos)
        return obj

    def mouseMoveEvent(self, event):
        if self.mode == MODE_EDGE_DRAG or self.mode == MODE_EDGE_REASSIGN:
            self.pos = self.mapToScene(event.pos())
            self.drag_edge.grEdge.setDestination(self.pos.x(), self.pos.y())
            self.drag_edge.grEdge.update()

        if self.mode == MODE_EDGE_CUT:
            pos = self.mapToScene(event.pos())
            self.cutline.line_points.append(pos)
            self.cutline.update()

        self.last_scene_mouse_position = self.mapToScene(event.pos())

        self.scenePosChanged.emit(
            int(self.last_scene_mouse_position.x()), int(self.last_scene_mouse_position.y())
        )

        super().mouseMoveEvent(event)

    def keyPressEvent(self, event):
        super().keyPressEvent(event)

    def cutIntersectingEdges(self):

        for ix in range(len(self.cutline.line_points) - 1):
            p1 = self.cutline.line_points[ix]
            p2 = self.cutline.line_points[ix + 1]

            for edge in self.grScene.scene.edges:
                if edge.grEdge.intersectsWith(p1, p2):
                    edge.remove()
        self.grScene.scene.history.storeHistory("Delete cut edges", setModified=True)

    def deleteSelected(self):
        for item in self.grScene.selectedItems():
            if isinstance(item, QDMGraphicsEdge):
                item.edge.remove()
            elif hasattr(item, 'node'):
                item.node.remove()
        self.grScene.scene.history.storeHistory("Delete selected", setModified=True)

    def edgeDragStart(self, item):
        if self.mode == MODE_EDGE_DRAG:
            self.drag_start_socket = item.socket
            self.drag_edge = Edge(self.grScene.scene, item.socket, None)
        if self.mode == MODE_EDGE_REASSIGN:
            self.previousEdge = item.socket.edges
            for edge in self.previousEdge:
                if edge.start_socket.socket_type == "output":
                    self.edge_center = edge.start_socket
                elif edge.start_socket.socket_type == "input":
                    self.edge_center = edge.end_socket
            self.drag_edge = Edge(self.grScene.scene, self.edge_center, None)

    def edgeDragEnd(self, item):
        self.drag_edge.remove()
        self.drag_edge=None
        if self.mode == MODE_EDGE_DRAG:
            # if end socket is different from start socket

            if type(item) is QDMGraphicsSocket:
                if item.socket != self.drag_start_socket:

                    if not item.socket.is_multi_edges:
                        item.socket.removeAllEdges()

                    if not self.drag_start_socket.is_multi_edges:
                        self.drag_start_socket.removeAllEdges()
        if self.mode == MODE_EDGE_REASSIGN:
            print("tes")
            if type(item) is QDMGraphicsSocket and item.socket_type == self.last_item_clicked[1]:

                # if item.socket.hasEdge():
                #     item.socket.edges.remove()
                if self.previousEdge is not None:
                    try:
                        self.previousEdge.remove()
                        print("yes")
                    except:
                        pass
                self.drag_edge.start_socket = self.drag_start_socket
                self.drag_edge.end_socket = item.socket
                self.drag_edge.start_socket.addEdge(self.drag_edge)
                self.drag_edge.end_socket.addEdge(self.drag_edge)
                self.drag_edge.updatePositions()
                self.grScene.scene.history.storeHistory("Created new edge by dragging", setModified=True)
            else:
                self.drag_edge.remove()
            return True
            if self.previousEdge is not None:
                self.previousEdge.start_socket.edges = self.previousEdge

        return False

    def wheelEvent(self, event):
        # calculate our zoom factor
        zoomOutFactor = 1 / self.zoomInFactor

        # calculate zoom
        if event.angleDelta().y() > 0:
            zoomFactor = self.zoomInFactor
            self.zoom += self.zoomStep
        else:
            zoomFactor = zoomOutFactor
            self.zoom -= self.zoomStep

        clamped = False
        if self.zoom < self.zoomRange[0]:
            self.zoom, clamped = self.zoomRange[0], True
        if self.zoom > self.zoomRange[1]:
            self.zoom, clamped = self.zoomRange[1], True

        # set scene scale
        if not clamped or self.zoomClamp == False:
            self.scale(zoomFactor, zoomFactor)
