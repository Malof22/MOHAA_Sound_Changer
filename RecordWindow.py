from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtWidgets import QWidget, QPushButton, QVBoxLayout, QApplication, QLabel, QSlider, QHBoxLayout, QCheckBox
from PyQt6.QtGui import QIcon
import sounddevice as sd
import numpy as np
import soundfile as sf

class RecordWindow(QWidget):
    def __init__(self, target_path):
        super().__init__()

        # Window settings
        self.setWindowTitle("Record sound")
        self.setFixedSize(400, 200)
        self.setWindowIcon(QIcon('icons/icon.ico'))

        # Paths settings
        self.target_path = target_path

        # Layout settings
        layout = QVBoxLayout()

        self.label = QLabel(f"Recording to : {target_path.split('/')[-1]}")
        layout.addWidget(self.label)

        self.start_button = QPushButton()
        self.start_button.setIcon(QIcon("icons/record.svg"))
        self.stop_button = QPushButton()
        self.stop_button.setIcon(QIcon("icons/stop.svg"))
        self.play_button = QPushButton()
        self.play_button.setIcon(QIcon("icons/play.svg"))
        self.stop_button.setEnabled(False)

        self.buttons_layout = QHBoxLayout()
        self.buttons_layout.addWidget(self.start_button)
        self.buttons_layout.addWidget(self.stop_button)
        self.buttons_layout.addWidget(self.play_button)
        layout.addLayout(self.buttons_layout)

        self.setLayout(layout)

        self.start_button.clicked.connect(self.start_countdown)
        self.stop_button.clicked.connect(self.stop_recording)
        self.play_button.clicked.connect(self.play_recording)

        self.stream = None
        self.frames = []
        self.sample_rate = 44100

        self.time_elapsed = 0

        self.timer_label = QLabel("00:00")
        layout.addWidget(self.timer_label)

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_timer)

        self.cut_checkbox = QCheckBox("Cut silence")
        self.cut_checkbox.setChecked(True)
        layout.addWidget(self.cut_checkbox)

        self.amp_label = QLabel("Amplification :")
        self.amp_label.setEnabled(False)
        layout.addWidget(self.amp_label)
        amp_layout = QHBoxLayout()
        self.amp_level = QLabel("1")
        self.amp_slider = QSlider(Qt.Orientation.Horizontal)
        self.amp_slider.setRange(0, 50)
        self.amp_slider.setValue(1)
        self.amp_slider.valueChanged.connect(
            lambda value: self.amp_level.setText(str(value))
        )
        self.amp_slider.setEnabled(False)
        self.amp_level.setEnabled(False)
        amp_layout.addWidget(self.amp_level)
        amp_layout.addWidget(self.amp_slider)
        layout.addLayout(amp_layout)

        self.save_button = QPushButton("Save")
        layout.addWidget(self.save_button)
        self.save_button.clicked.connect(self.save_audio)
        self.save_button.setEnabled(False)

        self.countdown_value = 3

        self.countdown_timer = QTimer()
        self.countdown_timer.timeout.connect(self.update_countdown)

    def start_countdown(self):
        self.countdown_value = 3

        self.timer_label.setText(str(self.countdown_value))

        self.start_button.setEnabled(False)
        self.play_button.setEnabled(False)
        self.save_button.setEnabled(False)
        self.amp_slider.setEnabled(False)
        self.amp_level.setEnabled(False)
        self.amp_label.setEnabled(False)

        self.countdown_timer.start(1000)

    def update_countdown(self):
        self.countdown_value -= 1

        if self.countdown_value > 0:
            self.timer_label.setText(str(self.countdown_value))
        else:
            self.countdown_timer.stop()

            self.timer_label.setText("00:00")

            self.start_recording()

    def start_recording(self):
        self.stop_button.setEnabled(True)

        self.time_elapsed = 0
        self.timer_label.setText("00:00")

        self.timer.start(1000)

        self.frames = []

        self.stream = sd.InputStream(
            samplerate=self.sample_rate,
            channels=1,
            callback=self.audio_callback
        )

        self.stream.start()

        print("Recording...")

    def stop_recording(self):
        if self.stream is None:
            return

        self.stop_button.setEnabled(False)
        self.start_button.setEnabled(True)
        self.save_button.setEnabled(True)
        self.amp_slider.setEnabled(True)
        self.amp_level.setEnabled(True)
        self.amp_label.setEnabled(True)
        self.play_button.setEnabled(True)

        self.timer.stop()

        self.stream.stop()
        print(self.frames)
        self.stream.close()

    def play_recording(self):
        audio = np.concatenate(self.frames, axis=0)
        audio = audio * self.amp_slider.value()
        sd.play(audio, self.sample_rate)

    def audio_callback(self, indata, frames, time, status):
        if status:
            print(status)

        self.frames.append(indata.copy())

    def update_timer(self):
        self.time_elapsed += 1

        minutes = self.time_elapsed // 60
        seconds = self.time_elapsed % 60

        self.timer_label.setText(f"{minutes:02}:{seconds:02}")

    def save_audio(self):
        audio = np.concatenate(self.frames, axis=0)

        if self.cut_checkbox.isChecked():
            # Détection du début du son
            threshold = 0.02  # à ajuster

            abs_audio = np.abs(audio[:, 0])
            indices = np.where(abs_audio > threshold)[0]

            if len(indices) > 0:
                audio = audio[indices[0]:]

            audio = np.clip(audio, -1.0, 1.0)

        audio = audio * self.amp_slider.value()

        sf.write(
            self.target_path,
            audio,
            self.sample_rate
        )

        sf.write(
            self.target_path,
            audio,
            self.sample_rate
        )
        print("Audio saved successfully.")
        self.close()


if __name__ == "__main__":
    app = QApplication([])
    window = RecordWindow("test.wav")
    window.show()
    app.exec()