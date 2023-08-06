"""Support for multi-channel audio synthesis

At least 2 simultaneous notes are supported.  samd5x, mimxrt10xx and rp2040 platforms support up to 12 notes.

"""

from __future__ import annotations

import typing
from typing import Optional, Sequence, Union

from circuitpython_typing import ReadableBuffer

class Envelope:
    def __init__(
        self,
        *,
        attack_time: Optional[float] = 0.1,
        decay_time: Optional[float] = 0.05,
        release_time: Optional[float] = 0.2,
        attack_level: Optional[float] = 1.0,
        sustain_level: Optional[float] = 0.8,
    ) -> None:
        """Construct an Envelope object

        The Envelope defines an ADSR (Attack, Decay, Sustain, Release) envelope with linear amplitude ramping. A note starts at 0 volume, then increases to ``attack_level`` over ``attack_time`` seconds; then it decays to ``sustain_level`` over ``decay_time`` seconds. Finally, when the note is released, it decreases to ``0`` volume over ``release_time``.

        If the ``sustain_level`` of an envelope is 0, then the decay and sustain phases of the note are always omitted. The note is considered to be released as soon as the envelope reaches the end of the attack phase. The ``decay_time`` is ignored. This is similar to how a plucked or struck instrument behaves.

        If a note is released before it reaches its sustain phase, it decays with the same slope indicated by ``sustain_level/release_time`` (or ``attack_level/release_time`` for plucked envelopes)

        :param float attack_time: The time in seconds it takes to ramp from 0 volume to attack_volume
        :param float decay_time: The time in seconds it takes to ramp from attack_volume to sustain_volume
        :param float release_time: The time in seconds it takes to ramp from sustain_volume to release_volume. When a note is released before it has reached the sustain phase, the release is done with the same slope indicated by ``release_time`` and ``sustain_level``. If the ``sustain_level`` is ``0.0`` then the release slope calculations use the ``attack_level`` instead.
        :param float attack_level: The level, in the range ``0.0`` to ``1.0`` of the peak volume of the attack phase
        :param float sustain_level: The level, in the range ``0.0`` to ``1.0`` of the volume of the sustain phase relative to the attack level
        """
    attack_time: float
    """The time in seconds it takes to ramp from 0 volume to attack_volume"""

    decay_time: float
    """The time in seconds it takes to ramp from attack_volume to sustain_volume"""

    release_time: float
    """The time in seconds it takes to ramp from sustain_volume to release_volume. When a note is released before it has reached the sustain phase, the release is done with the same slope indicated by ``release_time`` and ``sustain_level``"""

    attack_level: float
    """The level, in the range ``0.0`` to ``1.0`` of the peak volume of the attack phase"""

    sustain_level: float
    """The level, in the range ``0.0`` to ``1.0`` of the volume of the sustain phase relative to the attack level"""

def from_file(
    file: typing.BinaryIO,
    *,
    sample_rate: int = 11025,
    waveform: Optional[ReadableBuffer] = None,
    envelope: Optional[Envelope] = None,
) -> MidiTrack:
    """Create an AudioSample from an already opened MIDI file.
    Currently, only single-track MIDI (type 0) is supported.

    :param typing.BinaryIO file: Already opened MIDI file
    :param int sample_rate: The desired playback sample rate; higher sample rate requires more memory
    :param ReadableBuffer waveform: A single-cycle waveform. Default is a 50% duty cycle square wave. If specified, must be a ReadableBuffer of type 'h' (signed 16 bit)
    :param Envelope envelope: An object that defines the loudness of a note over time. The default envelope provides no ramping, voices turn instantly on and off.

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

def midi_to_hz(midi_note: float) -> float:
    """Converts the given midi note (60 = middle C, 69 = concert A) to Hz"""

def onevo_to_hz(ctrl: float) -> float:
    """Converts a 1v/octave signal to Hz.

    60/12 (5.0) corresponds to middle C, 69/12 is concert A."""

class BendMode:
    """Controls the way the ``Note.pitch_bend_depth`` and ``Note.pitch_bend_rate`` properties are interpreted."""

    STATIC: "BendMode"
    """The Note's pitch is modified by its ``pitch_bend_depth``. ``pitch_bend_rate`` is ignored."""

    VIBRATO: "BendMode"
    """The Note's pitch varies by ``±pitch_bend_depth`` at a rate of ``pitch_bend_rate`` Hz."""

    SWEEP: "BendMode"
    """The Note's pitch starts at ``Note.frequency`` then sweeps up or down by ``pitch_bend_depth`` over ``1/pitch_bend_rate`` seconds."""

    SWEEP_IN: "BendMode"
    """The Note's pitch sweep is the reverse of ``SWEEP`` mode, starting at the bent pitch and arriving at the tuned pitch."""

