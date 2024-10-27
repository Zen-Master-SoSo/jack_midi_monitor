#!/usr/bin/env python3
import jack, struct
from jack_midi_kbd import JackMidiKeyboard


NOTE_NAMES = {
	0:		'C-1',
	1:		'C#-1',
	2:		'D-1',
	3:		'D#-1',
	4:		'E-1',
	5:		'F-1',
	6:		'F#-1',
	7:		'G-1',
	8:		'G#-1',
	9:		'A-1',
	10:		'A#-1',
	11:		'B-1',
	12:		'C0',
	13:		'C#0',
	14:		'D0',
	15:		'D#0',
	16:		'E0',
	17:		'F0',
	18:		'F#0',
	19:		'G0',
	20:		'G#0',
	21:		'A0',
	22:		'A#0',
	23:		'B0',
	24:		'C1',
	25:		'C#1',
	26:		'D1',
	27:		'D#1',
	28:		'E1',
	29:		'F1',
	30:		'F#1',
	31:		'G1',
	32:		'G#1',
	33:		'A1',
	34:		'A#1',
	35:		'B1',
	36:		'C2',
	37:		'C#2',
	38:		'D2',
	39:		'D#2',
	40:		'E2',
	41:		'F2',
	42:		'F#2',
	43:		'G2',
	44:		'G#2',
	45:		'A2',
	46:		'A#2',
	47:		'B2',
	48:		'C3',
	49:		'C#3',
	50:		'D3',
	51:		'D#3',
	52:		'E3',
	53:		'F3',
	54:		'F#3',
	55:		'G3',
	56:		'G#3',
	57:		'A3',
	58:		'A#3',
	59:		'B3',
	60:		'C4',
	61:		'C#4',
	62:		'D4',
	63:		'D#4',
	64:		'E4',
	65:		'F4',
	66:		'F#4',
	67:		'G4',
	68:		'G#4',
	69:		'A4',
	70:		'A#4',
	71:		'B4',
	72:		'C5',
	73:		'C#5',
	74:		'D5',
	75:		'D#5',
	76:		'E5',
	77:		'F5',
	78:		'F#5',
	79:		'G5',
	80:		'G#5',
	81:		'A5',
	82:		'A#5',
	83:		'B5',
	84:		'C6',
	85:		'C#6',
	86:		'D6',
	87:		'D#6',
	88:		'E6',
	89:		'F6',
	90:		'F#6',
	91:		'G6',
	92:		'G#6',
	93:		'A6',
	94:		'A#6',
	95:		'B6',
	96:		'C7',
	97:		'C#7',
	98:		'D7',
	99:		'D#7',
	100:	'E7',
	101:	'F7',
	102:	'F#7',
	103:	'G7',
	104:	'G#7',
	105:	'A7',
	106:	'A#7',
	107:	'B7',
	108:	'C8',
	109:	'C#8',
	110:	'D8',
	111:	'D#8',
	112:	'E8',
	113:	'F8',
	114:	'F#8',
	115:	'G8',
	116:	'G#8',
	117:	'A8',
	118:	'A#8',
	119:	'B8',
	120:	'C9',
	121:	'C#9',
	122:	'D9',
	123:	'D#9',
	124:	'E9',
	125:	'F9',
	126:	'F#9',
	127:	'G9'
}


class JackMidiMonitor:

	__client	= None
	__in_port	= None
	__out_port	= None

	def __init__(self, hexdump=False):
		self.__print_function = self.__print_hex if hexdump else self.__print_pretty
		self._midi_keyboad = JackMidiKeyboard(True)
		self._midi_keyboad.on_midi_event(self.midi_keyboad_event)
		self.__decoders = {
			0x8: self.__note_off,
			0x9: self.__note_on,
			0xA: self.__poly_pressure,
			0xB: self.__control_change,
			0xC: self.__program_change,
			0xD: self.__channel_pressure,
			0xE: self.__pitch_bend
		}


	def midi_keyboad_event(self, last_frame_time, offset, status, val_1, val_2):
		"""
		------------ MIDI CHEAT SHEET -------------
		8n,x1,x2 - Note Off (x1 = note number, x2 = velocity).
		9n,x1,x2 - Note On  (x1 = note number, x2 = velocity [x2=0 -> note off]).
		An,x1,x2 - Poly Pressure (x1 = note number, x2 = pressure value).
		Bn,x1,x2 - Control Change (x1 = controller number, x2 = value).
		   x1 =   0(00h),x2 = Bank MSB
		   x1 =  32(20h),x2 = Bank LSB [Bank = (MSB*128)+LSB]
		   x1 = 120(78h),0  - All Sound Off                    ÄÄ¿
		   x1 = 121(79h),0  - Reset All Controllers              ³
		   x1 = 122(7Ah),x2 - Local Control (127=on, 0=off)      ³
		   x1 = 123(7Bh),0  - All Notes Off                      ÃÄÄ MODE MESSAGES
		   x1 = 124(7Ch),0  - Omni Off (modes 3,4)               ³      121-127
		   x1 = 125(7Dh),0  - Omni On  (modes 1,2)               ³
		   x1 = 126(7Eh),x2 - Mono On  (modes 2,4) (x2=# of chs) ³
		   x1 = 127(7Fh),0  - Poly On  (modes 1,3)             ÄÄÙ
		Cn,x1    - Program Change (x1 = program number).
		Dn,x1    - Channel (Mono) Pressure (x1 = value).
		En,x1,x2 - Pitch Bend (x1 = LSB, x2 = MSB).  Value = (MSB * 128) + LSB
		"""
		self.__print_function(status, val_1, val_2)


	def __print_pretty(self, status, val_1, val_2):
		if val_2 is None:
			print(('%02X %02X    : ' % (status, val_1, val_2)), end='')
		else:
			print(('%02X %02X %02X : ' % (status, val_1, val_2)), end='')
		opcode = status >> 4
		self.__decoders[opcode](status, val_1, val_2)


	def __note_on(self, status, val_1, val_2):
		print('ON  %-3s %3d v. %-3d' % (
			NOTE_NAMES[val_1],
			val_1,
			val_2
		))


	def __note_off(self, status, val_1, val_2):
		print('OFF %-3s %3d' % (
			NOTE_NAMES[val_1],
			val_1
		))


	def __poly_pressure(self, status, val_1, val_2):
		print('POLY   %-3s %d  pres %d' % (
			NOTE_NAMES[val_1],
			val_1,
			val_2
		))


	def __control_change(self, status, val_1, val_2):
		print('CC_%-3d %d' % (val_1, val_2))


	def __program_change(self, status, val_1, val_2):
		print('PROG   %d' % (val_1))


	def __channel_pressure(self, status, val_1, val_2):
		print('PRES   %d' % (val_1))


	def __pitch_bend(self, status, val_1, val_2):
		print('BEND   msb %d lsb %d' % (val_1, val_2))


	def __print_hex(self, status, val_1, val_2):
		if val_2 is None:
			print('%02X %02X' % (status, val_1, val_2))
		else:
			print('%02X %02X %02X' % (status, val_1, val_2))


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


if __name__ == "__main__":
	import argparse
	parser = argparse.ArgumentParser()
	parser.add_argument('--auto-connect', '-a', action='store_true')
	parser.add_argument('--hexdump', '-x', action='store_true')
	options = parser.parse_args()

	with JackMidiMonitor(options.hexdump) as mon:
		if options.auto_connect:
			mon.auto_connect()
		print('#' * 80)
		print('press Return to quit')
		print('#' * 80)
		input()


