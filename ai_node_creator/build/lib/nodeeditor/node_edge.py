from collections import OrderedDict
from nodeeditor.node_serializable import Serializable
from nodeeditor.node_graphics_edge import *

EDGE_TYPE_DIRECT = 1


class Edge(Serializable):
    def __init__(self, scene, start_socket=None, end_socket=None, edge_type=EDGE_TYPE_DIRECT):
        super().__init__()
        self.scene = scene

        # init start
        self._start_socket = None
        self._end_socket = None

        self.start_socket = start_socket
        self.end_socket = end_socket
        self.edge_type = edge_type

        self.scene.addEdge(self)

    @ property
    def start_socket(self): return self._start_socket

    @ start_socket.setter
    def start_socket(self, value):
        # delete from socket if assigned to another socket
        if self._start_socket is not None:
            self._start_socket.removeEdge(self)
        # assign new start socket
        self._start_socket = value
        # addEdge to the socket class
        if self.start_socket is not None:
            self.start_socket.addEdge(self)

    @ property
    def end_socket(self): return self._end_socket

    @ end_socket.setter
    def end_socket(self, value):
        # delete from socket if assigned to another socket
        if self._end_socket is not None:
            self._end_socket.removeEdge(self)
        # assign new end socket
        self._end_socket = value
        # addEdge to the socket class
        if self.end_socket is not None:
            self.end_socket.addEdge(self)

    @ property
    def edge_type(self): return self._edge_type

    @ edge_type.setter
    def edge_type(self, value):

        if hasattr(self, 'grEdge') and self.grEdge is not None:
            self.scene.grScene.removeItem(self.grEdge)

        self._edge_type = value

        self.grEdge = QDMGraphicsEdgeDirect(self)

        self.scene.grScene.addItem(self.grEdge)
        if self.start_socket is not None:
            self.updatePositions()

    def updatePositions(self):
        source_pos = self.start_socket.getSocketPosition()
        source_pos[0] += self.start_socket.node.grNode.pos().x()
        source_pos[1] += self.start_socket.node.grNode.pos().y()
        self.grEdge.setSource(*source_pos)
        if self.end_socket is not None:
            end_pos = self.end_socket.getSocketPosition()
            end_pos[0] += self.end_socket.node.grNode.pos().x()
            end_pos[1] += self.end_socket.node.grNode.pos().y()
            self.grEdge.setDestination(*end_pos)
        else:
            self.grEdge.setDestination(*source_pos)
        self.grEdge.update()

    def remove_from_sockets(self):
        # TODO: Fix ME!!
        # if self.start_socket is not None:
        #     self.start_socket.removeEdge(None)
        # if self.end_socket is not None:
        #     self.end_socket.removeEdge(None)
        self.end_socket = None
        self.start_socket = None

    def remove(self):

        self.remove_from_sockets()
        self.scene.grScene.removeItem(self.grEdge)
        self.grEdge = None
        try:
            self.scene.removeEdge(self)
        except ValueError:
            pass

    def serialize(self):
        return OrderedDict([
            ('id', self.id),
            ('start', self.start_socket.id),
            ('end', self.end_socket.id),
        ])

    def deserialize(self, data, hashmap={}, restore_id=True):
        if restore_id == True:
            self.id = data['id']
        self.start_socket = hashmap[data['start']]
        self.end_socket = hashmap[data['end']]
