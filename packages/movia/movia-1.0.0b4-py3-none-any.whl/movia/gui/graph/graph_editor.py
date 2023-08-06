#!/usr/bin/env python3

"""
** Allows you to view and edit the assembly graph with a ``block`` view. **
---------------------------------------------------------------------------
"""

import math
import numbers
import typing

from PyQt6 import QtCore, QtGui, QtWidgets

from movia.core.edit.operation.add import add_edge, add_node
from movia.core.edit.operation.remove import remove_element
from movia.gui.base import MoviaWidget
from movia.gui.graph.edge_properties import WindowEdgeProperties
from movia.gui.graph.layout import (compute_positions, clear_positions, create_and_init_agraph,
    draw, has_positions, same_structure)
from movia.gui.edit_node_state.main import EditNodeWindow



class GraphEditor(MoviaWidget, QtWidgets.QWidget):
    """
    ** Viewing and editing the assembly graph. **
    """

    def __init__(self, parent):
        super().__init__(parent)
        self._parent = parent

        # declaration
        self._agraph = None
        self._dpi = 100
        self.graph_viewer = GraphViewer(self)
        self.toolbar = GraphToolBar(self)

        # configuration
        self.setAcceptDrops(True)

        # location
        canvas_area = QtWidgets.QScrollArea(self)
        canvas_area.setWidget(self.graph_viewer)
        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(self.toolbar)
        layout.addWidget(canvas_area)
        self.setLayout(layout)

    def dragEnterEvent(self, event):
        """
        ** Drag and drop selection. **
        """
        if not event.mimeData().hasFormat("application/x-qabstractitemmodeldatalist"):
            event.ignore()
            return
        if self.app.global_vars.get("drag_an_drop", None) is None:
            event.ignore()
            return
        event.accept()

    def dropEvent(self, _):
        """
        ** Drag and drop management. **
        """
        node_name, attrs = self.app.global_vars["drag_an_drop"]
        add_node(self.app.graph, node_name, attrs)
        print(f"create {node_name}")
        self.refresh()

    @property
    def dpi(self):
        """
        ** Get the dpi resolution. **
        """
        return self._dpi

    @dpi.setter
    def dpi(self, new_dpi):
        """
        ** Set the dpi resolution and do verification. **
        """
        assert isinstance(new_dpi, numbers.Real), new_dpi.__class__.__name__
        new_dpi = round(float(new_dpi))
        assert new_dpi > 1, new_dpi
        self._dpi = new_dpi

    def get_agraph(self):
        """
        ** Returns the graph of type ``pygraphviz.AGraph``. **

        This graph if always updated with the assembly graph.
        """
        graph = self.app.graph.copy() # because it is not thread safe
        if self._agraph is not None:
            if not same_structure(self._agraph, graph):
                self._agraph = None
        if self._agraph is None:
            self._agraph = create_and_init_agraph(graph)
        return self._agraph

    def refresh(self):
        """
        ** Updates the elements of this widget and child widgets. **
        """
        self.graph_viewer.refresh()


class GraphToolBar(MoviaWidget, QtWidgets.QToolBar):
    """
    ** This is the toolbar related to graph editing. **
    """

    def __init__(self, parent):
        super().__init__(parent)
        self._parent = parent

        act_zoom_in = QtGui.QAction("zoom in", self)
        act_zoom_in.setIcon(QtGui.QIcon.fromTheme("zoom-in"))
        act_zoom_in.triggered.connect(self.zoom_in)
        self.addAction(act_zoom_in)

        act_zoom_out = QtGui.QAction("zoom out", self)
        act_zoom_out.setIcon(QtGui.QIcon.fromTheme("zoom-out"))
        act_zoom_out.triggered.connect(self.zoom_out)
        self.addAction(act_zoom_out)

    def zoom_in(self):
        """
        ** Increases dpi. **
        """
        print(f"zoom in (dpi {self.parent.dpi}->", end="")
        self.parent.dpi = min(600, self.parent.dpi * 1.2)
        print(f"{self.parent.dpi})")
        self.parent.refresh()

    def zoom_out(self):
        """
        ** Increases dpi. **
        """
        print(f"zoom out (dpi {self.parent.dpi}->", end="")
        self.parent.dpi = max(20, self.parent.dpi / 1.2)
        print(f"{self.parent.dpi})")
        self.parent.refresh()