class MidiTrack:
    """Simple MIDI synth"""

    def __init__(
        self,
        buffer: ReadableBuffer,
        tempo: int,
        *,
        sample_rate: int = 11025,
        waveform: Optional[ReadableBuffer] = None,
        envelope: Optional[Envelope] = None,
    ) -> None:
        """Create a MidiTrack from the given stream of MIDI events. Only "Note On" and "Note Off" events
        are supported; channel numbers and key velocities are ignored. Up to two notes may be on at the
        same time.

        :param ~circuitpython_typing.ReadableBuffer buffer: Stream of MIDI events, as stored in a MIDI file track chunk
        :param int tempo: Tempo of the streamed events, in MIDI ticks per second
        :param int sample_rate: The desired playback sample rate; higher sample rate requires more memory
        :param ReadableBuffer waveform: A single-cycle waveform. Default is a 50% duty cycle square wave. If specified, must be a ReadableBuffer of type 'h' (signed 16 bit)
        :param Envelope envelope: An object that defines the loudness of a note over time. The default envelope provides no ramping, voices turn instantly on and off.

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
    sample_rate: int
    """32 bit value that tells how quickly samples are played in Hertz (cycles per second)."""

    error_location: Optional[int]
    """Offset, in bytes within the midi data, of a decoding error"""

class Note:
    def __init__(
        self,
        *,
        frequency: float,
        panning: float = 0.0,
        waveform: Optional[ReadableBuffer] = None,
        envelope: Optional[Envelope] = None,
        tremolo_depth: float = 0.0,
        tremolo_rate: float = 0.0,
        bend_depth: float = 0.0,
        bend_rate: float = 0.0,
        bend_mode: "BendMode" = BendMode.VIBRATO,
    ) -> None:
        """Construct a Note object, with a frequency in Hz, and optional panning, waveform, envelope, tremolo (volume change) and bend (frequency change).

        If waveform or envelope are `None` the synthesizer object's default waveform or envelope are used.

        If the same Note object is played on multiple Synthesizer objects, the result is undefined.
        """
    frequency: float
    """The base frequency of the note, in Hz."""
    filter: bool
    """True if the note should be processed via the synthesizer's FIR filter."""
    panning: float
    """Defines the channel(s) in which the note appears.

    -1 is left channel only, 0 is both channels, and 1 is right channel.
    For fractional values, the note plays at full amplitude in one channel
    and partial amplitude in the other channel. For instance -.5 plays at full
    amplitude in the left channel and 1/2 amplitude in the right channel."""
    tremolo_depth: float
    """The tremolo depth of the note, from 0 to 1

    A depth of 0 disables tremolo. A nonzero value enables tremolo,
    with the maximum decrease in amplitude being equal to the tremolo
    depth. A note with a tremolo depth of 1 will fade out to nothing, while
    a tremolo depth of 0.1 will give a minimum amplitude of 0.9."""
    tremolo_rate: float
    """The tremolo rate of the note, in Hz."""

    bend_mode: BendMode
    """The type of bend operation"""

    bend_depth: float
    """The bend depth of the note, from -1 to +1

    A depth of 0 disables bend. A depth of 1 corresponds to a bend of 1
    octave.  A depth of (1/12) = 0.833 corresponds to a bend of 1 semitone,
    and a depth of .00833 corresponds to one musical cent.
    """
    bend_rate: float
    """The bend rate of the note, in Hz."""
    waveform: Optional[ReadableBuffer]
    """The waveform of this note. Setting the waveform to a buffer of a different size resets the note's phase."""
    envelope: Envelope
    """The envelope of this note"""

    ring_frequency: float
    """The ring frequency of the note, in Hz. Zero disables.

    For ring to take effect, both ``ring_frequency`` and ``ring_waveform`` must be set."""
    ring_waveform: Optional[ReadableBuffer]
    """The ring waveform of this note. Setting the ring_waveform to a buffer of a different size resets the note's phase.

    For ring to take effect, both ``ring_frequency`` and ``ring_waveform`` must be set."""

