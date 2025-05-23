"""
METAR tab UI component.
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox,
    QPushButton, QLabel, QTextEdit, QMessageBox
)
from PyQt6.QtCore import Qt, pyqtSignal
import logging
from ..core.metar_reader import MetarReader
from ..core.metar_processor import MetarProcessor
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

logger = logging.getLogger(__name__)

class MetarTab(QWidget):
    """METAR tab widget for processing METAR codes."""
    
    status_update = pyqtSignal(str)
    
    def __init__(self, browser_manager):
        """Initialize the METAR tab.
        
        Args:
            browser_manager: Browser manager instance
        """
        super().__init__()
        self.browser_manager = browser_manager
        self.setup_ui()
        
    def setup_ui(self):
        """Set up the METAR tab UI."""
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)

        # METAR Input Group
        input_group = QGroupBox("METAR Input")
        input_layout = QVBoxLayout()
        
        # Help text
        help_text = (
            "Enter METAR code below. Example format:\n"
            "WAAA 010500Z 12008KT 9999 FEW018CB SCT025 32/26 Q1008 NOSIG"
        )
        help_label = QLabel(help_text)
        help_label.setStyleSheet("color: #666666;")
        input_layout.addWidget(help_label)
        
        # METAR input field
        self.metar_input = QTextEdit()
        self.metar_input.setPlaceholderText("Enter METAR code here...")
        self.metar_input.setMinimumHeight(100)
        input_layout.addWidget(self.metar_input)
        
        input_group.setLayout(input_layout)
        layout.addWidget(input_group)

        # Control buttons group
        reminder_text = (
            "Pastika Kamu Sudah Berada Pada Halaman METAR \n"
            "https://bmkgsatu.bmkg.go.id/meteorologi/metarspeci"
        )
        control_group = QGroupBox("Controls")
        control_layout = QHBoxLayout()
        
        self.process_btn = QPushButton("Process METAR")
        self.process_btn.setObjectName("success")
        self.process_btn.clicked.connect(self.process_metar)
        self.process_btn.setMinimumHeight(50)
        control_layout.addWidget(self.process_btn)

        reminder_text = QLabel(reminder_text)
        reminder_text.setStyleSheet("color: #666666;")
        input_layout.addWidget(reminder_text)

        control_group.setLayout(control_layout)
        layout.addWidget(control_group)

        # Status group
        status_group = QGroupBox("Status")
        status_layout = QVBoxLayout()
        
        self.status_label = QLabel("Ready")
        self.status_label.setObjectName("progressLabel")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        status_layout.addWidget(self.status_label)
        
        status_group.setLayout(status_layout)
        layout.addWidget(status_group)

        # Add stretch to push everything to the top
        layout.addStretch()

    def reset_to_initial_state(self):
        """Reset the UI to its initial state."""
        self.process_btn.setEnabled(True)
        self.status_label.setText("Ready for next METAR input")
        # Don't clear the input text to allow the user to retry with the same METAR

    def process_metar(self):
        """Process the entered METAR code."""
        try:
            metar_code = self.metar_input.toPlainText().strip()
            if not metar_code:
                QMessageBox.warning(self, "No Input", "Please enter a METAR code.")
                return

            # Parse METAR code
            self.status_label.setText("Parsing METAR code...")
            reader = MetarReader(metar_code)
            metar_data = reader.parse()

            # Get the worker thread from the parent window
            parent_window = self.window()
            if not parent_window or not hasattr(parent_window, 'worker_thread'):
                QMessageBox.warning(self, "Error", "Could not access worker thread.")
                self.reset_to_initial_state()
                return

            # Disable the process button while processing
            self.process_btn.setEnabled(False)

            # Send the METAR processing command to the worker thread
            parent_window.worker_thread.send_command('process_metar', {'metar_data': metar_data})

        except ValueError as e:
            logger.error(f"Invalid METAR code: {e}")
            QMessageBox.critical(self, "Error", f"Invalid METAR code: {str(e)}")
            self.reset_to_initial_state()
        except PlaywrightTimeoutError as e:
            logger.warning(f"Timeout occurred while processing METAR: {e}")
            self.status_label.setText("Timeout occurred - system ready for next input")
            self.reset_to_initial_state()
        except Exception as e:
            logger.error(f"Error processing METAR: {e}")
            QMessageBox.critical(self, "Error", f"Error processing METAR: {str(e)}")
            self.reset_to_initial_state()

    def update_status(self, message: str):
        """Update the status label with a message.
        
        Args:
            message: Status message to display
        """
        self.status_label.setText(message)
        logger.info(message)
        
        # Handle different message types
        if "METAR processed successfully" in message:
            self.process_btn.setEnabled(True)
            self.metar_input.clear()  # Clear input after successful processing
        elif "Error" in message or "Timeout" in message:
            # Show a more user-friendly message for timeouts
            if "Timeout" in message:
                QMessageBox.warning(
                    self,
                    "Timeout Error",
                    "The operation timed out. The system has been reset and is ready for your next METAR input.\n\n"
                    "You can try again with the same METAR code."
                )
            self.reset_to_initial_state() 
            # Show a more user-friendly message for timeouts
            if "Timeout" in message:
                QMessageBox.warning(
                    self,
                    "Timeout Error",
                    "The operation timed out. The system has been reset and is ready for your next METAR input.\n\n"
                    "You can try again with the same METAR code."
                )
            self.reset_to_initial_state() 