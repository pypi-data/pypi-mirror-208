"""doc"""
import gi

gi.require_version("Gtk", "4.0")
import numpy as np
import sounddevice as sd
from gi.repository import Gtk


# Define the threshold for detecting a beep.
threshold = 0.5

# Create a window.

window = Gtk.Window()

# Create a label to display the decoded Morse code.
label = Gtk.Label()

# Create a button to start decoding.
button = Gtk.Button()


def decode_morse(button):
    # Get the audio file.
    with sd.Stream(channels=1, rate=44100, input=True) as stream:
        # Initialize the output string.
        output = ""

        # Loop over the audio samples.
        for frame in stream.read(1024):
            # Get the amplitude of the current sample.
            amplitude = np.max(frame)

            # If the amplitude is greater than the threshold, add a '1' to the output string.
            if amplitude > threshold:
                output += "1"
            else:
                output += "0"

        # Decode the Morse code.
        morse_code = ""
        for i in range(0, len(output), 5):
            # Get the current character.
            char = output[i : i + 5]

            # Decode the character.
            if char == "11111":
                morse_code += "."
            elif char == "11100":
                morse_code += "-"
            else:
                morse_code += " "

        # Set the label to the decoded Morse code.
        label.set_text(morse_code)


# Connect the button to a callback function.
button.connect("clicked", decode_morse)

# Add the label and button to the window.
window.add(label)
window.add(button)

# Show the window.
window.show_all()

# Start the main loop.
Gtk.main()
