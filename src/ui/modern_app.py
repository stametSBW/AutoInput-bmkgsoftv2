"""
Modern UI implementation for BMKG Auto Input menggunakan PyQt6.
"""
import sys
import os
import logging
from pathlib import Path
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QFileDialog, QComboBox, QMessageBox,
    QProgressBar, QFrame, QScrollArea, QGroupBox
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QSettings
from PyQt6.QtGui import QFont, QIcon, QPalette, QColor
from ..core import AutoInput, BrowserManager
from ..data import obs, ww, w1w2, ci, awan_lapisan, arah_angin, cm, ch, default_user_input, UserInputUpdater
from ..utils import get_logger
import queue

# Configure logging
logger = get_logger(__name__)

class FileHandler:
    """Handles file operations and validation."""
    
    @staticmethod
    def validate_file_path(file_path: str) -> None:
        """Validate if the file path exists and is accessible."""
        if not file_path or not os.path.exists(file_path):
            raise FileNotFoundError(f"File {file_path} not found.")
        
        if not os.access(file_path, os.R_OK):
            raise PermissionError(f"No permission to read file: {file_path}")

    @staticmethod
    def ensure_directory_exists(directory: str) -> str:
        """Ensure the directory exists, create if it doesn't."""
        path = Path(directory)
        path.mkdir(parents=True, exist_ok=True)
        return str(path)

class PersistentWorkerThread(QThread):
    progress = pyqtSignal(str)
    finished = pyqtSignal(str)
    error = pyqtSignal(str)

    def __init__(self, user_data_dir):
        super().__init__()
        self.user_data_dir = user_data_dir
        self.command_queue = queue.Queue()
        self.browser_manager = None
        self.running = True

    def run(self):
        from ..core import BrowserManager
        while self.running:
            try:
                command, args = self.command_queue.get(timeout=0.1)
            except queue.Empty:
                continue
            try:
                if command == 'open':
                    if self.browser_manager is None:
                        self.progress.emit("Opening browser...")
                        self.browser_manager = BrowserManager(user_data_dir=self.user_data_dir)
                        self.browser_manager.start_browser()
                        self.browser_manager.navigate_to_form()
                        self.progress.emit("Browser opened and form loaded!")
                        self.finished.emit('open')
                    else:
                        self.progress.emit("Browser already open.")
                        self.finished.emit('open')
                elif command == 'fill':
                    user_input = args.get('user_input')
                    if self.browser_manager is None:
                        self.error.emit("Browser not open. Please open the browser first.")
                        continue
                    self.progress.emit("Filling form...")
                    from ..core import AutoInput
                    from ..data import obs, ww, w1w2, ci, awan_lapisan, arah_angin, cm, ch
                    auto_input = AutoInput(
                        self.browser_manager.page,
                        user_input,
                        obs, ww, w1w2, awan_lapisan, arah_angin, ci, cm, ch
                    )
                    auto_input.fill_form()
                    self.progress.emit("Form filled successfully!")
                    self.finished.emit('fill')
                elif command == 'reload':
                    if self.browser_manager is None:
                        self.error.emit("Browser not open. Please open the browser first.")
                        continue
                    self.progress.emit("Refreshing page...")
                    self.browser_manager.page.reload()
                    self.progress.emit("Page refreshed successfully!")
                    self.finished.emit('reload')
                elif command == 'close':
                    if self.browser_manager:
                        self.browser_manager.close_browser()
                        self.browser_manager = None
                    self.running = False
                    self.progress.emit("Browser closed.")
                    self.finished.emit('close')
            except Exception as e:
                import traceback
                traceback.print_exc()
                self.error.emit(str(e))

    def send_command(self, command, args=None):
        if args is None:
            args = {}
        self.command_queue.put((command, args))

