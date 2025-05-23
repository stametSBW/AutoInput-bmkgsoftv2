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
        control_group = QGroupBox("Controls")
        control_layout = QHBoxLayout()
        
        self.process_btn = QPushButton("Process METAR")
        self.process_btn.setObjectName("success")
        self.process_btn.clicked.connect(self.process_metar)
        self.process_btn.setMinimumHeight(50)
        control_layout.addWidget(self.process_btn)
        
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

            # Check if browser is available
            if not self.browser_manager or not self.browser_manager.page:
                QMessageBox.warning(self, "Browser Not Ready", "Please open the browser first.")
                return

            # Process the METAR data
            self.status_label.setText("Processing METAR data...")
            processor = MetarProcessor(self.browser_manager.page)
            processor.fill_form(metar_data)

            # Update status
            self.status_label.setText("METAR processed successfully!")
            QMessageBox.information(self, "Success", "METAR code processed successfully!")

        except ValueError as e:
            logger.error(f"Invalid METAR code: {e}")
            QMessageBox.critical(self, "Error", f"Invalid METAR code: {str(e)}")
            self.status_label.setText("Error: Invalid METAR code")
        except Exception as e:
            logger.error(f"Error processing METAR: {e}")
            QMessageBox.critical(self, "Error", f"Error processing METAR: {str(e)}")
            self.status_label.setText("Error processing METAR")

    def update_status(self, message: str):
        """Update the status label.
        
        Args:
            message: Status message to display
        """
        self.status_label.setText(message) 