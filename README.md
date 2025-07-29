# jack_midi_monitor

Provides a means to monitor midi events from a Jack client.
Includes both a console and a Qt GUI version.

## Command line:

	$ jack-midi-monitor-cli

This will pop up a little QtDialog which will display incoming MIDI events.
You can resize the dialog to make the font size bigger.

## Gui:

	$ jack-midi-monitor

... will print incoming MIDI events to the console.

## Connections

Connect to the "JackMidiMonitor:input" port using your preferred method.

For example, from the command line:

	$ jack_connect system:midi_capture_1 JackMidiMonitor:input

(jack_connect is part of the "jackd2" package on Debian)
