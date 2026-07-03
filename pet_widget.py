"""Main pet widget — transparent floating window displaying Oreo's sprite sheet."""

import os
import sys
import math
from PIL import Image
from PyQt6.QtCore import Qt, QTimer, QPoint, QRectF, QRect
from PyQt6.QtGui import QPixmap, QPainter, QIcon, QAction, QCursor, QColor, QPen, QFont, QImage, QTransform
from PyQt6.QtWidgets import QWidget, QMenu, QSystemTrayIcon, QApplication

from behaviors import FloatingBehavior, State

if getattr(sys, "_MEIPASS", None):
    FRAMES_DIR = os.path.join(sys._MEIPASS, "frames")
else:
    FRAMES_DIR = os.path.join(os.path.dirname(__file__), "frames")

FRAMES_WALK_DIR = os.path.join(FRAMES_DIR, "walking")
WALK_FRAMES_SEQ = [5, 6]

PET_SIZE = 150
WALK_ANIM_SPEED = 8


def _pil_to_qpixmap(img):
    """Convert a PIL RGBA image to QPixmap."""
    data = img.tobytes("raw", "RGBA")
    qimg = QImage(data, img.width, img.height, 4 * img.width, QImage.Format.Format_RGBA8888)
    return QPixmap.fromImage(qimg.copy())


class PetWidget(QWidget):
    def __init__(self):
        super().__init__()
        self._setup_window()
        self._load_frames()
        self._setup_behavior()
        self._setup_animation()
        self._setup_tray()

        self.dragging = False
        self.drag_offset = QPoint(0, 0)
        self.click_pos = None
        self.float_x = float(self.x())
        self.float_y = float(self.y())
        self.walk_frame_index = 0
        self.walk_frame_counter = 0
        self._flipped_cache = {}

    def _setup_window(self):
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedSize(PET_SIZE, PET_SIZE)

        screen = QApplication.primaryScreen().geometry()
        self.screen_width = screen.width()
        self.screen_height = screen.height()

        start_x = self.screen_width // 2 - PET_SIZE // 2
        start_y = self.screen_height - PET_SIZE - 50
        self.move(start_x, start_y)

    def _load_frames(self):
        """Load walking frames."""
        self.walk_frames = []
        for i in WALK_FRAMES_SEQ:
            path = os.path.join(FRAMES_WALK_DIR, f"frame_{i}.png")
            img = Image.open(path).convert("RGBA")
            img.thumbnail((PET_SIZE, PET_SIZE), Image.LANCZOS)
            pixmap = _pil_to_qpixmap(img)
            self.walk_frames.append(pixmap)

    def _setup_behavior(self):
        self.behavior = FloatingBehavior(self.screen_width, self.screen_height, PET_SIZE)
        self.show_heart = False
        self.heart_timer = 0

    def _setup_animation(self):
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._tick)
        self.timer.start(50)

    def _setup_tray(self):
        icon = QIcon(self._frame_as_pixmap(0))

        self.tray = QSystemTrayIcon(icon, self)
        self.tray.setToolTip("Oreo")

        tray_menu = QMenu()
        show_action = QAction("Show Oreo", self)
        show_action.triggered.connect(self._show_pet)
        tray_menu.addAction(show_action)

        quit_action = QAction("Quit", self)
        quit_action.triggered.connect(QApplication.quit)
        tray_menu.addAction(quit_action)

        self.tray.setContextMenu(tray_menu)
        self.tray.activated.connect(self._tray_activated)
        self.tray.show()

    def _frame_as_pixmap(self, index):
        return self.walk_frames[index % len(self.walk_frames)]

    def _show_pet(self):
        self.show()
        self.raise_()

    def _tray_activated(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            self._show_pet()

    def _tick(self):
        if self.dragging:
            return

        dx, dy = self.behavior.update(self.float_x, self.float_y)
        self.float_x += dx
        self.float_y += dy

        self.float_x = max(0, min(self.float_x, self.screen_width - PET_SIZE))
        self.float_y = max(0, min(self.float_y, self.screen_height - PET_SIZE))

        self.move(int(self.float_x), int(self.float_y))

        # Always cycle through walk frames
        self.walk_frame_counter += 1
        if self.walk_frame_counter >= WALK_ANIM_SPEED:
            self.walk_frame_counter = 0
            self.walk_frame_index = (self.walk_frame_index + 1) % len(self.walk_frames)

        if self.show_heart:
            self.heart_timer -= 1
            if self.heart_timer <= 0:
                self.show_heart = False

        self.update()

    def _get_current_pixmap(self, flip=False):
        pixmap = self.walk_frames[self.walk_frame_index]

        if flip:
            key = (self.walk_frame_index, True)
            if key not in self._flipped_cache:
                self._flipped_cache[key] = pixmap.transformed(QTransform().scale(-1, 1))
            return self._flipped_cache[key]
        return pixmap

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)

        flip = self.behavior.direction < 0
        pixmap = self._get_current_pixmap(flip=flip)

        x = (PET_SIZE - pixmap.width()) // 2
        y = (PET_SIZE - pixmap.height()) // 2
        painter.drawPixmap(x, y, pixmap)

        if self.show_heart:
            self._draw_heart(painter)

        painter.end()

    def _draw_heart(self, painter):
        painter.setPen(QPen(QColor(255, 80, 80), 2))
        painter.setBrush(QColor(255, 80, 80, 200))
        font = QFont("Arial", 20)
        painter.setFont(font)
        painter.drawText(QRectF(PET_SIZE - 40, 0, 40, 40), Qt.AlignmentFlag.AlignCenter, "❤")

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.dragging = True
            self.drag_offset = event.pos()
            self.click_pos = event.globalPosition().toPoint()
            self.setCursor(QCursor(Qt.CursorShape.ClosedHandCursor))
        elif event.button() == Qt.MouseButton.RightButton:
            self._show_context_menu(event.globalPosition().toPoint())

    def mouseMoveEvent(self, event):
        if self.dragging:
            new_pos = event.globalPosition().toPoint() - self.drag_offset
            self.move(new_pos)
            self.float_x = float(new_pos.x())
            self.float_y = float(new_pos.y())

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and self.dragging:
            self.setCursor(QCursor(Qt.CursorShape.ArrowCursor))
            release_pos = event.globalPosition().toPoint()
            if self.click_pos and (release_pos - self.click_pos).manhattanLength() < 5:
                self.behavior.trigger_happy()
                self.show_heart = True
                self.heart_timer = 25
            self.dragging = False

    def _show_context_menu(self, pos):
        menu = QMenu(self)

        pet_action = QAction("Pet Oreo", self)
        pet_action.triggered.connect(self._pet_oreo)
        menu.addAction(pet_action)

        menu.addSeparator()

        quit_action = QAction("Quit", self)
        quit_action.triggered.connect(QApplication.quit)
        menu.addAction(quit_action)

        menu.exec(pos)

    def _pet_oreo(self):
        self.behavior.trigger_happy()
        self.show_heart = True
        self.heart_timer = 25
