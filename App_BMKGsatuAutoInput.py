import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
from autoinput import AutoInput
from sandi import obs, ww, w1w2, ci, awan_lapisan, arah_angin, cm, ch, default_user_input
from user_input import UserInputUpdater
from browsermanager import BrowserManager
import logging
import os

# fungsi helper
def validate_file_path(file_path):
    """Validasi apakah path file ada dan benar."""
    if not file_path or not os.path.exists(file_path):
        raise FileNotFoundError(f"File {file_path} not found.")


def get_default_user_data_dir():
    """Get or create default user data directory."""
    user_data_dir = 'C:/Users/Administrator/Documents/autoinput'
    if not os.path.exists(user_data_dir):
        os.makedirs(user_data_dir)
    return user_data_dir


class Application(tk.Tk):
    def __init__(self):
        super().__init__()
        self.browser_manager = None
        self.title("Auto Input BMKG by Zulkiflirmdn")
        self.geometry("400x300")

        # Variables
        self.file_path = tk.StringVar()
        self.jam_terpilih = tk.IntVar(value=0)

        # Inisialisasi browser manager
        self.init_browser()

        # Create Widgets
        self.create_widgets()

    def init_browser(self):
        """Initialize the browser manager asynchronously."""
        try:
            self.browser_manager = BrowserManager(user_data_dir=get_default_user_data_dir())
            self.browser_manager.start_browser()
        except Exception as e:
            logging.error(f"Failed to start browser: {e}")
            messagebox.showerror("Error", f"Error starting browser: {e}")

    def create_widgets(self):
        """Create UI components."""
        self.create_file_selection_ui()
        self.create_time_selection_ui()
        self.create_run_button()

    def create_file_selection_ui(self):
        """Create UI elements for file selection."""
        file_label = tk.Label(self, text="Pilih File (Excel/CSV):")
        file_label.pack(pady=10)

        file_entry = tk.Entry(self, textvariable=self.file_path, width=40)
        file_entry.pack(pady=5)

        browse_button = tk.Button(self, text="Browse", command=self.browse_file)
        browse_button.pack(pady=5)

    def create_time_selection_ui(self):
        """Create UI elements for selecting observation time."""
        jam_label = tk.Label(self, text="Pilih Jam Pengamatan:")
        jam_label.pack(pady=10)

        jam_selector = ttk.Combobox(self, textvariable=self.jam_terpilih, values=list(range(24)), state="readonly")
        jam_selector.pack(pady=5)
        jam_selector.current(0)

    def create_run_button(self):
        """Create the 'Run' and 'Refresh web' button that starts the auto input process and reload the page."""
        # Create a frame to hold the buttons
        button_frame = tk.Frame(self)
        button_frame.pack(pady=20)  # Add padding to the frame

        # Run Button
        run_button = tk.Button(button_frame, text="Run", command=self.run_auto_input)
        run_button.pack(side=tk.LEFT, padx=10)  # Add padding to the left and right

        # Refresh Button
        reload_button = tk.Button(button_frame, text="Reload Page", command=self.browser_manager.reload_browser)
        reload_button.pack(side=tk.LEFT, padx=10)  # Add padding between buttons

    def browse_file(self):
        """Buka dialog untuk memilih file Excel atau CSV."""
        filename = filedialog.askopenfilename(
            title="Pilih File Excel atau CSV",
            filetypes=(("Excel Files", "*.xlsx;*.xls"), ("CSV Files", "*.csv"), ("All Files", "*.*"))
        )
        self.file_path.set(filename)
        logging.info(f"File selected: {filename}")

    def run_auto_input(self):
        """Jalankan proses input otomatis setelah memvalidasi input file."""
        try:
            # Validasi path file menggunakan the helper method
            validate_file_path(self.file_path.get())

            # Default user input untuk testing (can be updated)
            user_input = default_user_input.copy()

            # Perbarui user_input dari file yang dipilih
            updater = UserInputUpdater(user_input)
            sheet_name = "input_data"
            updated_user_input = updater.update_from_file(self.file_path.get(), self.jam_terpilih.get(), sheet_name)

            logging.info(f"User input after update: {updated_user_input}")

            # Mulai isi formulir dengan input_pengguna yang diperbarui
            form_filler = AutoInput(self.browser_manager.page, updated_user_input, obs, ww, w1w2, awan_lapisan, arah_angin, ci, cm, ch)
            form_filler.fill_form()

            messagebox.showinfo("Success", "Proses input form selesai!")
            logging.info("Form input process completed successfully.")

        except FileNotFoundError as e:
            messagebox.showerror("Error", str(e))
            logging.error(f"File error: {e}")
        except Exception as e:
            logging.error(f"Unexpected error: {e}")
            messagebox.showerror("Error", f"An unexpected error occurred: {e}")

    def on_exit(self):
        """Cleanup on exit."""
        self.browser_manager.close_browser()
        logging.info("Application closed.")


if __name__ == "__main__":
    app = Application()
    # app.protocol("WM_DELETE_WINDOW", app.on_exit)
    app.mainloop()
