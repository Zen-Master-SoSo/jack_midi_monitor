#  jack_midi_monitor/__init__.py
#
#  Copyright 2024 liyang <liyang@veronica>
#
import jack, struct, logging
from midi_notes import NOTE_NAMES


class JackMidiMonitor:

	def __init__(self, auto_connect=False):
		self.client = jack.Client(self.__class__.__name__, no_start_server=True)
		logging.debug('Connected as %s; samplerate %s; blocksize %s',
			self.__class__.__name__,
			self.client.samplerate,
			self.client.blocksize
		)
		self.port = self.client.midi_inports.register('input')
		self.__callback = self.__noop
		self.client.set_process_callback(self.__process)
		self.client.activate()
		self.client.get_ports()
		if auto_connect:
			self.auto_connect()

	def auto_connect(self):
		for p in self.client.get_ports(is_output=True, is_midi=True):
			if 'Through' in p.name:
				continue
			logging.debug('Connecting %s to %s', p.name, self.port.name)
			try:
				self.port.connect(p.name)
				break
			except Exception as e:
				print(e)

	def on_midi_event(self, callback):
		"""
		Sets the MIDI event callback.
		"callback" takes these arguments:
		(self, last_frame_time, offset, status, val_1, val_2)
		"""
		if not callable(callback):
			raise Exception("Invalid callback")
		self.__callback = callback

	def __process(self, frames):
		for offset, indata in self.port.incoming_midi_events():
			if len(indata) == 3:
				status, val_1, val_2 = struct.unpack('3B', indata)
				self.__callback(self.client.last_frame_time, offset, status, val_1, val_2)
			elif len(indata) == 2:
				status, val_1 = struct.unpack('3B', indata)
				self.__callback(self.client.last_frame_time, offset, status, val_1, None)
			else:
				logging.debug(len(indata))

	def __noop(self, last_frame_time, offset, status, val_1, val_2):
		pass

	def __enter__(self):
		return self

	def __exit__(self, exc_type, exc_value, traceback):
		pass


def show_gui():
	import sys
	from PyQt5.QtWidgets import QApplication
	from jack_midi_monitor.gui import MainWindow
	app = QApplication([])
	window = MainWindow()
	window.show()
	sys.exit(app.exec())


def main():
	import argparse

	parser = argparse.ArgumentParser()
	parser.add_argument('--auto-connect', '-a', action='store_true')
	parser.add_argument('--hex', '-x', action='store_true')
	parser.add_argument("--verbose", "-v", action="store_true", help="Show more detailed debug information")
	options = parser.parse_args()
	logging.basicConfig(
		level = logging.DEBUG if options.verbose else logging.ERROR,
		format = "[%(filename)24s:%(lineno)4d] %(levelname)-8s %(message)s"
	)

	def print_pretty(last_frame_time, offset, status, val_1, val_2):
		if val_2 is None:
			print(('%02X %02X    : ' % (status, val_1, val_2)), end='')
		else:
			print(('%02X %02X %02X : ' % (status, val_1, val_2)), end='')
		opcode = status >> 4
		decoders[opcode](status, val_1, val_2)

	def print_hex(last_frame_time, offset, status, val_1, val_2):
		if val_2 is None:
			print('%02X %02X' % (status, val_1, val_2))
		else:
			print('%02X %02X %02X' % (status, val_1, val_2))

	def note_on(status, val_1, val_2):
		print('ON      %-3s %-3d %-3d' % (
			NOTE_NAMES[val_1],
			val_1,
			val_2
		))

	def note_off(status, val_1, val_2):
		print('OFF     %-3s %-3d' % (
			NOTE_NAMES[val_1],
			val_1
		))

	def poly_pressure(status, val_1, val_2):
		print('POLY    %-3s %d  pres %d' % (
			NOTE_NAMES[val_1],
			val_1,
			val_2
		))

	def control_change(status, val_1, val_2):
		print('CC_%-3d %d' % (val_1, val_2))

	def program_change(status, val_1, val_2):
		print('PROG    %d' % (val_1))

	def channel_pressure(status, val_1, val_2):
		print('PRES    %d' % (val_1))

	def pitch_bend(status, val_1, val_2):
		print('BEND    %d %d' % (val_1, val_2))

	decoders = {
		0x8: note_off,
		0x9: note_on,
		0xA: poly_pressure,
		0xB: control_change,
		0xC: program_change,
		0xD: channel_pressure,
		0xE: pitch_bend
	}

	with JackMidiMonitor(options.auto_connect) as mon:
		mon.on_midi_event(print_hex if options.hex else print_pretty)
		print('#' * 80)
		print('press Return to quit')
		print('#' * 80)
		input()


if __name__ == "__main__":
	main()

#  end jack_midi_monitor/__init__.py
