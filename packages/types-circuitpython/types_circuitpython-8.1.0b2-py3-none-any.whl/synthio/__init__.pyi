"""Support for MIDI synthesis"""

from __future__ import annotations

import typing
from typing import Optional, Sequence, Tuple

from circuitpython_typing import ReadableBuffer

def from_file(file: typing.BinaryIO, *, sample_rate: int = 11025) -> MidiTrack:
    """Create an AudioSample from an already opened MIDI file.
    Currently, only single-track MIDI (type 0) is supported.

    :param typing.BinaryIO file: Already opened MIDI file
    :param int sample_rate: The desired playback sample rate; higher sample rate requires more memory
    :param ReadableBuffer waveform: A single-cycle waveform. Default is a 50% duty cycle square wave. If specified, must be a ReadableBuffer of type 'h' (signed 16 bit)


    Playing a MIDI file from flash::

          import audioio
          import board
          import synthio

          data = open("single-track.midi", "rb")
          midi = synthio.from_file(data)
          a = audioio.AudioOut(board.A0)

          print("playing")
          a.play(midi)
          while a.playing:
            pass
          print("stopped")"""
    ...

class MidiTrack:
    """Simple MIDI synth"""

    def __init__(
        self,
        buffer: ReadableBuffer,
        tempo: int,
        *,
        sample_rate: int = 11025,
        waveform: ReadableBuffer = None,
    ) -> None:
        """Create a MidiTrack from the given stream of MIDI events. Only "Note On" and "Note Off" events
        are supported; channel numbers and key velocities are ignored. Up to two notes may be on at the
        same time.

        :param ~circuitpython_typing.ReadableBuffer buffer: Stream of MIDI events, as stored in a MIDI file track chunk
        :param int tempo: Tempo of the streamed events, in MIDI ticks per second
        :param int sample_rate: The desired playback sample rate; higher sample rate requires more memory
        :param ReadableBuffer waveform: A single-cycle waveform. Default is a 50% duty cycle square wave. If specified, must be a ReadableBuffer of type 'h' (signed 16 bit)

        Simple melody::

          import audioio
          import board
          import synthio

          dac = audioio.AudioOut(board.SPEAKER)
          melody = synthio.MidiTrack(b"\\0\\x90H\\0*\\x80H\\0\\6\\x90J\\0*\\x80J\\0\\6\\x90L\\0*\\x80L\\0\\6\\x90J\\0" +
                                     b"*\\x80J\\0\\6\\x90H\\0*\\x80H\\0\\6\\x90J\\0*\\x80J\\0\\6\\x90L\\0T\\x80L\\0" +
                                     b"\\x0c\\x90H\\0T\\x80H\\0\\x0c\\x90H\\0T\\x80H\\0", tempo=640)
          dac.play(melody)
          print("playing")
          while dac.playing:
            pass
          print("stopped")"""
        ...
    def deinit(self) -> None:
        """Deinitialises the MidiTrack and releases any hardware resources for reuse."""
        ...
    def __enter__(self) -> MidiTrack:
        """No-op used by Context Managers."""
        ...
    def __exit__(self) -> None:
        """Automatically deinitializes the hardware when exiting a context. See
        :ref:`lifetime-and-contextmanagers` for more info."""
        ...
    sample_rate: Optional[int]
    """32 bit value that tells how quickly samples are played in Hertz (cycles per second)."""

class Synthesizer:
    def __init__(
        self, *, sample_rate: int = 11025, waveform: ReadableBuffer = None
    ) -> None:
        """Create a synthesizer object.

        This API is experimental.

        At least 2 simultaneous notes are supported.  mimxrt10xx and rp2040 platforms support up to
        12 notes.

        Notes use MIDI note numbering, with 60 being C4 or Middle C, approximately 262Hz.

        :param int sample_rate: The desired playback sample rate; higher sample rate requires more memory
        :param ReadableBuffer waveform: A single-cycle waveform. Default is a 50% duty cycle square wave. If specified, must be a ReadableBuffer of type 'h' (signed 16 bit). It is permitted to modify this buffer during synthesis. This can be used, for instance, to control the overall volume or timbre of the notes.
        """
    def press(self, /, press: Sequence[int] = ()) -> None:
        """Turn some notes on. Notes use MIDI numbering, with 60 being middle C, approximately 262Hz.

        Pressing a note that was already pressed has no effect.

        :param Sequence[int] press: Any sequence of integer notes."""
    def release_then_press(
        self, release: Sequence[int] = (), press: Sequence[int] = ()
    ) -> None:
        """Turn some notes on and/or off. Notes use MIDI numbering, with 60 being middle C.

        It is OK to release note that was not actually turned on.

        Pressing a note that was already pressed has no effect.

        Releasing and pressing the note again has little effect, but does reset the phase
        of the note, which may be perceptible as a small glitch.

        :param Sequence[int] release: Any sequence of integer notes.
        :param Sequence[int] press: Any sequence of integer notes."""
    def release_all_then_press(self, /, press: Sequence[int]) -> None:
        """Turn any currently-playing notes off, then turn on the given notes

        Releasing and pressing the note again has little effect, but does reset the phase
        of the note, which may be perceptible as a small glitch.

        :param Sequence[int] press: Any sequence of integer notes."""
    def release_all(self) -> None:
        """Turn any currently-playing notes off"""
    def deinit(self) -> None:
        """Deinitialises the object and releases any memory resources for reuse."""
        ...
    def __enter__(self) -> MidiTrack:
        """No-op used by Context Managers."""
        ...
    def __exit__(self) -> None:
        """Automatically deinitializes the hardware when exiting a context. See
        :ref:`lifetime-and-contextmanagers` for more info."""
        ...
    sample_rate: int
    """32 bit value that tells how quickly samples are played in Hertz (cycles per second)."""
    pressed: Tuple[int]
    """A sequence of the currently pressed notes (read-only property)"""

    max_polyphony: int
    """Maximum polyphony of the synthesizer (read-only class property)"""
