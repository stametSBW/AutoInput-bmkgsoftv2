"""
Modern UI implementation for BMKG Auto Input.
"""
import os
import sys
import asyncio
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                            QPushButton, QFileDialog, QLabel, QProgressBar, QMessageBox,
                            QComboBox, QFrame, QGroupBox)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt6.QtGui import QFont, QPalette, QColor
from ..core.browsermanager import BrowserManager
from ..core.fileprocessor import FileProcessor
from ..utils import get_logger

logger = get_logger(__name__)

class WorkerThread(QThread):
    finished = pyqtSignal()
    error = pyqtSignal(str)
    progress = pyqtSignal(int)
    browser_ready = pyqtSignal()
    status_update = pyqtSignal(str)

    def __init__(self, file_path, browser_manager, hour_selected, mode="run"):
        super().__init__()
        self.file_path = file_path
        self.browser_manager = browser_manager
        self.hour_selected = hour_selected
        self.mode = mode  # 'run', 'open', 'reload'
        self.is_running = True

    def run(self):
        try:
            if self.mode == "open":
                self.browser_manager.start_browser()
                self.browser_ready.emit()
                self.finished.emit()
                return
            elif self.mode == "reload":
                self.browser_manager.reload_browser()
                self.finished.emit()
                return
            elif self.mode == "run":
                # Start browser if not already started
                if not self.browser_manager.page:
                    self.browser_manager.start_browser()
                    self.browser_ready.emit()
                # Process the file
                processor = FileProcessor(self.browser_manager)
                processor.process_file(self.file_path, self.hour_selected, self.progress.emit, self.status_update.emit)
                self.finished.emit()
        except Exception as e:
            logger.error(f"Error in worker thread: {e}")
            self.error.emit(str(e))

class ModernApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("BMKG Auto Input")
        self.setGeometry(100, 100, 800, 600)
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f0f0f0;
            }
            QGroupBox {
                font-weight: bold;
                border: 1px solid #cccccc;
                border-radius: 5px;
                margin-top: 1ex;
                padding: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 3px;
            }
            QPushButton {
                background-color: #0078d7;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #106ebe;
            }
            QPushButton:disabled {
                background-color: #cccccc;
            }
            QComboBox {
                padding: 5px;
                border: 1px solid #cccccc;
                border-radius: 3px;
                min-width: 100px;
            }
            QProgressBar {
                border: 1px solid #cccccc;
                border-radius: 3px;
                text-align: center;
                height: 20px;
            }
            QProgressBar::chunk {
                background-color: #0078d7;
            }
        """)
        
        user_data_dir = os.path.join(os.path.expanduser("~"), "bmkg_browser_data")
        self.browser_manager = BrowserManager(user_data_dir)
        self.worker = None
        self.file_path = None
        self.hour_selected = 0
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

        # Control buttons group
        control_group = QGroupBox("Controls")
        control_layout = QHBoxLayout()
        
        self.open_browser_btn = QPushButton("Open Browser")
        self.open_browser_btn.clicked.connect(self.open_browser)
        control_layout.addWidget(self.open_browser_btn)

        self.reload_browser_btn = QPushButton("Reload Browser")
        self.reload_browser_btn.clicked.connect(self.reload_browser)
        control_layout.addWidget(self.reload_browser_btn)

        self.run_btn = QPushButton("Run Auto Input")
        self.run_btn.clicked.connect(self.run_processing)
        control_layout.addWidget(self.run_btn)
        
        control_group.setLayout(control_layout)
        layout.addWidget(control_group)

        # Progress group
        progress_group = QGroupBox("Progress")
        progress_layout = QVBoxLayout()
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        progress_layout.addWidget(self.progress_bar)

        self.status_label = QLabel("Ready")
        self.status_label.setStyleSheet("color: #666666;")
        progress_layout.addWidget(self.status_label)
        
        progress_group.setLayout(progress_layout)
        layout.addWidget(progress_group)

        self.update_button_states()

    def time_changed(self, index):
        self.hour_selected = index

    def select_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Excel File",
            "",
            "Excel Files (*.xlsx *.xls)"
        )
        if file_path:
            self.file_path = file_path
            self.file_label.setText(f"Selected: {os.path.basename(file_path)}")
            self.status_label.setText(f"File selected: {os.path.basename(file_path)}")
        self.update_button_states()

    def open_browser(self):
        self.disable_all_buttons()
        self.status_label.setText("Opening browser...")
        self.worker = WorkerThread(None, self.browser_manager, self.hour_selected, mode="open")
        self.worker.finished.connect(self.open_browser_finished)
        self.worker.error.connect(self.processing_error)
        self.worker.browser_ready.connect(self.browser_ready)
        self.worker.start()

    def open_browser_finished(self):
        self.status_label.setText("Browser opened!")
        self.update_button_states()

    def reload_browser(self):
        self.disable_all_buttons()
        self.status_label.setText("Reloading browser...")
        self.worker = WorkerThread(None, self.browser_manager, self.hour_selected, mode="reload")
        self.worker.finished.connect(self.reload_browser_finished)
        self.worker.error.connect(self.processing_error)
        self.worker.start()

    def reload_browser_finished(self):
        self.status_label.setText("Browser reloaded!")
        self.update_button_states()

    def run_processing(self):
        if not self.file_path:
            QMessageBox.warning(self, "No File", "Please select a file first.")
            return
        self.disable_all_buttons()
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.status_label.setText("Processing...")
        self.worker = WorkerThread(self.file_path, self.browser_manager, self.hour_selected, mode="run")
        self.worker.finished.connect(self.processing_finished)
        self.worker.error.connect(self.processing_error)
        self.worker.progress.connect(self.update_progress)
        self.worker.status_update.connect(self.update_status)
        self.worker.browser_ready.connect(self.browser_ready)
        self.worker.start()

    def processing_finished(self):
        self.progress_bar.setValue(100)
        self.status_label.setText("Processing completed!")
        self.progress_bar.setVisible(False)
        QTimer.singleShot(2000, lambda: self.status_label.setText("Ready"))
        self.update_button_states()

    def processing_error(self, error_msg):
        self.status_label.setText(f"Error: {error_msg}")
        self.progress_bar.setVisible(False)
        QMessageBox.critical(self, "Error", error_msg)
        self.update_button_states()

    def update_progress(self, value):
        self.progress_bar.setValue(value)

    def update_status(self, status):
        self.status_label.setText(status)

    def browser_ready(self):
        self.status_label.setText("Browser ready!")

    def disable_all_buttons(self):
        self.select_file_btn.setEnabled(False)
        self.open_browser_btn.setEnabled(False)
        self.reload_browser_btn.setEnabled(False)
        self.run_btn.setEnabled(False)
        self.time_combo.setEnabled(False)

    def update_button_states(self):
        # Enable Open Browser always
        self.open_browser_btn.setEnabled(True)
        # Enable Reload Browser if browser is open
        self.reload_browser_btn.setEnabled(self.browser_manager.page is not None)
        # Enable Run if file is selected and browser is open
        self.run_btn.setEnabled(self.file_path is not None and self.browser_manager.page is not None)
        # Enable file select always
        self.select_file_btn.setEnabled(True)
        # Enable time selection always
        self.time_combo.setEnabled(True)

    def closeEvent(self, event):
        if self.browser_manager:
            self.browser_manager.close_browser()
        event.accept()

def main():
    app = QApplication(sys.argv)
    window = ModernApp()
    window.show()
    sys.exit(app.exec()) 