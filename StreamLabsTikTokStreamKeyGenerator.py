import glob
import os
import platform
import re
import sys
import json
import threading
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                              QGroupBox, QPushButton, QLineEdit, QLabel, QCheckBox,
                              QListWidget, QMessageBox, QListWidgetItem, QSizePolicy)
from PySide6.QtCore import Signal, QTimer
from PySide6.QtGui import QDesktopServices
from Stream import Stream
from TokenRetriever import TokenRetriever
from Updater import VersionChecker
from packaging import version

class StreamApp(QMainWindow):
    update_suggestions = Signal(list)
    update_ui = Signal()
    
    def __init__(self):
        super().__init__()
        self.stream = None
        self.game_mask_id = ""
        self.init_ui()
        self.load_config()
        
        QTimer.singleShot(3000, lambda: [
            self.show_donation_reminder(),
            QTimer.singleShot(3000, self.check_updates_on_startup)
        ])

        # Connect signals
        self.update_suggestions.connect(self.update_suggestions_list)
        self.update_ui.connect(self.handle_ui_update)

    def init_ui(self):
        self.setWindowTitle("StreamLabs TikTok Stream Key Generator")
        self.setMinimumSize(800, 600)

        main_widget = QWidget()
        main_layout = QHBoxLayout()
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)

        # Left column
        left_column = QVBoxLayout()
        main_layout.addLayout(left_column)

        # Token Section
        token_group = QGroupBox("Token Loader")
        token_group.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        left_column.addWidget(token_group)

        token_layout = QVBoxLayout()
        token_layout.setContentsMargins(8, 12, 8, 8)
        token_layout.setSpacing(6)
        token_group.setLayout(token_layout)

        # Token Entry Row
        token_entry_row = QHBoxLayout()
        token_entry_row.setSpacing(5)

        self.token_entry = QLineEdit()
        self.token_entry.setPlaceholderText("Paste token here or load below...")
        self.token_entry.setEchoMode(QLineEdit.Password)
        self.token_entry.setFixedHeight(28)
        self.token_entry.textChanged.connect(self.handle_token_change)
        self.token_entry.returnPressed.connect(self.refresh_account_info)
        token_entry_row.addWidget(self.token_entry)

        # Eye icon for password visibility
        self.toggle_token_btn = QPushButton()
        self.toggle_token_btn.setFixedSize(28, 28)
        self.toggle_token_btn.setText("👁️")
        self.toggle_token_btn.setToolTip("Show token")
        self.toggle_token_btn.clicked.connect(self.toggle_token_visibility)
        token_entry_row.addWidget(self.toggle_token_btn)

        token_layout.addLayout(token_entry_row)

        # Token Load Buttons Row
        load_buttons_row = QHBoxLayout()
        load_buttons_row.setSpacing(5)

        # Local Token Button
        self.load_local_btn = QPushButton("Load from PC")
        self.load_local_btn.setFixedHeight(30)
        self.load_local_btn.setToolTip("Load token from Streamlabs desktop app data")
        self.load_local_btn.clicked.connect(self.load_local_token)
        load_buttons_row.addWidget(self.load_local_btn)

        # Online Token Button
        self.load_online_btn = QPushButton("Load from Web")
        self.load_online_btn.setFixedHeight(30)
        self.load_online_btn.setToolTip("Get token through browser login")
        self.load_online_btn.clicked.connect(self.fetch_online_token)
        load_buttons_row.addWidget(self.load_online_btn)

        token_layout.addLayout(load_buttons_row)

        # Binary Location Input Row
        if platform.system() == "Linux":
            binary_row = QHBoxLayout()
            binary_row.setSpacing(5)

            self.binary_location_entry = QLineEdit()
            self.binary_location_entry.setPlaceholderText("Custom Chrome binary path (optional)")
            self.binary_location_entry.setFixedHeight(28)
            self.binary_location_entry.setToolTip("Leave empty to auto-detect Chrome path on Linux")
            binary_row.addWidget(self.binary_location_entry)
            
            token_layout.addLayout(binary_row)


        # Account Info Section
        account_info_label = QLabel("Account Information")
        account_info_label.setStyleSheet("font-weight: bold; margin-top: 8px;")
        token_layout.addWidget(account_info_label)

        # Username
        username_row = QHBoxLayout()
        username_row.setSpacing(5)
        username_label = QLabel("Username:")
        username_label.setFixedWidth(100)
        self.tiktok_username = QLineEdit()
        self.tiktok_username.setReadOnly(True)
        self.tiktok_username.setFixedHeight(26)
        username_row.addWidget(username_label)
        username_row.addWidget(self.tiktok_username)
        token_layout.addLayout(username_row)

        # Status
        status_row = QHBoxLayout()
        status_row.setSpacing(5)
        status_label = QLabel("Status:")
        status_label.setFixedWidth(100)
        self.app_status = QLineEdit()
        self.app_status.setReadOnly(True)
        self.app_status.setFixedHeight(26)
        status_row.addWidget(status_label)
        status_row.addWidget(self.app_status)
        token_layout.addLayout(status_row)

        # Go Live Status
        live_row = QHBoxLayout()
        live_row.setSpacing(5)
        live_label = QLabel("Can Go Live:")
        live_label.setFixedWidth(100)
        self.can_go_live = QLineEdit()
        self.can_go_live.setReadOnly(True)
        self.can_go_live.setFixedHeight(26)
        live_row.addWidget(live_label)
        live_row.addWidget(self.can_go_live)
        token_layout.addLayout(live_row)
        
        # Refresh account info button
        refresh_btn = QPushButton("Refresh Account Info")
        refresh_btn.setFixedHeight(30)
        refresh_btn.setToolTip("Refresh account information")
        refresh_btn.clicked.connect(self.refresh_account_info)
        token_layout.addWidget(refresh_btn)

        # Add stretch to prevent expansion
        token_layout.addStretch()

        # Stream Details
        stream_group = QGroupBox("Stream Details")
        left_column.addWidget(stream_group)
        stream_layout = QVBoxLayout()
        stream_layout.setContentsMargins(8, 8, 8, 8)  # Left, Top, Right, Bottom margins
        stream_layout.setSpacing(5)  # Reduced spacing between widgets
        stream_group.setLayout(stream_layout)

        # Stream Title
        title_label = QLabel("Stream Title:")
        title_label.setStyleSheet("font-weight: bold;")
        stream_layout.addWidget(title_label)
        self.stream_title = QLineEdit()
        self.stream_title.setFixedHeight(28)  # Slightly smaller height
        stream_layout.addWidget(self.stream_title)

        # Game Category
        game_label = QLabel("Game Category:")
        game_label.setStyleSheet("font-weight: bold;")
        stream_layout.addWidget(game_label)
        self.game_category = QLineEdit()
        self.game_category.setFixedHeight(28)
        self.game_category.textChanged.connect(self.handle_game_search)
        stream_layout.addWidget(self.game_category)

        # Suggestions List
        self.suggestions_list = QListWidget()
        self.suggestions_list.hide()
        self.suggestions_list.setFixedHeight(100)  # Limit height of suggestions
        self.suggestions_list.itemClicked.connect(self.handle_suggestion_selected)
        stream_layout.addWidget(self.suggestions_list)

        # Mature Checkbox
        self.mature_checkbox = QCheckBox("Enable mature content")
        self.mature_checkbox.setStyleSheet("padding: 2px;")  # Reduce internal padding
        stream_layout.addWidget(self.mature_checkbox)

        # Add stretch to push everything up
        stream_layout.addStretch()

        # Right column (Controls)
        control_group = QGroupBox("Stream Control")
        control_group.setMinimumWidth(250)  # Set a minimum width for the control column
        main_layout.addWidget(control_group)

        control_layout = QVBoxLayout()
        control_layout.setContentsMargins(8, 12, 8, 8)  # Tighter margins
        control_layout.setSpacing(6)  # Reduced spacing between widgets
        control_group.setLayout(control_layout)

        # Buttons row
        button_row = QHBoxLayout()
        button_row.setSpacing(5)  # Tight spacing between buttons

        self.go_live_btn = QPushButton("Go Live")
        self.go_live_btn.setEnabled(False)
        self.go_live_btn.clicked.connect(self.start_stream)
        self.go_live_btn.setFixedHeight(32)  # Consistent button height
        button_row.addWidget(self.go_live_btn)

        self.end_live_btn = QPushButton("End Live")
        self.end_live_btn.setEnabled(False)
        self.end_live_btn.clicked.connect(self.end_stream)
        self.end_live_btn.setFixedHeight(32)
        button_row.addWidget(self.end_live_btn)

        control_layout.addLayout(button_row)

        # URL Section
        url_label = QLabel("Stream URL:")
        url_label.setStyleSheet("font-weight: bold; margin-top: 5px;")
        control_layout.addWidget(url_label)

        self.stream_url = QLineEdit()
        self.stream_url.setReadOnly(True)
        self.stream_url.setFixedHeight(28)  # Compact height
        control_layout.addWidget(self.stream_url)

        self.copy_url_btn = QPushButton("Copy URL")
        self.copy_url_btn.setFixedHeight(28)
        self.copy_url_btn.clicked.connect(lambda: self.copy_to_clipboard(self.stream_url))
        control_layout.addWidget(self.copy_url_btn)

        # Key Section
        key_label = QLabel("Stream Key:")
        key_label.setStyleSheet("font-weight: bold; margin-top: 5px;")
        control_layout.addWidget(key_label)

        self.stream_key = QLineEdit()
        self.stream_key.setReadOnly(True)
        self.stream_key.setFixedHeight(28)
        control_layout.addWidget(self.stream_key)

        self.copy_key_btn = QPushButton("Copy Key")
        self.copy_key_btn.setFixedHeight(28)
        self.copy_key_btn.clicked.connect(lambda: self.copy_to_clipboard(self.stream_key))
        control_layout.addWidget(self.copy_key_btn)

        # Add stretch to prevent expansion of widgets
        control_layout.addStretch()
        # Bottom buttons
        bottom_buttons = QHBoxLayout()
        left_column.addLayout(bottom_buttons)

        self.save_btn = QPushButton("Save Config")
        self.save_btn.clicked.connect(lambda: self.save_config())
        bottom_buttons.addWidget(self.save_btn)

        self.help_btn = QPushButton("Help")
        self.help_btn.clicked.connect(self.show_help)
        bottom_buttons.addWidget(self.help_btn)
        
        self.donate_btn = QPushButton("☕ Donate")
        self.donate_btn.setToolTip("Support the developer")
        self.donate_btn.clicked.connect(lambda: QDesktopServices.openUrl("https://buymeacoffee.com/loukious"))
        bottom_buttons.addWidget(self.donate_btn)

        self.monitor_btn = QPushButton("Open Live Monitor")
        self.monitor_btn.clicked.connect(self.open_live_monitor)
        bottom_buttons.addWidget(self.monitor_btn)

    def toggle_token_visibility(self):
        """Toggle token visibility and update emoji"""
        if self.token_entry.echoMode() == QLineEdit.Normal:
            self.token_entry.setEchoMode(QLineEdit.Password)
            self.toggle_token_btn.setText("👁️")  # Closed eye
            self.toggle_token_btn.setToolTip("Show token")
        else:
            self.token_entry.setEchoMode(QLineEdit.Normal)
            self.toggle_token_btn.setText("👁️‍🗨️")  # Eye with speech bubble (visible)
            self.toggle_token_btn.setToolTip("Hide token")

    def handle_token_change(self):
        self.go_live_btn.setEnabled(bool(self.token_entry.text()))

    def load_config(self):
        try:
            with open("config.json", "r") as file:
                data = json.load(file)
        except Exception as e:
            data = {}
        self.token_entry.setText(data.get("token", ""))
        self.stream_title.setText(data.get("title", ""))
        self.game_category.setText(data.get("game", ""))
        self.mature_checkbox.setChecked(data.get("audience_type", "0") == "1")
        self.suppress_donation_reminder = data.get("suppress_donation_reminder", False)

        self.refresh_account_info()

    def save_config(self, show_message=True):
        data = {
            "title": self.stream_title.text(),
            "game": self.game_category.text(),
            "audience_type": "1" if self.mature_checkbox.isChecked() else "0",
            "token": self.token_entry.text(),
            "suppress_donation_reminder": self.suppress_donation_reminder
        }
        with open("config.json", "w") as file:
            json.dump(data, file)
        if show_message:
            QMessageBox.information(self, "Config Saved", "Configuration saved successfully!")

    def load_account_info(self):
        if self.stream:
            try:
                info = self.stream.getInfo()
                user = info.get("user", {})
                self.tiktok_username.setText(user.get("username", "Unknown"))
                
                app_status = info.get("application_status", {})
                self.app_status.setText(app_status.get("status", "Unknown"))
                
                self.can_go_live.setText(str(info.get("can_be_live", False)))
                
                if not info.get("can_be_live", False):
                    self.stream_title.setEnabled(False)
                    self.game_category.setEnabled(False)
                    self.mature_checkbox.setEnabled(False)
                    self.go_live_btn.setEnabled(False)
                else:
                    self.stream_title.setEnabled(True)
                    self.game_category.setEnabled(True)
                    self.mature_checkbox.setEnabled(True)
                    self.go_live_btn.setEnabled(True)

            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to load account info: {str(e)}")
    
    def refresh_account_info(self):
        if self.token_entry.text():
            self.stream = Stream(self.token_entry.text())
            self.load_account_info()
            self.fetch_game_mask_id(self.game_category.text())
        self.save_config(False)

    def load_local_token(self):
        # Determine the correct path based on the operating system
        if platform.system() == 'Windows':
            path_pattern = os.path.expandvars(r'%appdata%\slobs-client\Local Storage\leveldb\*.log')
        elif platform.system() == 'Darwin':  # macOS
            path_pattern = os.path.expanduser('~/Library/Application Support/slobs-client/Local Storage/leveldb/*.log')
        else:
            QMessageBox.critical(self, "Error", "Unsupported operating system for local token retrieval.")
            return

        # Get all files matching the pattern
        files = glob.glob(path_pattern)
        
        # Sort files by date modified, newest first
        files.sort(key=os.path.getmtime, reverse=True)
        
        # Define the regex pattern to search for the apiToken
        token_pattern = re.compile(r'"apiToken":"([a-f0-9]+)"', re.IGNORECASE)
        
        token = None
        
        # Loop through files and search for the token pattern
        for file in files:
            try:
                with open(file, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    matches = token_pattern.findall(content)
                    if matches:
                        # Get the last occurrence of the token
                        token = matches[-1]
                        break
            except Exception as e:
                QMessageBox.critical("Error", f"Error reading file {file}: {e}")
        if token:
            self.token_entry.setText(token)
            self.stream = Stream(token)
            self.load_account_info()
            self.fetch_game_mask_id(self.game_category.text())
        else:
            QMessageBox.critical(self, "Error", "No API Token found locally. Make sure Streamlabs is installed and you're logged in using TikTok.")


    def fetch_online_token(self):
        retriever = TokenRetriever()
        binary_path = None
        if hasattr(self, "binary_location_entry"):
            binary_path = self.binary_location_entry.text().strip() or None
        try:
            token = retriever.retrieve_token(binary_path)
        except Exception as e:
            if "Chrome not found" in str(e):
                QMessageBox.critical(self, "Error", "Google Chrome not found. Please install it to use this feature.")
                return
        if token:
            self.token_entry.setText(token)
            self.stream = Stream(token)
            self.load_account_info()
            self.fetch_game_mask_id(self.game_category.text())
        else:
            QMessageBox.critical(self, "Error", "Failed to obtain token online!")

    def fetch_game_mask_id(self, game_name):
        if self.stream:
            try:
                categories = self.stream.search(game_name)
                for category in categories:
                    if category['full_name'] == game_name:
                        self.game_mask_id = category['game_mask_id']
                        return
                self.game_mask_id = ""
            except Exception as e:
                QMessageBox.warning(self, "Search Error", f"Failed to search games: {str(e)}")

    def handle_game_search(self, text):
        if text and self.stream:
            threading.Thread(target=self.search_games, args=(text,)).start()
        else:
            self.suggestions_list.hide()

    def search_games(self, text):
        try:
            categories = self.stream.search(text)
            self.update_suggestions.emit(categories)
        except Exception as e:
            QMessageBox.critical(self, "Search Error", f"Game search failed: {str(e)}")

    def update_suggestions_list(self, categories):
        self.suggestions_list.clear()
        for category in categories:
            self.suggestions_list.addItem(QListWidgetItem(category['full_name']))
        self.suggestions_list.setVisible(bool(categories))

    def handle_suggestion_selected(self, item):
        self.game_category.setText(item.text())
        self.fetch_game_mask_id(item.text())
        self.suggestions_list.hide()

    def start_stream(self):
        try:
            audience_type = "1" if self.mature_checkbox.isChecked() else "0"
            stream_url, stream_key = self.stream.start(
                self.stream_title.text(),
                self.game_mask_id,
                audience_type
            )
            
            if stream_url and stream_key:
                self.stream_url.setText(stream_url)
                self.stream_key.setText(stream_key)
                self.end_live_btn.setEnabled(True)
                self.go_live_btn.setEnabled(False)
                QMessageBox.information(self, "Live Started", "Stream started successfully!")
            else:
                QMessageBox.critical(self, "Error", "Failed to start stream!")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to start stream: {str(e)}")

    def end_stream(self):
        try:
            if self.stream.end():
                self.stream_url.clear()
                self.stream_key.clear()
                self.end_live_btn.setEnabled(False)
                self.go_live_btn.setEnabled(True)
                QMessageBox.information(self, "Live Ended", "Stream ended successfully!")
            else:
                QMessageBox.critical(self, "Error", "Failed to end stream!")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to end stream: {str(e)}")

    def copy_to_clipboard(self, widget):
        QApplication.clipboard().setText(widget.text())
        QMessageBox.information(self, "Copied", "Text copied to clipboard!")

    def show_help(self):
        help_text = """1. Apply for LIVE access on Streamlabs
2. Install Streamlabs and login to TikTok
3. Use this app to get Streamlabs token
4. Go live!"""
        
        msg = QMessageBox(self)
        msg.setWindowTitle("Help")
        msg.setText(help_text)
        msg.addButton(QMessageBox.Ok)
        msg.exec()


    def check_updates_on_startup(self):
        """Non-blocking update check with GUI notification"""
        update_info = VersionChecker.check_update()

        if update_info and version.parse(update_info["latest"]) > version.parse(update_info["current"]):
            msg = QMessageBox(self)
            msg.setWindowTitle("Update Available")
            msg.setText(
                f"Version {update_info['latest']} is available!\n\n"
                f"Current version: {update_info['current']}\n\n"
                "Would you like to download it now?"
            )
            
            # Use standard buttons for better compatibility
            msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
            msg.setDefaultButton(QMessageBox.Yes)
            
            if msg.exec() == QMessageBox.Yes:
                QDesktopServices.openUrl(update_info["url"])

    def show_donation_reminder(self):
        
        if self.suppress_donation_reminder:
            return
        
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setWindowTitle("Support Development")
        msg.setText("Enjoying this app? Consider supporting its development!")
        
        dont_show_again = QCheckBox("Never show this message again")
        msg.setCheckBox(dont_show_again)
        
        # Add buttons
        donate_btn = msg.addButton("Donate Now", QMessageBox.AcceptRole)
        msg.addButton(QMessageBox.Ok)
        
        # Make the "Donate Now" button more prominent
        donate_btn.setStyleSheet("font-weight: bold;")
        
        # Execute the message box
        msg.exec()
        
        if dont_show_again.isChecked():
            self.suppress_donation_reminder = True
            self.save_config(False)
        # Handle button clicks
        if msg.clickedButton() == donate_btn:
            QDesktopServices.openUrl("https://buymeacoffee.com/loukious")

    def open_live_monitor(self):
        QDesktopServices.openUrl("https://livecenter.tiktok.com/live_monitor?lang=en-US")

    def handle_ui_update(self):
        self.load_account_info()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = StreamApp()
    window.show()
    sys.exit(app.exec())