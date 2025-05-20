import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import logging
import os
from pathlib import Path
from typing import Optional, Dict, Any
from dataclasses import dataclass
from autoinput import AutoInput
from sandi import obs, ww, w1w2, ci, awan_lapisan, arah_angin, cm, ch, default_user_input
from user_input import UserInputUpdater
from browsermanager import BrowserManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('autoinput.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class AppConfig:
    """Configuration settings for the application."""
    title: str = "Auto Input BMKG by Zulkiflirmdn"
    window_size: str = "600x400"
    default_user_data_dir: str = str(Path.home() / "Documents" / "autoinput")
    supported_file_types: tuple = (
        ("Excel Files", "*.xlsx;*.xls"),
        ("CSV Files", "*.csv"),
        ("All Files", "*.*")
    )

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

class AutoInputApp(tk.Tk):
    """Main application class for BMKG Auto Input."""
    
    def __init__(self, config: AppConfig = AppConfig()):
        super().__init__()
        self.config = config
        self.browser_manager: Optional[BrowserManager] = None
        
        # Initialize UI
        self._setup_window()
        self._init_variables()
        self._init_browser()
        self._create_widgets()
        
        # Bind cleanup on window close
        self.protocol("WM_DELETE_WINDOW", self.on_exit)

    def _setup_window(self) -> None:
        """Setup the main window properties."""
        self.title(self.config.title)
        self.geometry(self.config.window_size)
        self.configure(padx=20, pady=20)

    def _init_variables(self) -> None:
        """Initialize application variables."""
        self.file_path = tk.StringVar()
        self.jam_terpilih = tk.IntVar(value=0)
        self.status_text = tk.StringVar(value="Ready")

    def _init_browser(self) -> None:
        """Initialize the browser manager."""
        try:
            user_data_dir = FileHandler.ensure_directory_exists(self.config.default_user_data_dir)
            self.browser_manager = BrowserManager(user_data_dir=user_data_dir)
            self.browser_manager.start_browser()
            logger.info("Browser initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize browser: {e}")
            messagebox.showerror("Error", f"Failed to start browser: {e}")

    def _create_widgets(self) -> None:
        """Create and organize all UI widgets."""
        # Main container
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # File selection section
        self._create_file_section(main_frame)
        
        # Time selection section
        self._create_time_section(main_frame)
        
        # Control buttons section
        self._create_control_section(main_frame)
        
        # Status section
        self._create_status_section(main_frame)

    def _create_file_section(self, parent: ttk.Frame) -> None:
        """Create file selection UI elements."""
        file_frame = ttk.LabelFrame(parent, text="File Selection", padding=10)
        file_frame.pack(fill=tk.X, pady=5)

        ttk.Label(file_frame, text="Select File (Excel/CSV):").pack(anchor=tk.W)
        
        file_entry = ttk.Entry(file_frame, textvariable=self.file_path, width=50)
        file_entry.pack(side=tk.LEFT, padx=5, pady=5)
        
        browse_btn = ttk.Button(file_frame, text="Browse", command=self.browse_file)
        browse_btn.pack(side=tk.LEFT, padx=5)

    def _create_time_section(self, parent: ttk.Frame) -> None:
        """Create time selection UI elements."""
        time_frame = ttk.LabelFrame(parent, text="Observation Time", padding=10)
        time_frame.pack(fill=tk.X, pady=5)

        ttk.Label(time_frame, text="Select Observation Hour:").pack(anchor=tk.W)
        
        time_selector = ttk.Combobox(
            time_frame,
            textvariable=self.jam_terpilih,
            values=list(range(24)),
            state="readonly",
            width=10
        )
        time_selector.pack(pady=5)
        time_selector.current(0)

    def _create_control_section(self, parent: ttk.Frame) -> None:
        """Create control buttons section."""
        control_frame = ttk.Frame(parent)
        control_frame.pack(fill=tk.X, pady=10)

        run_btn = ttk.Button(
            control_frame,
            text="Run Auto Input",
            command=self.run_auto_input,
            style="Accent.TButton"
        )
        run_btn.pack(side=tk.LEFT, padx=5)

        reload_btn = ttk.Button(
            control_frame,
            text="Reload Page",
            command=self._reload_browser
        )
        reload_btn.pack(side=tk.LEFT, padx=5)

    def _create_status_section(self, parent: ttk.Frame) -> None:
        """Create status display section."""
        status_frame = ttk.LabelFrame(parent, text="Status", padding=10)
        status_frame.pack(fill=tk.X, pady=5)

        status_label = ttk.Label(
            status_frame,
            textvariable=self.status_text,
            wraplength=500
        )
        status_label.pack(fill=tk.X)

    def browse_file(self) -> None:
        """Open file dialog to select input file."""
        try:
            filename = filedialog.askopenfilename(
                title="Select Excel or CSV File",
                filetypes=self.config.supported_file_types
            )
            if filename:
                self.file_path.set(filename)
                logger.info(f"File selected: {filename}")
                self.status_text.set(f"Selected file: {os.path.basename(filename)}")
        except Exception as e:
            logger.error(f"Error in file selection: {e}")
            messagebox.showerror("Error", f"Error selecting file: {e}")

    def _reload_browser(self) -> None:
        """Reload the browser page."""
        try:
            if self.browser_manager:
                self.browser_manager.reload_browser()
                self.status_text.set("Page reloaded successfully")
                logger.info("Browser page reloaded")
        except Exception as e:
            logger.error(f"Error reloading browser: {e}")
            messagebox.showerror("Error", f"Error reloading page: {e}")

    def run_auto_input(self) -> None:
        """Execute the auto input process."""
        try:
            # Validate file
            FileHandler.validate_file_path(self.file_path.get())
            
            # Update status
            self.status_text.set("Processing input data...")
            self.update_idletasks()

            # Prepare user input
            user_input = default_user_input.copy()
            updater = UserInputUpdater(user_input)
            updated_user_input = updater.update_from_file(
                self.file_path.get(),
                self.jam_terpilih.get(),
                "input_data"
            )

            logger.info("User input updated successfully")

            # Fill form
            if self.browser_manager and self.browser_manager.page:
                form_filler = AutoInput(
                    self.browser_manager.page,
                    updated_user_input,
                    obs, ww, w1w2,
                    awan_lapisan,
                    arah_angin,
                    ci, cm, ch
                )
                form_filler.fill_form()
                
                self.status_text.set("Form filled successfully!")
                messagebox.showinfo("Success", "Form input process completed successfully!")
                logger.info("Form input process completed successfully")
            else:
                raise RuntimeError("Browser not initialized properly")

        except FileNotFoundError as e:
            logger.error(f"File error: {e}")
            messagebox.showerror("Error", str(e))
            self.status_text.set("Error: File not found")
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            messagebox.showerror("Error", f"An unexpected error occurred: {e}")
            self.status_text.set("Error occurred during processing")

    def on_exit(self) -> None:
        """Cleanup resources before exit."""
        try:
            if self.browser_manager:
                self.browser_manager.close_browser()
            logger.info("Application closed successfully")
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
        finally:
            self.quit()

def main():
    """Main entry point of the application."""
    try:
        app = AutoInputApp()
        app.mainloop()
    except Exception as e:
        logger.critical(f"Application failed to start: {e}")
        messagebox.showerror("Critical Error", f"Application failed to start: {e}")

if __name__ == "__main__":
    main()