class GraphViewer(MoviaWidget, QtWidgets.QLabel):
    """
    ** Draw the assembly graph. **
    """

    def __init__(self, parent):
        super().__init__(parent)
        self._parent = parent
        self._state = None
        self._positions = None
        self._state_in_content = None # the value when entering the new state

        self.setMouseTracking(True) # avoids having to click
        self.state = "normal"

    def _draw_arrow_new_stream(self, dst_node):
        # draw main
        canvas = self.pixmap()
        painter = QtGui.QPainter(canvas)
        pen = QtGui.QPen()
        pen.setWidth(6)
        pen.setColor(QtGui.QColorConstants.Black)
        pen.setStyle(QtCore.Qt.PenStyle.DotLine)
        pen.setCapStyle(QtCore.Qt.PenCapStyle.RoundCap)
        painter.setPen(pen)
        src_pos = self.get_positions()[self._state_in_content["node"]]
        dst_pos = self.get_positions()[dst_node]
        fact = max(self.width(), self.height())
        x_s, y_s = round(src_pos["x"]*fact), round(self.height()-src_pos["y"]*fact)
        x_d, y_d = round(dst_pos["x"]*fact), round(self.height()-dst_pos["y"]*fact)
        painter.drawLine(x_s, y_s, x_d, y_d)

        # draw arrow
        phi = math.copysign(math.acos((x_d-x_s)/math.dist([x_s, y_s], [x_d, y_d])), y_d-y_s)
        for theta in (math.radians(150), math.radians(-150)):
            painter.drawLine(
                x_d, y_d, round(x_d + 22*math.cos(theta+phi)), round(y_d + 22*math.sin(theta+phi))
            )

        painter.end()
        self.setPixmap(canvas)

    def del_element(self, name):
        """
        ** Delete the selected element of the graph. **
        """
        old_state, self.state = self.state, "loading"
        backup_graph = self.app.graph.copy()
        trans = remove_element(self.app.graph, name)
        try:
            self.app.tree()
        except AssertionError as err:
            self.app.graph = backup_graph
            QtWidgets.QMessageBox.warning(
                None, "Deletion not permitted", f"Unable to delete {name} : {err}"
            )
        else:
            for element, action in trans.items():
                if action is None:
                    print(f"delete {element}")
                else:
                    print(f"rename {element} to {action}")
            self.main_window.refresh()
        self.state = old_state

    def enter_state_new_stream(self, node, index):
        """
        ** Enter the stream adding mode. **
        """
        self.state = "new_stream"

        element = self.parent.get_agraph().get_node(node)
        old_style = element.attr["style"]
        element.attr["style"] = "bold"

        self._state_in_content = {"node": node, "index": index, "old_style": old_style}

        self.refresh()

    def enterEvent(self, _):
        """
        ** For focus management. **
        """
        self.setFocus() # for keyPressEvent enable

    def exit_state_new_stream(self, event):
        """
        ** Add the new edge. **
        """
        node_dst, _ = self.select_node(event)
        node_src = self._state_in_content["node"]
        index = self._state_in_content["index"]
        self.state = "normal"

        old_state, self.state = self.state, "loading"
        backup_graph = self.app.graph.copy()
        edge = add_edge(self.app.graph, node_src, node_dst, index)
        try:
            self.app.tree()
        except AssertionError as err:
            self.app.graph = backup_graph
            QtWidgets.QMessageBox.warning(
                None, "Stream creation not permitted", f"Unable to create {edge} : {err}"
            )
        else:
            print(f"create {edge}")
            self.main_window.refresh()
        self.state = old_state

    def get_positions(self):
        """
        ** Returns the relative positions of the elements in the graph. **
        """
        agraph = self.parent.get_agraph()
        if (
            self._positions is None
            or not has_positions(agraph)
            or set(self._positions) != set(self.app.graph.nodes) | set(self.app.graph.edges)
        ):
            clear_positions(agraph)
            self._positions = compute_positions(agraph)
        return self._positions

    def keyPressEvent(self, event):
        """
        ** Delete an element. **
        """
        if self.state == "normal":
            if event.key() == QtCore.Qt.Key.Key_Delete:
                name, dist = self.select()
                if dist <= 20:
                    self.del_element(name)
        elif self.state == "new_stream":
            if event.key() == QtCore.Qt.Key.Key_Escape:
                self.state = "normal"

    def leaveEvent(self, _):
        """
        ** Allows you to put the graph image at rest. **
        """
        self.refresh()

    def menu_element(self, event):
        """
        ** Displays the menu related to objects. **
        """
        name, dist = self.select(event)
        if dist <= 20:
            sub_elements = []

            if isinstance(name, str): # if the element is a node
                streams = self.app.tree_node(name).out_streams
                if len(streams) == 1:
                    action = QtGui.QAction("New stream")
                    action.setIcon(QtGui.QIcon.fromTheme("list-add"))
                    action.triggered.connect(lambda: self.enter_state_new_stream(name, 0))
                    sub_elements.append(action)
                elif len(streams) > 1:
                    def local_enter_new_stream(index): # local copy of index
                        return lambda: self.enter_state_new_stream(name, index)
                    sub_menu = QtWidgets.QMenu("New stream", self)
                    sub_menu.setIcon(QtGui.QIcon.fromTheme("list-add"))
                    actions = []
                    for index, stream in enumerate(streams):
                        action = QtGui.QAction(f"stream {index} ({stream})")
                        action.triggered.connect(local_enter_new_stream(index))
                        actions.append(action)
                    sub_menu.addActions(actions)
                    sub_elements.append(sub_menu)

            action = QtGui.QAction("Delete")
            action.setIcon(QtGui.QIcon.fromTheme("edit-delete"))
            action.setShortcut("delete")
            action.triggered.connect(lambda: self.del_element(name))
            sub_elements.append(action)

            action = QtGui.QAction("Edit")
            action.setIcon(QtGui.QIcon.fromTheme("edit-find"))
            action.triggered.connect(lambda: self.show_element_properties(event))
            sub_elements.append(action)

            menu = QtWidgets.QMenu(self)
            for sub_element in sub_elements:
                if isinstance(sub_element, QtGui.QAction):
                    menu.addAction(sub_element)
                elif isinstance(sub_element, QtWidgets.QMenu):
                    menu.addMenu(sub_element)
            menu.exec(QtGui.QCursor.pos())

    def mouseMoveEvent(self, event):
        """
        ** Allows you to highlight the elements of the graph that are hovered over. **
        """
        if self.state == "normal":
            name, dist = self.select(event)
            if dist > 20:
                self.refresh()
                return
            agraph = self.parent.get_agraph()
            if isinstance(name, tuple):
                element = agraph.get_edge(*name)
            else:
                element = agraph.get_node(name)
            old_style = element.attr["style"]
            element.attr["style"] = "bold"
            self.refresh()
            element.attr["style"] = old_style

        elif self.state == "new_stream":
            node, _ = self.select_node(event)
            element = self.parent.get_agraph().get_node(node)
            old_style = element.attr["style"]
            element.attr["style"] = "bold"
            if self._state_in_content["node"] == node:
                old_color = element.attr["color"]
                element.attr["color"] = "red"
            self.refresh()
            element.attr["style"] = old_style
            if self._state_in_content["node"] == node:
                element.attr["color"] = old_color
            else:
                self._draw_arrow_new_stream(node)

    def mousePressEvent(self, event):
        """
        ** Leads according to the internal state, the actions to be followed at the click. **
        """
        if self.state == "normal":
            if event.button() == QtCore.Qt.MouseButton.LeftButton:
                self.show_element_properties(event)
            elif event.button() == QtCore.Qt.MouseButton.RightButton:
                self.menu_element(event)
        if self.state == "new_stream":
            if event.button() == QtCore.Qt.MouseButton.LeftButton:
                self.exit_state_new_stream(event)

    def refresh(self):
        """
        ** Updates the elements of this widget and child widgets. **
        """
        form = "png"
        agraph = self.parent.get_agraph()
        if not has_positions(agraph):
            compute_positions(agraph)
        (width, height), img_bytes = draw(agraph, dpi=self.parent.dpi, form=form)

        bytes_array = QtCore.QByteArray(img_bytes)
        canvas = self.pixmap()
        self.resize(width, height)
        assert canvas.loadFromData(bytes_array, form)

        self.setPixmap(canvas)

    def select(self, event=None) -> tuple[typing.Union[tuple, str], numbers.Real]:
        """
        ** Select the nearest edge or node. **

        Returns
        -------
        name : typing.Union[tuple, str]
            The name of the selected edge or node.
        dist : number.Real
            The minimum distance between the element and the cursor, in pixel.
        """
        edge_name, edge_dist = self.select_edge(event)
        node_name, node_dist = self.select_node(event)
        if edge_name is None or node_dist < edge_dist:
            return node_name, node_dist
        return edge_name, edge_dist

    def select_edge(self, event=None) -> tuple[tuple, numbers.Real]:
        """
        ** Selects the edge closest to the cursor. **

        Returns
        -------
        edge_name : tuple
            The name of the selected edge.
        dist : number.Real
            The minimum distance between the edge and the cursor, in pixel.
        """
        factor = max(self.width(), self.height())
        pos = self.mapFromGlobal(QtGui.QCursor.pos()) if event is None else event.pos()
        rel_x = pos.x() / factor
        rel_y = (self.height() - pos.y()) / factor
        positions = self.get_positions()

        def edge_dist(rel_x, rel_y, line_xy):
            dist = math.inf
            for (p1_x, p1_y), (p2_x, p2_y) in zip(line_xy[:-1], line_xy[1:]):

                x_0 = p1_x*p2_x
                x_1 = p1_y*p2_y
                x_2 = p1_x**2 + p1_y**2
                num = -p1_x*rel_x - p1_y*rel_y + p2_x*rel_x + p2_y*rel_y - x_0 - x_1 + x_2
                den = p2_x**2 + p2_y**2 - 2*x_0 - 2*x_1 + x_2
                lamb = num / den

                if lamb >= 1: # case p2
                    inter = (p2_x, p2_y)
                elif lamb <= 0: # case p1
                    inter = (p1_x, p1_y)
                else:
                    inter = (p1_x + lamb*(p2_x-p1_x), p1_y + lamb*(p2_y-p1_y))
                dist = min(dist, math.sqrt((rel_x-inter[0])**2 + (rel_y-inter[1])**2))

            return dist

        dist2edge = {
            edge_dist(rel_x, rel_y, edge_attr["pos"]): edge_name
            for edge_name, edge_attr in positions.items() if isinstance(edge_name, tuple)
        }
        if not dist2edge:
            return None, None
        rel_dist = min(dist2edge)
        edge_name = dist2edge[rel_dist]
        dist = rel_dist * factor
        return edge_name, dist

    def select_node(self, event=None) -> tuple[str, numbers.Real]:
        """
        ** Selects the node closest the cursor. **

        Returns
        -------
        node_name : str
            The name of the node.
        dist : numbers.Real
            The distance between the node and the cursor, in pixel.
        """
        factor = max(self.width(), self.height())
        pos = self.mapFromGlobal(QtGui.QCursor.pos()) if event is None else event.pos()
        rel_x = pos.x() / factor
        rel_y = (self.height() - pos.y()) / factor

        def ellipse_dist(rel_x, rel_y, attr):
            p_x, p_y = rel_x-attr["x"] , rel_y-attr["y"]
            r_x, r_y = .5*attr["width"], .5*attr["height"]

            # case we are in the ellipse
            if (p_x/r_x)**2 + (p_y/r_y)**2 <= 1:
                return 0

            # case out of the ellipse, for a question of solvability and speed, the distance
            # is compute like the intersection of the ellipse
            # and the segment passing through the origin of the ellipse
            p_x, p_y = abs(p_x), abs(p_y) # symmetries
            if p_x == 0:
                return abs(p_y) - r_y
            if p_y == 0:
                return abs(p_x) - r_x

            i_x = math.sqrt((r_y*r_x*p_x)**2 / ((r_x*p_y)**2 + (r_y*p_x)**2))
            i_y = math.sqrt((r_x*r_y*p_y)**2 / ((r_y*p_x)**2 + (r_x*p_y)**2))
            dist = math.sqrt((p_x-i_x)**2 + (p_y-i_y)**2)
            return dist

        dist_funcs = {
            "ellipse": ellipse_dist,
            "oval": ellipse_dist,
        }

        positions = self.get_positions()
        dist2node = {
            dist_funcs[attr["shape"]](rel_x, rel_y, attr): node_name
            for node_name, attr in positions.items() if isinstance(node_name, str)
        }
        rel_dist = min(dist2node)
        node_name = dist2node[rel_dist]
        dist = rel_dist * factor
        return node_name, dist

    def show_element_properties(self, event):
        """
        ** Shows a window associated to the selected element. **
        """
        name, dist = self.select(event)
        if dist <= 20:
            old_state, self.state = self.state, "loading"
            if isinstance(name, tuple): # element is edge
                graph_win = WindowEdgeProperties(self, name)
            else: # element is node
                graph_win = EditNodeWindow(self, name)
            graph_win.exec()
            self.state = old_state

    @property
    def state(self) -> str:
        """
        ** Returns the graph viewer state. **
        """
        return self._state

    def state_new_stream_to_normal(self):
        """
        ** Performs the steps necessary to transition states. **
        """
        element = self.parent.get_agraph().get_node(self._state_in_content["node"])
        element.attr["style"] = self._state_in_content["old_style"]
        self._state_in_content = None
        self.refresh()

    @state.setter
    def state(self, new_state: str) -> None:
        """
        ** Updates the state and shape of the cursor. **

        Parameters
        ----------
        new_state : str
            Can take the values:
                * loading
                * normal
        """
        assert isinstance(new_state, str), new_state.__class__.__name__

        old_state = self._state
        if new_state == "loading":
            self._state = "loading"
            self.setCursor(QtCore.Qt.CursorShape.WaitCursor)
        elif new_state == "normal":
            self._state = "normal"
            self.setCursor(QtCore.Qt.CursorShape.PointingHandCursor)
        elif new_state == "new_stream":
            self._state = "new_stream"
            self.setCursor(QtCore.Qt.CursorShape.PointingHandCursor)
        else:
            raise ValueError(f"the state '{new_state}' is not possible")
        if (apply_state := getattr(self, f"state_{old_state}_to_{new_state}", None)) is not None:
            apply_state()
