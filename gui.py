import os, logging

from PyQt5 import uic
from PyQt5.QtCore import pyqtSignal, pyqtSlot
from PyQt5.QtGui import QResizeEvent
from PyQt5.QtWidgets import QDialog

from jack_midi_monitor import NOTE_NAMES
from jack_midi_kbd import JackMidiKeyboard


class ShutUpQT(object):
	"""
	A context manager for temporarily supressing DEBUG level messages.
	Primarily used when loading a Qt graphical user interface using uic.
	"""

	def __init__(self, level=logging.ERROR):
		self.level = level

	def __enter__(self):
		self.root = logging.getLogger()
		self.previous_log_level = self.root.getEffectiveLevel()
		self.root.setLevel(self.level)

	def __exit__(self, *_):
		self.root.setLevel(self.previous_log_level)	# Carry on ...


class MainWindow(QDialog):

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		my_dir = os.path.split(os.path.abspath(__file__))[0]
		with ShutUpQT():
			uic.loadUi(os.path.join(my_dir, 'gui.ui'), self)
		self._midi_keyboad = JackMidiKeyboard(True)
		self._midi_keyboad.on_midi_event(self.midi_keyboad_event)
		self.__decoders = {
			0x8: self.__note_off,
			0x9: self.__note_on,
			0xA: self.__no_op,
			0xB: self.__no_op,
			0xC: self.__no_op,
			0xD: self.__no_op,
			0xE: self.__no_op
		}

	def midi_keyboad_event(self, last_frame_time, offset, status, val_1, val_2):
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


if __name__ == "__main__":
	from jack_midi_monitor import show_gui
	show_gui()


# -------- end file
