import pandas as pd
from .sandi import default_user_input


class UserInputUpdater:
    def __init__(self, user_input):
        """
        Inisialisasi dengan data `user_input` yang akan di-update.

        Args:
            user_input (dict): Dictionary berisi data user_input yang akan diperbarui.
        """
        self.user_input = user_input

    def update_from_file(self, file_path, jam_terpilih, sheet_name=None):
        """
        Update user_input dari file Excel atau CSV berdasarkan jam terpilih.

        Args:
            file_path (str): Path ke file (Excel atau CSV).
            jam_terpilih (int): Jam pengamatan yang ingin diperbarui.

        Returns:
            dict: Dictionary user_input yang sudah diperbarui.
            :param jam_terpilih:
            :param file_path:
            :param sheet_name:
        """
        # Tentukan format file (CSV atau Excel)
        if file_path.endswith('.csv'):
            data = pd.read_csv(file_path)
        else:
            data = pd.read_excel(file_path, sheet_name=sheet_name)

        # Cari baris yang sesuai dengan jam terpilih
        row = data[data['Jam'] == jam_terpilih]

        if row.empty:
            raise ValueError(f"Jam {jam_terpilih} tidak ditemukan di file.")

        # Parameter yang harus memiliki satu angka di belakang koma
        decimal_keys = [
            'lama_penyinaran', 'suhu_bola_kering', 'suhu_bola_basah',
            'suhu_maksimum', 'suhu_minimum', 'tekanan_qff', 'tekanan_qfe',
            'penguapan', 'hujan_ditakar'
        ]

        # Update user_input dengan data dari row yang ditemukan
        for key in self.user_input:
            if key in row.columns:
                value = row.iloc[0][key]
                # Jika key berada di daftar parameter yang memerlukan satu angka di belakang koma
                if key in decimal_keys:
                    try:
                        if pd.notna(value):  # Pastikan nilai bukan NaN
                            # Konversi ke float lalu ke string dengan satu angka desimal
                            self.user_input[key] = f"{float(value):.1f}"
                        else:
                            self.user_input[key] = "0.0"  # Jika NaN, set ke 0.0
                    except (ValueError, TypeError):
                        # Jika konversi gagal, set nilai default 0.0
                        self.user_input[key] = "0.0"
                else:
                    # Untuk kunci lainnya, jika NaN maka jadikan string kosong
                    if pd.notna(value):
                        if pd.api.types.is_numeric_dtype(value):
                            # Konversi nilai menjadi integer jika mungkin
                            self.user_input[key] = str(int(float(value)))  # Konversi ke int tanpa desimal
                        else:
                            self.user_input[key] = str(value)  # Konversi nilai non-numerik menjadi string
                    else:
                        self.user_input[key] = ""  # Jika NaN, jadikan string kosong

        return self.user_input
