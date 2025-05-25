import os
import re
import sys
from pathlib import Path
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QPushButton, QFileDialog, QListWidget, QLabel)
from PyQt6.QtCore import Qt

class AdUnitSearchWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AdMob AdUnit Search")
        self.setGeometry(100, 100, 600, 400)

        # Define the AdMob AdUnit pattern
        self.admob_pattern = r"ca-app-pub-\d{16}/\d+"
        self.supported_extensions = ['.xml', '.java', '.kt', '.txt', '.json', 
                                  '.yml', '.yaml', '.dex', '.smali', '.so']

        # Setup UI
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        # Select directory button
        self.select_dir_btn = QPushButton("Select Decompiled APK Directory")
        self.select_dir_btn.clicked.connect(self.select_directory)
        self.layout.addWidget(self.select_dir_btn)

        # Status label
        self.status_label = QLabel("Please select a directory to search.")
        self.layout.addWidget(self.status_label)

        # Result list
        self.result_list = QListWidget()
        self.layout.addWidget(self.result_list)

    def select_directory(self):
        """Open a dialog to select the decompiled APK directory."""
        directory = QFileDialog.getExistingDirectory(self, "Select Decompiled APK Directory")
        if directory:
            self.status_label.setText(f"Searching in {directory}...")
            self.result_list.clear()
            self.search_adunits_in_directory(directory)

    def search_adunits_in_file(self, file_path):
        """Search for AdMob AdUnit IDs in a single file."""
        try:
            # Handle binary files (.dex, .smali, .so) and text files differently
            if file_path.suffix in ['.dex', '.so']:
                with open(file_path, 'rb') as file:
                    content = file.read().decode('utf-8', errors='ignore')
            else:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
                    content = file.read()
            
            matches = re.finditer(self.admob_pattern, content)
            results = [(match.group(), content.count(match.group())) for match in matches]
            return results
        except Exception as e:
            self.result_list.addItem(f"Error reading {file_path}: {e}")
            return []

    def search_adunits_in_directory(self, directory):
        """Search for AdMob AdUnit IDs in all supported files in the directory."""
        found = False
        for root, _, files in os.walk(directory):
            for file in files:
                file_path = Path(root) / file
                if file_path.suffix in self.supported_extensions:
                    results = self.search_adunits_in_file(file_path)
                    if results:
                        found = True
                        self.result_list.addItem(f"File: {file_path}")
                        for adunit, count in set(results):
                            self.result_list.addItem(f"  AdUnit: {adunit} (Count: {count})")
        
        if not found:
            self.result_list.addItem("No AdMob AdUnit IDs found in the directory.")
        self.status_label.setText(f"Search completed in {directory}.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AdUnitSearchWindow()
    window.show()
    sys.exit(app.exec())
