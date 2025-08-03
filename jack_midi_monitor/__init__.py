#  jack_midi_monitor/jack_midi_monitor/__init__.py
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
Provides a means to monitor midi events from a Jack client.
Includes both a console and a Qt GUI version.
"""
import struct, logging
from jack import Client as JackClient, OwnPort

__version__ = "1.1.0"


class JackMidiMonitor:

	def __init__(self, auto_connect=False):
		self.client = JackClient(self.__class__.__name__, no_start_server=True)
		logging.debug('Connected as %s; samplerate %s; blocksize %s',
			self.__class__.__name__,
			self.client.samplerate,
			self.client.blocksize
		)
		self.port = self.client.midi_inports.register('input')
		self.__midi_evt_callback = self.__noop
		self.__connect_callback = None
		self.client.set_process_callback(self.__process)
		self.client.set_port_connect_callback(self.port_connect_callback)
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

	def port_connect_callback(self, a, b, connect):
		if self.__connect_callback:
			connected_port = None
			if isinstance(a, OwnPort):
				self.__connect_callback(b if connect else None)
			elif isinstance(b, OwnPort):
				self.__connect_callback(a if connect else None)

	def on_midi_event(self, callback):
		"""
		Sets the MIDI event callback.
		"callback" takes these arguments:
		(self, last_frame_time, offset, status, val_1, val_2)
		"""
		if not callable(callback):
			raise Exception("Invalid callback")
		self.__midi_evt_callback = callback

	def on_connect_event(self, callback):
		"""
		Sets the Port Connect event callback.
		"callback" takes one argument:
		(connected_port: Port)
		"""
		if not callable(callback):
			raise Exception("Invalid callback")
		self.__connect_callback = callback

	def __process(self, frames):
		for offset, indata in self.port.incoming_midi_events():
			if len(indata) == 3:
				status, val_1, val_2 = struct.unpack('3B', indata)
				self.__midi_evt_callback(self.client.last_frame_time, offset, status, val_1, val_2)
			elif len(indata) == 2:
				status, val_1 = struct.unpack('2B', indata)
				self.__midi_evt_callback(self.client.last_frame_time, offset, status, val_1, None)
			else:
				logging.debug('Invalid MIDI message len: %d', len(indata))

	def __noop(self, last_frame_time, offset, status, val_1, val_2):
		pass

	def __enter__(self):
		return self

	def __exit__(self, exc_type, exc_value, traceback):
		pass


#  end jack_midi_monitor/jack_midi_monitor/__init__.py