class ModernAutoInputApp(QMainWindow):
    """Modern UI implementation for BMKG Auto Input."""
    
    def __init__(self):
        super().__init__()
        self.worker_thread = None
        self.default_user_data_dir = str(Path.home() / "Documents" / "autoinput")
        self.settings = QSettings('BMKG', 'AutoInput')
        self.init_ui()
        self.start_worker()

    def init_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle("BMKG Auto Input")
        self.setMinimumSize(600, 400)
        
        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # File selection section
        file_group = QGroupBox("Pilihan File")
        file_layout = QVBoxLayout()
        
        self.file_path_label = QLabel("Belum ada file dipilih")
        self.file_path_label.setWordWrap(True)
        self.select_file_button = QPushButton("Pilih File Excel")
        self.select_file_button.clicked.connect(self.select_file)
        
        file_layout.addWidget(self.file_path_label)
        file_layout.addWidget(self.select_file_button)
        file_group.setLayout(file_layout)
        
        # Time selection section
        time_group = QGroupBox("Pilihan Waktu")
        time_layout = QVBoxLayout()
        
        self.time_combo = QComboBox()
        self.time_combo.addItems([f"{hour:02d}:00" for hour in range(24)])
        
        time_layout.addWidget(self.time_combo)
        time_group.setLayout(time_layout)
        
        # Progress section
        progress_group = QGroupBox("Status")
        progress_layout = QVBoxLayout()
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setTextVisible(False)
        self.progress_label = QLabel("Siap")
        
        progress_layout.addWidget(self.progress_bar)
        progress_layout.addWidget(self.progress_label)
        progress_group.setLayout(progress_layout)
        
        # Control buttons
        button_layout = QHBoxLayout()
        
        self.open_browser_button = QPushButton("Buka Browser")
        self.open_browser_button.clicked.connect(self.open_browser)
        self.open_browser_button.setStyleSheet("""
            QPushButton { background-color: #FFC107; color: black; border: none; padding: 8px 16px; border-radius: 4px; }
            QPushButton:hover { background-color: #ffb300; }
            QPushButton:disabled { background-color: #cccccc; }
        """)
        
        self.start_button = QPushButton("Jalankan")
        self.start_button.clicked.connect(self.start_process)
        self.start_button.setStyleSheet("""
            QPushButton { background-color: #4CAF50; color: white; border: none; padding: 8px 16px; border-radius: 4px; }
            QPushButton:hover { background-color: #45a049; }
            QPushButton:disabled { background-color: #cccccc; }
        """)
        
        self.reload_button = QPushButton("Muat Ulang")
        self.reload_button.clicked.connect(self.reload_browser)
        self.reload_button.setStyleSheet("""
            QPushButton { background-color: #2196F3; color: white; border: none; padding: 8px 16px; border-radius: 4px; }
            QPushButton:hover { background-color: #0b7dda; }
            QPushButton:disabled { background-color: #cccccc; }
        """)
        
        button_layout.addWidget(self.open_browser_button)
        button_layout.addWidget(self.start_button)
        button_layout.addWidget(self.reload_button)
        
        # Add all sections to main layout
        layout.addWidget(file_group)
        layout.addWidget(time_group)
        layout.addWidget(progress_group)
        layout.addLayout(button_layout)
        
        # Set window style
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f5f5;
            }
            QGroupBox {
                font-weight: bold;
                border: 1px solid #cccccc;
                border-radius: 6px;
                margin-top: 6px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 3px 0 3px;
            }
            QLabel {
                color: #333333;
            }
            QComboBox {
                padding: 5px;
                border: 1px solid #cccccc;
                border-radius: 4px;
                background-color: white;
            }
            QProgressBar {
                border: 1px solid #cccccc;
                border-radius: 4px;
                text-align: center;
                background-color: #f0f0f0;
            }
            QProgressBar::chunk {
                background-color: #4CAF50;
                border-radius: 3px;
            }
        """)

    def select_file(self):
        """Handle file selection."""
        try:
            # Get the last used directory from settings, or use home directory if not set
            last_dir = self.settings.value('last_directory', str(Path.home()))
            
            file_path, _ = QFileDialog.getOpenFileName(
                self,
                "Pilih File Excel",
                last_dir,
                "File Excel (*.xls *.xlsx)"
            )
            if file_path:
                # Save the directory of the selected file for next time
                self.settings.setValue('last_directory', str(Path(file_path).parent))
                self.file_path_label.setText(file_path)
                logger.info(f"File dipilih: {file_path}")
        except Exception as e:
            logger.error(f"Error memilih file: {e}")
            QMessageBox.critical(self, "Error", f"Error memilih file: {e}")

    def start_worker(self):
        self.worker_thread = PersistentWorkerThread(self.default_user_data_dir)
        self.worker_thread.progress.connect(self.update_progress)
        self.worker_thread.finished.connect(self.worker_finished)
        self.worker_thread.error.connect(self.handle_error)
        self.worker_thread.start()

    def open_browser(self):
        self.worker_thread.send_command('open')
        self.disable_all_buttons()

    def start_process(self):
        try:
            FileHandler.validate_file_path(self.file_path_label.text())
            selected_time = int(self.time_combo.currentText().split(":")[0])
            updater = UserInputUpdater(default_user_input.copy())
            user_input = updater.update_from_file(
                self.file_path_label.text(),
                selected_time,
                "input_data"
            )
            self.worker_thread.send_command('fill', {'user_input': user_input})
            self.disable_all_buttons()
        except Exception as e:
            logger.error(f"Failed to start process: {e}")
            QMessageBox.critical(self, "Error", f"Failed to start process: {str(e)}")

    def reload_browser(self):
        self.worker_thread.send_command('reload')
        self.disable_all_buttons()

    def worker_finished(self, action):
        if action == 'open':
            QMessageBox.information(self, "Sukses", "Browser dibuka dan siap digunakan!")
        elif action == 'fill':
            QMessageBox.information(self, "Sukses", "Form berhasil diisi!")
        elif action == 'reload':
            QMessageBox.information(self, "Sukses", "Halaman berhasil dimuat ulang!")
        elif action == 'close':
            QMessageBox.information(self, "Info", "Browser ditutup.")
        self.reset_ui()

    def disable_all_buttons(self):
        self.start_button.setEnabled(False)
        self.select_file_button.setEnabled(False)
        self.time_combo.setEnabled(False)
        self.reload_button.setEnabled(False)
        self.open_browser_button.setEnabled(False)

    def handle_error(self, error_message):
        """Handle process errors."""
        logger.error(f"Proses gagal: {error_message}")
        QMessageBox.critical(self, "Error", f"Proses gagal: {error_message}")
        self.reset_ui()

    def reset_ui(self):
        """Reset UI to initial state."""
        self.start_button.setEnabled(True)
        self.select_file_button.setEnabled(True)
        self.time_combo.setEnabled(True)
        self.reload_button.setEnabled(True)
        self.open_browser_button.setEnabled(True)
        self.progress_bar.setValue(0)
        self.progress_label.setText("Siap")

    def update_progress(self, message):
        """Update progress information."""
        self.progress_label.setText(message)
        if "successfully" in message.lower():
            self.progress_bar.setValue(100)
        elif "filling" in message.lower():
            self.progress_bar.setValue(75)
        elif "navigating" in message.lower():
            self.progress_bar.setValue(50)
        elif "initializing" in message.lower():
            self.progress_bar.setValue(25)
        elif "refreshing" in message.lower():
            self.progress_bar.setValue(50)

    def closeEvent(self, event):
        """Handle application closure."""
        try:
            self.reset_ui()
            logger.info("Aplikasi ditutup dengan sukses")
        except Exception as e:
            logger.error(f"Error saat pembersihan: {e}")
        event.accept()

def main():
    """Run the application."""
    try:
        app = QApplication(sys.argv)
        window = ModernAutoInputApp()
        window.show()
        sys.exit(app.exec())
    except Exception as e:
        logger.critical(f"Aplikasi gagal dimulai: {e}")
        QMessageBox.critical(None, "Error Kritis", f"Aplikasi gagal dimulai: {e}") 