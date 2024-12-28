import sys
import sqlite3
from datetime import datetime
from PyQt6.QtWidgets import (QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QLabel, QLineEdit, QTextEdit, QListWidget, QMessageBox, QInputDialog, QHBoxLayout, QMenu, QFileDialog, QComboBox)
from PyQt6.QtGui import QAction
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

# 🗂️ Initialize Database Connection
def initialize_database():
    connection = sqlite3.connect("portfolio.db")  # 📁 Creating or connecting to SQLite database
    cursor = connection.cursor()

    # 🛠️ Create a table for user projects
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,  -- 🆔 Auto-incremented ID for each project
            name TEXT NOT NULL,  -- 📋 Project name
            description TEXT,  -- 📝 Description of the project
            link TEXT,  -- 🔗 Link to the project
            created_at TEXT NOT NULL  -- 📅 Timestamp of when the project was added
        )
    ''')
    connection.commit()
    return connection

class PortfolioManager(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Portfolio Manager")
        self.setGeometry(300, 200, 900, 700)

        self.connection = initialize_database()

        # Main Layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout()
        self.central_widget.setLayout(self.layout)

        # Menu Button for Settings
        self.settings_button = QPushButton("⚙️ Settings")
        self.settings_button.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        self.settings_button.setStyleSheet("background-color: #673ab7; color: white; padding: 10px; border-radius: 5px;")
        self.settings_button.clicked.connect(self.show_settings_menu)
        self.layout.addWidget(self.settings_button)

        # Widgets
        self.project_list = QListWidget()
        self.project_list.setSelectionMode(QListWidget.SelectionMode.SingleSelection)
        self.project_list.setStyleSheet("font-size: 14px; background-color: #f9f9f9; border: 1px solid #ccc;")
        self.layout.addWidget(self.project_list)

        self.load_projects()

        button_layout = QHBoxLayout()
        self.layout.addLayout(button_layout)

        self.add_button = QPushButton("➕ Add Project")
        self.add_button.setFont(QFont("Arial", 11))
        self.add_button.setStyleSheet("background-color: #4caf50; color: white; padding: 10px; border-radius: 5px;")
        self.add_button.clicked.connect(self.add_project)
        button_layout.addWidget(self.add_button)

        self.update_button = QPushButton("✏️ Update Project")
        self.update_button.setFont(QFont("Arial", 11))
        self.update_button.setStyleSheet("background-color: #2196f3; color: white; padding: 10px; border-radius: 5px;")
        self.update_button.clicked.connect(self.update_project)
        button_layout.addWidget(self.update_button)

        self.delete_button = QPushButton("🗑️ Delete Project")
        self.delete_button.setFont(QFont("Arial", 11))
        self.delete_button.setStyleSheet("background-color: #f44336; color: white; padding: 10px; border-radius: 5px;")
        self.delete_button.clicked.connect(self.delete_project)
        button_layout.addWidget(self.delete_button)

        self.import_button = QPushButton("📥 Import Project")
        self.import_button.setFont(QFont("Arial", 11))
        self.import_button.setStyleSheet("background-color: #ff9800; color: white; padding: 10px; border-radius: 5px;")
        self.import_button.clicked.connect(self.import_project)
        button_layout.addWidget(self.import_button)

        self.details_label = QLabel("Select a project to see details.")
        self.details_label.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.details_label.setWordWrap(True)
        self.layout.addWidget(self.details_label)

        self.project_list.itemSelectionChanged.connect(self.display_details)

    def load_projects(self):
        self.project_list.clear()
        cursor = self.connection.cursor()
        cursor.execute("SELECT id, name FROM projects")
        projects = cursor.fetchall()

        for project in projects:
            self.project_list.addItem(f"{project[0]}: {project[1]}")

    def add_project(self):
        name, ok = QInputDialog.getText(self, "Add Project", "Enter project name:")
        if not ok or not name.strip():
            QMessageBox.warning(self, "Error", "Project name cannot be empty!")
            return

        description, ok = QInputDialog.getMultiLineText(self, "Add Project", "Enter project description:")
        if not ok:
            return

        link, ok = QInputDialog.getText(self, "Add Project", "Enter project link (optional):")
        if not ok:
            link = ""

        cursor = self.connection.cursor()
        created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("INSERT INTO projects (name, description, link, created_at) VALUES (?, ?, ?, ?)", (name, description, link, created_at))
        self.connection.commit()
        QMessageBox.information(self, "Success", f"Project '{name}' added successfully!")
        self.load_projects()

    def update_project(self):
        selected_item = self.project_list.currentItem()
        if not selected_item:
            QMessageBox.warning(self, "Error", "No project selected!")
            return

        project_id = int(selected_item.text().split(":")[0])
        new_description, ok = QInputDialog.getMultiLineText(self, "Update Project", "Enter new description:")
        if not ok:
            return

        new_link, ok = QInputDialog.getText(self, "Update Project", "Enter new link (optional):")
        if not ok:
            new_link = ""

        cursor = self.connection.cursor()
        cursor.execute("UPDATE projects SET description = ?, link = ? WHERE id = ?", (new_description, new_link, project_id))
        self.connection.commit()
        QMessageBox.information(self, "Success", "Project updated successfully!")
        self.display_details()

    def delete_project(self):
        selected_item = self.project_list.currentItem()
        if not selected_item:
            QMessageBox.warning(self, "Error", "No project selected!")
            return

        project_id = int(selected_item.text().split(":")[0])
        cursor = self.connection.cursor()
        cursor.execute("DELETE FROM projects WHERE id = ?", (project_id,))
        self.connection.commit()
        QMessageBox.information(self, "Success", "Project deleted successfully!")
        self.load_projects()
        self.details_label.setText("Select a project to see details.")

    def display_details(self):
        selected_item = self.project_list.currentItem()
        if not selected_item:
            self.details_label.setText("Select a project to see details.")
            return

        project_id = int(selected_item.text().split(":")[0])
        cursor = self.connection.cursor()
        cursor.execute("SELECT name, description, link, created_at FROM projects WHERE id = ?", (project_id,))
        project = cursor.fetchone()

        if project:
            details = f"<b>Name:</b> {project[0]}<br><b>Description:</b> {project[1] or 'No description provided.'}<br><b>Created At:</b> {project[3]}"
            if project[2]:
                details += f"<br><b>Link:</b> <a href='{project[2]}'>{project[2]}</a>"
            self.details_label.setText(details)

    def show_settings_menu(self):
        menu = QMenu()

        change_style_action = QAction("Change Style", self)
        change_style_action.triggered.connect(self.change_style)
        menu.addAction(change_style_action)

        menu.exec(self.settings_button.mapToGlobal(self.settings_button.rect().bottomLeft()))

    def import_project(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Import Project", "", "All Files (*.*);;Python Files (*.py);;C++ Files (*.cpp);;C# Files (*.cs);;Java Files (*.java)")
        if file_path:
            name, ok = QInputDialog.getText(self, "Import Project", "Enter project name for the imported file:")
            if not ok or not name.strip():
                QMessageBox.warning(self, "Error", "Project name cannot be empty!")
                return

            description, ok = QInputDialog.getMultiLineText(self, "Import Project", "Enter project description:")
            if not ok:
                description = ""

            cursor = self.connection.cursor()
            created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cursor.execute("INSERT INTO projects (name, description, link, created_at) VALUES (?, ?, ?, ?)", (name, description, file_path, created_at))
            self.connection.commit()
            QMessageBox.information(self, "Success", f"Project '{name}' imported successfully!")
            self.load_projects()

    def change_style(self):
        styles = ["Fusion", "Windows", "Macintosh"]
        style, ok = QInputDialog.getItem(self, "Change Style", "Select a style:", styles, 0, False)
        if ok:
            QApplication.setStyle(style)
            if style == "Fusion":
                self.setStyleSheet("background-color: #e0f7fa;")
            elif style == "Windows":
                self.setStyleSheet("background-color: #ffffff;")
            elif style == "Macintosh":
                self.setStyleSheet("background-color: #f8f8f8;")

    def closeEvent(self, event):
        self.connection.close()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PortfolioManager()
    window.show()
    sys.exit(app.exec())
