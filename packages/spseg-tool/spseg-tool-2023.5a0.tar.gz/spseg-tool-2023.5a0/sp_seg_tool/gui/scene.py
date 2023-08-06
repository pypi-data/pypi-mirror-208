import random
from typing import Callable
import numpy as np

from PyQt5.QtWidgets import QGraphicsScene, QGraphicsView
from PyQt5.QtGui import QImage, QPixmap, QPainter, QColor, QPolygonF, QPen
from PyQt5.QtCore import Qt, QPointF


class ScrollableView(QGraphicsView):
    ZOOM_IN_FACTOR = 1.2
    ZOOM_OUT_FACTOR = 1.0 / ZOOM_IN_FACTOR

    def __init__(self, scene):
        super().__init__(scene)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setMouseTracking(True)

    def wheelEvent(self, event):
        if event.modifiers() & Qt.ControlModifier:
            if event.angleDelta().y() > 0:
                zoom_factor = self.ZOOM_IN_FACTOR
            else:
                zoom_factor = self.ZOOM_OUT_FACTOR
            self.scale(zoom_factor, zoom_factor)
        elif event.modifiers() & Qt.ShiftModifier:
            self.horizontalScrollBar().setValue(
                self.horizontalScrollBar().value() + event.angleDelta().y()
            )
        else:
            super().wheelEvent(event)


class Scene(QGraphicsScene):
    def __init__(
        self,
        parent,
        left_button_logic: Callable[[QPointF], None],
        right_button_logic: Callable[[QPointF], None],
        get_img: Callable[[None], None],
    ):
        super().__init__()
        self.parent = parent
        self.pixmap_item = self._set_default_view_and_get_reference()
        self.view = ScrollableView(self)
        self.left_button_logic = left_button_logic
        self.right_button_logic = right_button_logic
        self.get_img = get_img

        self.painter = QPainter()

        self.is_drawing_polygon = True
        self.cursor_point = None
        self.polygon_points = []
        self.polygon = None

    def add_close_polygon_callback(self, func) -> None:
        assert callable(func)
        self.close_polygon_callback = func

    def _set_default_view_and_get_reference(self):
        img = np.require(
            np.full((400, 400, 3), fill_value=125).astype(np.int32),
            np.uint8,
            "C",
        )
        img = QImage(img, img.shape[1], img.shape[0], QImage.Format_RGB888)
        pixamap = QPixmap(img)
        return self.addPixmap(pixamap)

    def refresh(self):
        img = self.get_img()
        if len(img.shape) == 3:
            format_ = QImage.Format_RGB888
        else:
            format_ = QImage.Format_Grayscale8
        # pixamap = QPixmap.fromImage(ImageQt(img))
        img = QImage(img, img.shape[1], img.shape[0], format_)
        pixamap = QPixmap(img)

        if self.is_drawing_polygon:
            self.painter.begin(pixamap)
            self.painter.setBrush(self.get_color())
            self.painter.setPen(QPen(QColor(102, 255, 0)))
            all_points = (
                self.polygon_points + [self.cursor_point]
                if self.cursor_point
                else self.polygon_points
            )
            if self.polygon_points:
                self.painter.drawPolygon(QPolygonF(all_points))
            self.painter.end()
        return self.pixmap_item.setPixmap(pixamap)

    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        match event.button():
            case Qt.LeftButton:
                self.polygon_points.append(QPointF(event.pos()))
                self.is_drawing_polygon = True
            case Qt.RightButton:
                self.close_polygon()
                self.is_drawing_polygon = False
                self.polygon = QPolygonF(self.polygon_points)
                self.close_polygon_callback(self.polygon)
                self.polygon_points = []
                self.polygon = None
        self.refresh()

    def mouseMoveEvent(self, event):
        super().mouseMoveEvent(event)
        if event.buttons() == Qt.NoButton:
            point = QPointF(event.scenePos())
            if self._is_in_scene(point):
                self.cursor_point = QPointF(point)
        self.refresh()

    def _is_in_scene(self, point: QPointF) -> QPointF:
        if point.x() > self.width():
            return False
        elif point.x() < 0:
            return False
        if point.y() > self.height():
            return False
        elif point.y() < 0:
            return False
        return True

    def get_color(self):
        return QColor(150, 200, 200)

    def close_polygon(self) -> None:
        if self.polygon_points:
            self.polygon_points.append(self.polygon_points[0])
