"""Main pet widget — transparent floating window displaying Oreo's sprite sheet."""

import os
import sys
from PIL import Image
from PyQt6.QtCore import Qt, QTimer, QPoint, QRectF, QUrl
from PyQt6.QtGui import QPixmap, QPainter, QIcon, QAction, QCursor, QColor, QPen, QFont, QImage, QTransform
from PyQt6.QtMultimedia import QSoundEffect
from PyQt6.QtWidgets import QWidget, QMenu, QSystemTrayIcon, QApplication

from behaviors import FloatingBehavior, State

if getattr(sys, "_MEIPASS", None):
    RESOURCE_DIR = sys._MEIPASS
else:
    RESOURCE_DIR = os.path.dirname(__file__)

FRAMES_DIR = os.path.join(RESOURCE_DIR, "frames")
FRAMES_WALK_DIR = os.path.join(FRAMES_DIR, "walking3")
FRAMES_TRANSITION_DIR = os.path.join(FRAMES_DIR, "walking-to-stretching")
FRAMES_STRETCH_DIR = os.path.join(FRAMES_DIR, "stretching")
STRETCH_SOUND_PATH = os.path.join(RESOURCE_DIR, "audio", "stretch.wav")

PET_SIZE = 150
WALK_ANIM_SPEED = 8
STRETCH_ANIM_SPEED = 4


def _pil_to_qpixmap(img):
    """Convert a PIL RGBA image to QPixmap."""
    data = img.tobytes("raw", "RGBA")
    qimg = QImage(data, img.width, img.height, 4 * img.width, QImage.Format.Format_RGBA8888)
    return QPixmap.fromImage(qimg.copy())


class PetWidget(QWidget):
    def __init__(self, sound_enabled=False):
        super().__init__()
        self.sound_enabled = sound_enabled
        self._setup_window()
        self._load_frames()
        self._load_sounds()
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
        self.stretch_frame_index = 0
        self.stretch_frame_counter = 0
        self._flipped_cache = {}
        self.show_heart = False
        self.heart_timer = 0

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
        """Load walking, transition, and stretching frames at Retina resolution."""
        dpr = QApplication.primaryScreen().devicePixelRatio()
        load_size = int(PET_SIZE * dpr)

        self.walk_frames = []
        for i in [1, 2, 3, 4]:
            path = os.path.join(FRAMES_WALK_DIR, f"frame_{i}.png")
            img = Image.open(path).convert("RGBA")
            img.thumbnail((load_size, load_size), Image.LANCZOS)
            pixmap = _pil_to_qpixmap(img)
            pixmap.setDevicePixelRatio(dpr)
            self.walk_frames.append(pixmap)

        # Stretch sequence: transition frame 2, 3 then stretch frame 1, 2
        padded_size = int(load_size * 0.85)
        self.stretch_seq = []
        for i in [2, 3]:
            path = os.path.join(FRAMES_TRANSITION_DIR, f"frame_{i}.png")
            img = Image.open(path).convert("RGBA")
            img.thumbnail((padded_size, padded_size), Image.LANCZOS)
            pixmap = _pil_to_qpixmap(img)
            pixmap.setDevicePixelRatio(dpr)
            self.stretch_seq.append(pixmap)
        for i in [1, 2, 2, 2]:
            path = os.path.join(FRAMES_STRETCH_DIR, f"frame_{i}.png")
            img = Image.open(path).convert("RGBA")
            img.thumbnail((padded_size, padded_size), Image.LANCZOS)
            pixmap = _pil_to_qpixmap(img)
            pixmap.setDevicePixelRatio(dpr)
            self.stretch_seq.append(pixmap)

    def _load_sounds(self):
        if not self.sound_enabled:
            self.stretch_sound = None
            return
        self.stretch_sound = QSoundEffect(self)
        self.stretch_sound.setSource(QUrl.fromLocalFile(STRETCH_SOUND_PATH))
        self.stretch_sound.setVolume(0.01)

    def _setup_behavior(self):
        self.behavior = FloatingBehavior(self.screen_width, self.screen_height, PET_SIZE)

    def _setup_animation(self):
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._tick)
        self.timer.start(50)

    def _setup_tray(self):
        icon = QIcon(self.walk_frames[0])

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

        if self.behavior.state == State.WALK:
            self.walk_frame_counter += 1
            if self.walk_frame_counter >= WALK_ANIM_SPEED:
                self.walk_frame_counter = 0
                self.walk_frame_index = (self.walk_frame_index + 1) % len(self.walk_frames)
        else:
            self.stretch_frame_counter += 1
            if self.stretch_frame_counter >= STRETCH_ANIM_SPEED:
                self.stretch_frame_counter = 0
                self.stretch_frame_index += 1
                if self.stretch_frame_index >= len(self.stretch_seq):
                    self.stretch_frame_index = 0
                    self.behavior.end_stretch()

        if self.show_heart:
            self.heart_timer -= 1
            if self.heart_timer <= 0:
                self.show_heart = False

        self.update()

    def _get_current_pixmap(self, flip=False):
        if self.behavior.state == State.WALK:
            pixmap = self.walk_frames[self.walk_frame_index]
            cache_key = ("walk", self.walk_frame_index, flip)
        else:
            pixmap = self.stretch_seq[self.stretch_frame_index]
            cache_key = ("stretch", self.stretch_frame_index, flip)

        if flip:
            if cache_key not in self._flipped_cache:
                self._flipped_cache[cache_key] = pixmap.transformed(QTransform().scale(-1, 1))
            return self._flipped_cache[cache_key]
        return pixmap

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)

        flip = self.behavior.direction < 0
        pixmap = self._get_current_pixmap(flip=flip)

        dpr = pixmap.devicePixelRatio()
        logical_w = int(pixmap.width() / dpr)
        logical_h = int(pixmap.height() / dpr)
        x = (PET_SIZE - logical_w) // 2
        y = (PET_SIZE - logical_h) // 2
        painter.drawPixmap(x, y, logical_w, logical_h, pixmap)

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
                self._trigger_stretch()
            self.dragging = False

    def _trigger_stretch(self):
        self.behavior.trigger_stretch()
        self.stretch_frame_index = 0
        self.stretch_frame_counter = 0
        self.show_heart = True
        self.heart_timer = 25
        if self.stretch_sound is not None:
            self.stretch_sound.play()

    def _show_context_menu(self, pos):
        menu = QMenu(self)

        pet_action = QAction("Pet Oreo", self)
        pet_action.triggered.connect(self._trigger_stretch)
        menu.addAction(pet_action)

        menu.addSeparator()

        quit_action = QAction("Quit", self)
        quit_action.triggered.connect(QApplication.quit)
        menu.addAction(quit_action)

        menu.exec(pos)
