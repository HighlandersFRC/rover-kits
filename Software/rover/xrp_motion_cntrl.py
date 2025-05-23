# Filename: FlaskServer.py
# Author: Aswin S Babu
# Description: This script sets up a Flask web server on the Raspberry Pi to control the XRP robot via joystick-like buttons in the browser.
# The server communicates with the Pico via USB serial to send movement commands such as Forward, Backward, Left, Right, and Stop.

from flask import Flask, render_template_string, request  # Import necessary modules from Flask
import serial  # Import the serial module for USB communication

# Attempt to set up the serial connection to Pico
try:
    # Open a serial connection to the Pico on port "/dev/ttyACM1" with baud rate 115200
    # Adjust the port if Pico is connected to a different one (e.g., "/dev/ttyACM0")
    s = serial.Serial("/dev/ttyACM1", 115200)
    print("Connected to Pico via USB Serial.")
except serial.SerialException as e:
    # If there is an error opening the serial port, catch the exception and print the error message
    print(f"Failed to connect to Pico: {e}")
    print("Verify serial port number using ls /dev/ttyACM*")
    s = None  # Set the serial object to None to indicate the connection failed

# Initialize the Flask application
app = Flask(__name__)

# HTML template for the joystick interface
# This template includes buttons for controlling the Pico: Forward, Backward, Left, Right, and Stop
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Joystick Control</title>
    <style>
        /* Styling for the joystick buttons */
        .button {
            padding: 20px 40px; /* Button size */
            font-size: 24px; /* Text size */
            margin: 5px; /* Space around buttons */
            cursor: pointer; /* Pointer cursor on hover */
            background-color: #4CAF50; /* Green background color */
            color: white; /* White text */
            border: none; /* No border */
            border-radius: 5px; /* Rounded corners */
        }
        .button-container {
            display: grid; /* Use CSS Grid layout for joystick arrangement */
            grid-template-columns: repeat(3, 1fr); /* 3 columns equally spaced */
            gap: 10px; /* Space between buttons */
            justify-items: center; /* Center the buttons horizontally */
            align-items: center; /* Center the buttons vertically */
        }
        .spacer {
            visibility: hidden; /* Invisible spacers to maintain layout */
        }
    </style>
</head>
<body>
    <h1>Joystick Control</h1>
    <!-- Form containing the joystick control buttons arranged in a cross pattern -->
    <form method="POST">
        <div class="button-container">
            <!-- Spacer to align Forward button in the center -->
            <div class="spacer"></div>
            <!-- Forward button placed directly above the Stop button -->
            <button class="button" name="command" value="F">Forward</button>
            <div class="spacer"></div> <!-- Spacer for alignment -->

            <!-- Left button placed to the left of the Stop button -->
            <button class="button" name="command" value="L">Left</button>
            <!-- Stop button in the center -->
            <button class="button" name="command" value="S">Stop</button>
            <!-- Right button placed to the right of the Stop button -->
            <button class="button" name="command" value="R">Right</button>

            <!-- Spacer to align Backward button in the center -->
            <div class="spacer"></div>
            <!-- Backward button placed directly below the Stop button -->
            <button class="button" name="command" value="B">Backward</button>
            <div class="spacer"></div> <!-- Spacer for alignment -->
        </div>
    </form>
</body>
</html>
"""

@app.route('/', methods=['GET', 'POST'])  # Define route for the root URL ('/')
def index():
    """Render the joystick control page and handle button presses."""
    if request.method == 'POST':  # Check if the request method is POST (form submitted)
        command = request.form.get('command')  # Get the command value from the button pressed
        if command:  # If a command is received, send it to the Pico
            send_usb_command(command)  # Call the function to send the command over USB
    return render_template_string(HTML_TEMPLATE)  # Render the HTML template

def send_usb_command(command):
    """Send the corresponding command to the Pico via USB Serial."""
    if not s:  # Check if the serial connection is established
        print("Serial connection not established.")  # Print error if not connected
        return  # Exit the function if no connection
    try:
        # Send the command to the Pico by writing it to the serial port
        # Append a newline character '\n' to the command for proper parsing on the Pico side
        s.write((command + '\n').encode('utf-8'))  # Encode the command as bytes and send
        print(f"Sent command: {command}")  # Print the command sent for debugging
    except Exception as e:  # Catch any exceptions during serial communication
        print(f"Error sending command: {e}")  # Print the error message

if __name__ == '__main__':
    # Start the Flask web server on all available IPs (host='0.0.0.0'), on port 5000
    try:
        app.run(host='0.0.0.0', port=5000)  # Start the Flask server
    except KeyboardInterrupt:
        print("Server stopped by user.")  # Print message if server is stopped with Ctrl+C
    finally:
        if s:  # Check if the serial connection is open
            s.close()  # Close the serial connection to clean up resources
            print("Serial connection closed.")  # Confirm that the connection has been closed