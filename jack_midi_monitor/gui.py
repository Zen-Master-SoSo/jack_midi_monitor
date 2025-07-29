#  jack_midi_monitor/jack_midi_monitor/gui.py
#
#  Copyright 2025 Leon Dionne <ldionne@dridesign.sh.cn>
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#
"""
Provides a Qt interface to see what's coming in from a Jack port.
"""
from os.path import dirname, abspath, join
from PyQt5 import uic
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtGui import QResizeEvent
from PyQt5.QtWidgets import QApplication, QDialog
from qt_extras import DevilBox, ShutUpQT
from jack import JackError
from jack_midi_monitor import JackMidiMonitor
from midi_notes import NOTE_NAMES


class MainWindow(QDialog):

	def __init__(self):
		super().__init__()
		with ShutUpQT():
			uic.loadUi(join(dirname(abspath(__file__)), 'res', 'gui.ui'), self)
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


#  end jack_midi_monitor/jack_midi_monitor/gui.py