NoteSequence = Sequence[Union[int, Note]]
"""A sequence of notes, which can each be integer MIDI notes or `Note` objects"""

class Synthesizer:
    def __init__(
        self,
        *,
        sample_rate: int = 11025,
        channel_count: int = 1,
        waveform: Optional[ReadableBuffer] = None,
        envelope: Optional[Envelope] = None,
    ) -> None:
        """Create a synthesizer object.

        This API is experimental.

        Integer notes use MIDI note numbering, with 60 being C4 or Middle C,
        approximately 262Hz. Integer notes use the given waveform & envelope,
        and do not support advanced features like tremolo or vibrato.

        :param int sample_rate: The desired playback sample rate; higher sample rate requires more memory
        :param int channel_count: The number of output channels (1=mono, 2=stereo)
        :param ReadableBuffer waveform: A single-cycle waveform. Default is a 50% duty cycle square wave. If specified, must be a ReadableBuffer of type 'h' (signed 16 bit)
        :param ReadableBuffer filter: Coefficients of an FIR filter to apply to notes with ``filter=True``. If specified, must be a ReadableBuffer of type 'h' (signed 16 bit)
        :param Optional[Envelope] envelope: An object that defines the loudness of a note over time. The default envelope, `None` provides no ramping, voices turn instantly on and off.
        """
    def press(self, /, press: NoteSequence = ()) -> None:
        """Turn some notes on.

        Pressing a note that was already pressed has no effect.

        :param NoteSequence press: Any sequence of notes."""
    def release(self, /, release: NoteSequence = ()) -> None:
        """Turn some notes off.

        Releasing a note that was already released has no effect.

        :param NoteSequence release: Any sequence of notes."""
    def release_then_press(
        self, release: NoteSequence = (), press: NoteSequence = ()
    ) -> None:
        """Turn some notes on and/or off.

        It is OK to release note that was not actually turned on.

        Pressing a note that was already pressed has no effect.

        Releasing and pressing the note again has little effect, but does reset the phase
        of the note, which may be perceptible as a small glitch.

        :param NoteSequence release: Any sequence of notes.
        :param NoteSequence press: Any sequence of notes."""
    def release_all_then_press(self, /, press: NoteSequence) -> None:
        """Turn any currently-playing notes off, then turn on the given notes

        Releasing and pressing the note again has little effect, but does reset the phase
        of the note, which may be perceptible as a small glitch.

        :param NoteSequence press: Any sequence of notes."""
    def release_all(self) -> None:
        """Turn any currently-playing notes off"""
    def deinit(self) -> None:
        """Deinitialises the object and releases any memory resources for reuse."""
        ...
    def __enter__(self) -> Synthesizer:
        """No-op used by Context Managers."""
        ...
    def __exit__(self) -> None:
        """Automatically deinitializes the hardware when exiting a context. See
        :ref:`lifetime-and-contextmanagers` for more info."""
        ...
    envelope: Optional[Envelope]
    """The envelope to apply to all notes. `None`, the default envelope, instantly turns notes on and off. The envelope may be changed dynamically, but it affects all notes (even currently playing notes)"""
    sample_rate: int
    """32 bit value that tells how quickly samples are played in Hertz (cycles per second)."""
    pressed: NoteSequence
    """A sequence of the currently pressed notes (read-only property)"""

    max_polyphony: int
    """Maximum polyphony of the synthesizer (read-only class property)"""
