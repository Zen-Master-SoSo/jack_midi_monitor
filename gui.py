#  jack_midi_monitor/gui.py
#
#  Copyright 2024 liyang <liyang@veronica>
#
import os
from PyQt5 import uic
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtGui import QResizeEvent
from PyQt5.QtWidgets import QDialog
from qt_extras import ShutUpQT
from jack_midi_monitor import JackMidiMonitor
from midi_notes import NOTE_NAMES


class MainWindow(QDialog):

	def __init__(self):
		super().__init__()
		my_dir = os.path.split(os.path.abspath(__file__))[0]
		with ShutUpQT():
			uic.loadUi(os.path.join(my_dir, 'res', 'gui.ui'), self)
		self.monitor = JackMidiMonitor()
		self.monitor.on_midi_event(self.midi_event)
		self.monitor.on_connect_event(self.connect_event)
		self.__decoders = {
			0x8: self.__note_off,
			0x9: self.__note_on,
			0xA: self.__no_op,
			0xB: self.__no_op,
			0xC: self.__no_op,
			0xD: self.__no_op,
			0xE: self.__no_op
		}

	def connect_event(self, connected_port):
		if connected_port is None:
			self.l_client.setText('-')
			self.__note_off(None, None, None)
		else:
			self.l_client.setText(f'{connected_port.name}')

	def midi_event(self, last_frame_time, offset, status, val_1, val_2):
		opcode = status >> 4
		self.__decoders[opcode](status, val_1, val_2)

	def __no_op(self, status, val_1, val_2):
		pass

	def __note_on(self, status, val_1, val_2):
		self.l_note_name.setText(NOTE_NAMES[val_1])
		self.l_note_number.setText(str(val_1))
		self.l_velocity.setText(str(val_2))

	def __note_off(self, status, val_1, val_2):
		self.l_note_name.setText('')
		self.l_note_number.setText('')
		self.l_velocity.setText('')

	@pyqtSlot(QResizeEvent)
	def resizeEvent(self, event):
		f = self.l_note_name.font()
		f.setPixelSize(round(self.l_note_name.height() * 0.8))
		self.l_note_name.setFont(f)
		self.l_note_number.setFont(f)
		self.l_velocity.setFont(f)
		super().resizeEvent(event)


def main():
	from jack import JackError
	from PyQt5.QtWidgets import QApplication
	from qt_extras import DevilBox
	app = QApplication([])
	try:
		window = MainWindow()
	except JackError:
		DevilBox('Could not connect to JACK server. Is it running?')
		return 1
	window.show()
	return app.exec()


if __name__ == "__main__":
	import sys
	sys.exit(main())


#  end jack_midi_monitor/gui.py
