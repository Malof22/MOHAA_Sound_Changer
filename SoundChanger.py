from PyQt6.QtCore import Qt, QUrl
from PyQt6.QtGui import QIcon
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
from PyQt6.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QFileDialog, QListWidget, QTreeWidget, \
    QTreeWidgetItem, QMenu, QLabel
import os
import zipfile
import shutil

from RecordWindow import RecordWindow

class SoundChanger(QWidget):
    def __init__(self):
        super().__init__()

        # Window settings
        self.setWindowTitle("MOHAA Sound Changer")
        self.setFixedSize(800, 600)
        self.setWindowIcon(QIcon('icons/icon.ico'))

        # Paths settings
        self.folder_path = None
        self.pack_name = '/Pak3.pk3'
        self.extract_path = '/temp'

        # Audio player settings
        self.player = QMediaPlayer()
        self.audio_output = QAudioOutput()

        self.player.setAudioOutput(self.audio_output)

        # Layout settings
        self.main_layout = QVBoxLayout()

        button = QPushButton("Select MOHAA folder")
        button.clicked.connect(self.select_folder)
        self.main_layout.addWidget(button)

        self.setLayout(self.main_layout)

        # When window is closed, delete temp folder
        self.closeEvent = self.closeEvent
        self.closeEvent = lambda event: self.delete_temp_folder()

    def select_folder(self):
        self.folder_path = QFileDialog.getExistingDirectory(self, "Select MOHAA folder")
        if self.folder_path:
            print("Selected folder:", self.folder_path)
        else:
            print("No folder selected.")
            return

        if not os.path.exists(self.folder_path + '/backup'):
            os.makedirs(self.folder_path + '/backup')

        if os.path.exists(self.folder_path+self.pack_name):
            self.pak_path = self.folder_path + self.pack_name
            self.bkp_path = self.folder_path + '/backup' + self.pack_name
            self.sounds_path = self.folder_path + self.extract_path
        elif os.path.exists(self.folder_path+'/main'+self.pack_name):
            self.pak_path = self.folder_path + '/main' + self.pack_name
            self.bkp_path = self.folder_path + '/main/backup' + self.pack_name
            self.sounds_path = self.folder_path + '/main' + self.extract_path
        else:
            print("No files found in the specified folder.")
            return

        shutil.copyfile(self.pak_path, self.bkp_path)
        self.extract_files(self.pak_path, self.sounds_path)

        sounds = {}

        sound_root = os.path.join(self.sounds_path, "sound")

        for root, dirs, files in os.walk(sound_root):

            category = os.path.relpath(root, sound_root)

            if category == ".":
                category = "root"

            for file in files:
                if file.lower().endswith((".wav", ".mp3")):

                    full_path = os.path.join(root, file)

                    if category not in sounds:
                        sounds[category] = []

                    sounds[category].append(
                        (file, full_path)
                    )

        self.show_sounds(sounds)

    def extract_files(self, zip_file, extract_path):
        print("Extracting files...")
        with zipfile.ZipFile(zip_file, 'r') as zip_ref:
            zip_ref.extractall(extract_path)
            print("Files extracted successfully.")

    def compress_files(self, folder_path, zip_file):
        with zipfile.ZipFile(zip_file, "w", zipfile.ZIP_DEFLATED) as zipf:
            try:

                for root, dirs, files in os.walk(folder_path):
                    for file in files:
                        file_path = os.path.join(root, file)

                        archive_path = os.path.relpath(file_path, folder_path)

                        zipf.write(file_path, archive_path)

                return 'ok'
            except Exception as e:
                print(f"Error compressing files: {e}")
                return e

    def show_sounds(self, sounds):
        while self.main_layout.count():
            item = self.main_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        tree = QTreeWidget()
        tree.setHeaderLabel("Sounds")

        for category, files in sounds.items():

            category_item = QTreeWidgetItem([category])

            for name, path in files:
                sound_item = QTreeWidgetItem([name])

                sound_item.setData(
                    0,
                    Qt.ItemDataRole.UserRole,
                    path
                )

                category_item.addChild(sound_item)

            tree.addTopLevelItem(category_item)

        tree.itemDoubleClicked.connect(self.play_sound)

        tree.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        tree.customContextMenuRequested.connect(self.show_context_menu)

        self.tree = tree

        self.save_button = QPushButton("Save")
        self.save_button.clicked.connect(self.save_changes)

        self.status_label = QLabel()
        self.status_label.setVisible(False)
        self.status_label.setStyleSheet(
            "QLabel { color: green; }"
        )

        self.main_layout.addWidget(tree)
        self.main_layout.addWidget(self.save_button)
        self.main_layout.addWidget(self.status_label)

    def show_context_menu(self, pos):
        item = self.tree.itemAt(pos)

        if item is None:
            return

        path = item.data(0, Qt.ItemDataRole.UserRole)

        if path is None:
            return

        menu = QMenu()

        play_action = menu.addAction("Play")
        replace_action = menu.addAction("Replace")
        open_action = menu.addAction("Open folder")
        record_action = menu.addAction("Record")

        action = menu.exec(
            self.tree.viewport().mapToGlobal(pos)
        )

        if action == play_action:
            self.play_sound(item, 0)

        elif action == replace_action:
            self.replace_sound(path)

        elif action == open_action:
            self.open_folder(path)

        elif action == record_action:
            self.record_sound(path)

    def replace_sound(self, old_path):
        new_file, _ = QFileDialog.getOpenFileName(
            self,
            "Choisir un nouveau son",
            "",
            "Audio (*.wav *.mp3)"
        )

        #Convert to 1 channel
        if new_file.endswith(".wav"):
            new_file = new_file.replace(".wav", "_1.wav")
            os.system(f"ffmpeg -i {new_file} -ac 1 {new_file}")
            new_file = new_file.replace("_1.wav", ".wav")
        elif new_file.endswith(".mp3"):
            new_file = new_file.replace(".mp3", "_1.mp3")
            os.system(f"ffmpeg -i {new_file} -ac 1 {new_file}")
            new_file = new_file.replace("_1.mp3", ".wav")

        if not new_file:
            return

        shutil.copy2(new_file, old_path)

        print(f"Replaced : {old_path}")

    def open_folder(self, path):
        os.startfile(os.path.dirname(path))

    def play_sound(self, item, column):
        path = item.data(0, Qt.ItemDataRole.UserRole)

        if path is None:
            return

        self.player.setSource(QUrl.fromLocalFile(path))
        self.player.play()

    def record_sound(self, path):
        self.record_window = RecordWindow(path)
        self.record_window.show()

    def save_changes(self):
        print("Backing up...")
        self.backup(
            self.pak_path,
            self.bkp_path
        )
        print("Saving changes...")
        print(self.sounds_path)
        if '/main' in self.folder_path:
            save_path = self.folder_path + self.pack_name
        else:
            save_path = self.folder_path + '/main' + self.pack_name
        result = self.compress_files(self.sounds_path, save_path)
        if result == 'ok':
            self.status_label.setText("Changes saved successfully.")
        else:
            self.status_label.setText(f"Error saving changes: {result}")
        self.status_label.setVisible(True)

    def delete_temp_folder(self):
        if '/main' in self.folder_path:
            temp_path = self.folder_path + self.extract_path
        else:
            temp_path = self.folder_path + '/main' + self.extract_path
        shutil.rmtree(temp_path)

    def backup(self, pak_path, bkp_path):
        if os.path.exists(bkp_path):
            i=0
            bkp_path = bkp_path.replace(self.pack_name, f"/{self.pack_name[1:-4]}_backup{i}.pk3")
            while True:
                bkp_path = bkp_path.replace(f"backup{i}", f"backup{i+1}")
                if not os.path.exists(bkp_path):
                    break
                i+=1

        shutil.copyfile(pak_path, bkp_path)

if __name__ == "__main__":
    app = QApplication([])

    window = SoundChanger()
    window.show()

    app.exec()