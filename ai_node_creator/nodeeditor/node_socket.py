from collections import OrderedDict
from nodeeditor.node_graphics_socket import QDMGraphicsSocket
from nodeeditor.node_editor_widget import *
from nodeeditor.node_serializable import Serializable
LEFT_TOP = 1
LEFT_BOTTOM = 2
RIGHT_TOP = 3
RIGHT_BOTTOM = 4


class Socket(Serializable):
    def __init__(self, node, index=0, position=LEFT_TOP, socket_type="input", multi_edges=True):
        super().__init__()
        layout = QStackedLayout()
        layout.setCurrentIndex(1)

        self.node = node
        self.index = index
        self.position = position
        self.socket_type = socket_type
        self.is_multi_edges = multi_edges

        if self.socket_type == "input":
            self.grSocket = QDMGraphicsSocket(self, 0)
        if self.socket_type == "output":
            self.grSocket = QDMGraphicsSocket(self, 1)

        self.grSocket.setPos(*self.node.getSocketPosition(index, position))

        self.edges = []

    def getSocketPosition(self):
        res = self.node.getSocketPosition(self.index, self.position)
        return res

    def addEdge(self, edge):
        self.edges.append(edge)

    def removeEdge(self, edge):
        if edge in self.edges: self.edges.remove(edge)
        else: print("W: ", "Socket::removeEdge", "Want to remove edge", edge, "from self.edges, but not in list,")

    def removeAllEdges(self):
        while self.edges:
            edge = self.edges.pop(0)
            edge.remove()
    # def hasEdge(self):
    #     return self.edges is not None
    def determineMultiEdges(self, data):
        if "multi_edges" in data:
            return data['multi_edges']
        else:
            return data['position'] in (RIGHT_BOTTOM, RIGHT_TOP)

    def serialize(self):
        return OrderedDict({
            ('id', self.id),
            ('index', self.index),
            ('multi_edges', self.is_multi_edges),
            ('position', self.position),
            ('socket_type', self.socket_type)
        })

    def deserialize(self, data, hashmap={}, restore_id=True):
        if restore_id:
            self.id = data['id']
        self.is_multi_edges = self.determineMultiEdges(data)
        hashmap[data['id']] = self

        return True
