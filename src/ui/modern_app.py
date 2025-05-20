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
    QProgressBar, QFrame, QScrollArea, QGroupBox, QCheckBox
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QSettings
from PyQt6.QtGui import QFont, QIcon, QPalette, QColor
from ..core import AutoInput, BrowserManager
from ..data import obs, ww, w1w2, ci, awan_lapisan, arah_angin, cm, ch, default_user_input, UserInputUpdater
from ..utils import get_logger
from ..auto_sender import AutoSender
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
        self.auto_sender = None
        self.auto_send_running = False

    def run(self):
        from ..core import BrowserManager
        while self.running:
            try:
                command, args = self.command_queue.get(timeout=0.1)
            except queue.Empty:
                # Check if auto-send is running and needs to continue
                if self.auto_send_running and self.auto_sender:
                    try:
                        self.auto_sender.start()
                    except Exception as e:
                        self.error.emit(f"Error in auto-send: {str(e)}")
                        self.auto_send_running = False
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
                elif command == 'start_auto_send':
                    if self.browser_manager is None:
                        self.error.emit("Browser not open. Please open the browser first.")
                        continue
                    from ..auto_sender import AutoSender
                    self.auto_sender = AutoSender(page=self.browser_manager.page)
                    self.auto_send_running = True
                    self.progress.emit("Auto-send started")
                    self.finished.emit('start_auto_send')
                elif command == 'stop_auto_send':
                    self.auto_send_running = False
                    self.auto_sender = None
                    self.progress.emit("Auto-send stopped")
                    self.finished.emit('stop_auto_send')
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

class ModernApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("BMKG Auto Input - By Zulkiflirmdn_")
        self.setGeometry(100, 100, 400, 600)
        
        # Set application icon
        icon_path = os.path.join(os.path.dirname(__file__), "assets", "BMKG.ico")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f0f0f0;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #1a237e;  /* BMKG Blue */
                border-radius: 8px;
                margin-top: 1ex;
                padding: 15px;
                background-color: white;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 5px;
                color: #1a237e;  /* BMKG Blue */
            }
            QPushButton {
                padding: 10px 20px;
                border-radius: 5px;
                min-width: 120px;
                font-weight: bold;
            }
            QPushButton#primary {
                background-color: #1a237e;  /* BMKG Blue */
                color: white;
                border: none;
            }
            QPushButton#primary:hover {
                background-color: #283593;
            }
            QPushButton#success {
                background-color: #2e7d32;  /* Green */
                color: white;
                border: none;
            }
            QPushButton#success:hover {
                background-color: #388e3c;
            }
            QPushButton#warning {
                background-color: #f57c00;  /* Orange */
                color: white;
                border: none;
            }
            QPushButton#warning:hover {
                background-color: #fb8c00;
            }
            QPushButton:disabled {
                background-color: #9e9e9e;  /* Grey background */
                color: #e0e0e0;  /* Light grey text */
                border: 1px solid #757575;  /* Darker grey border */
            }
            QComboBox {
                padding: 8px;
                border: 2px solid #1a237e;
                border-radius: 5px;
                min-width: 120px;
                background-color: white;
            }
            QComboBox:hover {
                border-color: #283593;
            }
            QProgressBar {
                border: 2px solid #1a237e;
                border-radius: 5px;
                text-align: center;
                height: 25px;
                background-color: white;
            }
            QProgressBar::chunk {
                background-color: #1a237e;
                border-radius: 3px;
            }
            QLabel {
                color: #1a237e;
            }
        """)
        
        # Initialize settings
        self.settings = QSettings('BMKG', 'AutoInput')
        
        # Initialize browser and worker
        user_data_dir = os.path.join(os.path.expanduser("~"), "bmkg_browser_data")
        self.browser_manager = BrowserManager(user_data_dir)
        self.worker_thread = PersistentWorkerThread(user_data_dir)
        self.worker_thread.progress.connect(self.update_status)
        self.worker_thread.finished.connect(self.worker_finished)
        self.worker_thread.error.connect(self.handle_error)
        self.worker_thread.start()
        
        # Initialize other variables
        self.file_path = None
        self.hour_selected = 0
        self.auto_sender = None
        self.auto_send_thread = None
        self.browser_opened = False
        
        # Setup UI
        self.setup_ui()

    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)

        # File selection group
        file_group = QGroupBox("File Selection")
        file_layout = QVBoxLayout()
        
        self.select_file_btn = QPushButton("Select Excel File")
        self.select_file_btn.setObjectName("primary")
        self.select_file_btn.clicked.connect(self.select_file)
        file_layout.addWidget(self.select_file_btn)

        self.file_label = QLabel("No file selected")
        self.file_label.setStyleSheet("color: #666666;")
        file_layout.addWidget(self.file_label)
        
        file_group.setLayout(file_layout)
        layout.addWidget(file_group)

        # Time selection group
        time_group = QGroupBox("Observation Time")
        time_layout = QVBoxLayout()
        
        time_label = QLabel("Select Observation Hour:")
        time_layout.addWidget(time_label)
        
        self.time_combo = QComboBox()
        self.time_combo.addItems([f"{i:02d}:00" for i in range(24)])
        self.time_combo.currentIndexChanged.connect(self.time_changed)
        time_layout.addWidget(self.time_combo)
        
        time_group.setLayout(time_layout)
        layout.addWidget(time_group)

        # Auto Send Control group
        auto_send_group = QGroupBox("Auto Send Control")
        auto_send_layout = QVBoxLayout()

        # Status label
        self.auto_send_status = QLabel("Auto Send: Tidak Aktif")
        self.auto_send_status.setStyleSheet("color: #666666;")
        auto_send_layout.addWidget(self.auto_send_status)

        # Control buttons
        auto_send_buttons = QHBoxLayout()
        
        self.start_auto_send_btn = QPushButton("Start Auto Send")
        self.start_auto_send_btn.setObjectName("success")
        self.start_auto_send_btn.clicked.connect(self.start_auto_send)
        auto_send_buttons.addWidget(self.start_auto_send_btn)

        self.stop_auto_send_btn = QPushButton("Stop Auto Send")
        self.stop_auto_send_btn.setObjectName("warning")
        self.stop_auto_send_btn.clicked.connect(self.stop_auto_send)
        self.stop_auto_send_btn.setEnabled(False)
        auto_send_buttons.addWidget(self.stop_auto_send_btn)

        auto_send_layout.addLayout(auto_send_buttons)
        auto_send_group.setLayout(auto_send_layout)
        layout.addWidget(auto_send_group)

        # Run Auto Input button
        self.run_btn = QPushButton("Run Auto Input")
        self.run_btn.setObjectName("success")
        self.run_btn.clicked.connect(self.run_processing)
        self.run_btn.setMinimumHeight(50)  # Make it bigger
        layout.addWidget(self.run_btn)
        # Control buttons group
        control_group = QGroupBox("Controls")
        control_layout = QHBoxLayout()
        
        self.open_browser_btn = QPushButton("Open Browser")
        self.open_browser_btn.setObjectName("primary")
        self.open_browser_btn.clicked.connect(self.open_browser)
        control_layout.addWidget(self.open_browser_btn)

        self.reload_browser_btn = QPushButton("Reload Browser")
        self.reload_browser_btn.setObjectName("primary")
        self.reload_browser_btn.clicked.connect(self.reload_browser)
        control_layout.addWidget(self.reload_browser_btn)
        
        control_group.setLayout(control_layout)
        layout.addWidget(control_group)

        # Progress group at the bottom
        progress_group = QGroupBox("Progress")
        progress_layout = QVBoxLayout()
        
        # Status label
        self.status_label = QLabel("Ready")
        self.status_label.setStyleSheet("color: #666666;")
        progress_layout.addWidget(self.status_label)
        
        progress_group.setLayout(progress_layout)
        layout.addWidget(progress_group)

        self.update_button_states()

    def check_browser_open(self):
        """Check if browser is open and show message if not."""
        if not self.browser_opened:
            QMessageBox.warning(
                self,
                "Browser Not Open",
                "Please open the browser first before using this feature!",
                QMessageBox.StandardButton.Ok
            )
            return False
        return True

    def start_auto_send(self):
        """Start the auto-send process."""
        if not self.check_browser_open():
            return
        try:
            self.worker_thread.send_command('start_auto_send')
            self.auto_send_status.setText("Auto Send: Aktif")
            self.start_auto_send_btn.setEnabled(False)
            self.stop_auto_send_btn.setEnabled(True)
            logger.info("Auto-send process started")
        except Exception as e:
            logger.error(f"Failed to start auto-send: {e}")
            QMessageBox.critical(self, "Error", f"Failed to start auto-send: {str(e)}")

    def stop_auto_send(self):
        """Stop the auto-send process."""
        if not self.check_browser_open():
            return
        try:
            self.worker_thread.send_command('stop_auto_send')
            self.auto_send_status.setText("Auto Send: Tidak Aktif")
            self.start_auto_send_btn.setEnabled(True)
            self.stop_auto_send_btn.setEnabled(False)
            logger.info("Auto-send process stopped")
        except Exception as e:
            logger.error(f"Error stopping auto-send: {e}")
            QMessageBox.critical(self, "Error", f"Error stopping auto-send: {str(e)}")

    def closeEvent(self, event):
        """Handle window close event."""
        try:
            self.stop_auto_send()
            if self.worker_thread:
                self.worker_thread.send_command('close')
                self.worker_thread.wait()
            if self.browser_manager:
                self.browser_manager.close_browser()
            logger.info("Application closed successfully")
        except Exception as e:
            logger.error(f"Error during application closure: {e}")
        event.accept()

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
                self.file_path = file_path
                self.file_label.setText(file_path)
                logger.info(f"File dipilih: {file_path}")
        except Exception as e:
            logger.error(f"Error memilih file: {e}")
            QMessageBox.critical(self, "Error", f"Error memilih file: {e}")

    def time_changed(self, index):
        self.hour_selected = index

    def open_browser(self):
        self.worker_thread.send_command('open')
        self.disable_all_buttons()

    def reload_browser(self):
        if self.check_browser_open():
            self.worker_thread.send_command('reload')
            self.disable_all_buttons()

    def disable_all_buttons(self):
        self.start_auto_send_btn.setEnabled(False)
        self.stop_auto_send_btn.setEnabled(False)
        self.select_file_btn.setEnabled(False)
        self.time_combo.setEnabled(False)
        self.reload_browser_btn.setEnabled(False)
        self.open_browser_btn.setEnabled(False)

    def run_processing(self):
        if not self.check_browser_open():
            return
        try:
            FileHandler.validate_file_path(self.file_label.text())
            selected_time = int(self.time_combo.currentText().split(":")[0])
            updater = UserInputUpdater(default_user_input.copy())
            user_input = updater.update_from_file(
                self.file_label.text(),
                selected_time,
                "input_data"
            )
            self.worker_thread.send_command('fill', {'user_input': user_input})
            self.disable_all_buttons()
        except Exception as e:
            logger.error(f"Failed to start process: {e}")
            QMessageBox.critical(self, "Error", f"Failed to start process: {str(e)}")

    def worker_finished(self, action):
        """Handle worker thread completion."""
        if action == 'open':
            self.browser_opened = True
            self.progress_bar.setValue(100)
            QMessageBox.information(self, "Sukses", "Browser dibuka dan siap digunakan!")
        elif action == 'fill':
            self.progress_bar.setValue(100)
            QMessageBox.information(self, "Sukses", "Form berhasil diisi!")
        elif action == 'reload':
            self.progress_bar.setValue(100)
            QMessageBox.information(self, "Sukses", "Halaman berhasil dimuat ulang!")
        elif action == 'start_auto_send':
            self.progress_bar.setValue(0)
            QMessageBox.information(self, "Sukses", "Auto-send berhasil dimulai!")
        elif action == 'stop_auto_send':
            self.progress_bar.setValue(0)
            QMessageBox.information(self, "Sukses", "Auto-send berhasil dihentikan!")
        elif action == 'close':
            self.browser_opened = False
            self.progress_bar.setValue(0)
            QMessageBox.information(self, "Info", "Browser ditutup.")
        self.update_button_states()

    def handle_error(self, error_message):
        """Handle process errors."""
        logger.error(f"Proses gagal: {error_message}")
        QMessageBox.critical(self, "Error", f"Proses gagal: {error_message}")
        self.update_button_states()

    def update_status(self, message):
        """Update the status label and progress bar with the given message."""
        if hasattr(self, 'status_label'):
            self.status_label.setText(message)
            
            # Update progress bar based on message content
            if "Waiting" in message and "seconds" in message:
                # Extract seconds from message
                try:
                    seconds = int(message.split("seconds")[0].split("Waiting")[1].strip())
                    # Calculate progress (assuming max wait is 3600 seconds)
                    progress = min(100, int((3600 - seconds) / 3600 * 100))
                    self.progress_bar.setValue(progress)
                except:
                    pass
            elif "Completed" in message:
                self.progress_bar.setValue(100)
            elif "Starting" in message:
                self.progress_bar.setValue(0)
            
        logger.info(message)

    def update_button_states(self):
        """Update the state of all buttons based on current conditions."""
        # Enable Open Browser always
        self.open_browser_btn.setEnabled(True)
        # Enable Reload Browser if browser is open
        self.reload_browser_btn.setEnabled(self.browser_opened)
        # Enable Run if file is selected and browser is open
        self.run_btn.setEnabled(self.file_path is not None and self.browser_opened)
        # Enable file select always
        self.select_file_btn.setEnabled(True)
        # Enable time selection always
        self.time_combo.setEnabled(True)
        # Auto Sender controls
        auto_sender_running = self.worker_thread.auto_send_running if hasattr(self.worker_thread, 'auto_send_running') else False
        self.start_auto_send_btn.setEnabled(self.browser_opened and not auto_sender_running)
        self.stop_auto_send_btn.setEnabled(auto_sender_running)

def main():
    """Run the application."""
    try:
        app = QApplication(sys.argv)
        window = ModernApp()
        window.show()
        sys.exit(app.exec())
    except Exception as e:
        logger.critical(f"Aplikasi gagal dimulai: {e}")
        QMessageBox.critical(None, "Error Kritis", f"Aplikasi gagal dimulai: {e}") 