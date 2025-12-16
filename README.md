# Remote Command Shell

I built this project to create a Python-based reverse shell that allows for remote command execution and system administration. It essentially lets you open a terminal on another computer from your own machine, enabling you to run commands and see their output in real-time. The tool was designed with education in mind, serving as a practical demonstration of socket programming and how client-server architectures interact over a network.

## Key Features

The core functionality focuses on giving you direct control over a remote system's command line, regardless of whether it's running Windows, Linux, or macOS. I made sure to include robust error handling and automatic logging so you can easily track what's happening if something goes wrong. It also supports directory navigation, meaning you can move around the file system on the remote machine just as if you were sitting right in front of it. All the configuration is handled through a simple JSON file, making it easy to adjust settings without touching the code.

## Prerequisites

Before running the project, you need to install Python and two external libraries on the client machine (the computer you want to control).

1.  **Install Python** (3.6 or higher) from [python.org](https://www.python.org/downloads/).
2.  **Install Dependencies** by running this command in your terminal:
    ```bash
    pip install opencv-python pillow
    ```
    *   `opencv-python`: Required for the webcam feature.
    *   `pillow`: Required for taking screenshots.

## Installation

1.  **Clone the Repository**
    Download the project files to your computer:
    ```bash
    git clone https://github.com/ved0904/RemoteCommandShell-Python.git
    cd Reverse_Shell
    ```

2.  **Configure Settings**
    Open `Reverse_Shell/config.json` and update the server IP:
    ```json
    {
      "server": {
        "host": "YOUR_IP_HERE",
        "port": 9999
      }
    }
    ```

## How to Run

Follow these steps in order:

1.  **Start the Server (Your Computer)**
    Open a terminal, go to the project folder, and run:
    ```bash
    cd Reverse_Shell
    python server.py
    ```
    You will see: `Waiting for incoming connections...`

2.  **Start the Client (Target Computer)**
    On the other computer, open a terminal in the project folder and run:
    ```bash
    python client.py
    ```
    If successful, it will connect immediately.

## Usage & Special Commands

Once connected, you can type standard commands like `dir` or `cd`.

I've also built in some **special commands** to make things easier. Just type **`help`** in the server terminal to see the full list, which includes:

*   **`sysinfo`**: Shows system information (OS, hostname, user, admin status)
*   **`ipconfig`**: Displays network configuration and IP addresses
*   **`processes`**: Lists the top 50 running processes
*   **`wifi`**: (Windows only) Extracts all saved WiFi passwords
*   **`screenshot`**: Captures screen and transfers to server
*   **`webcam`**: Captures photo from webcam and transfers to server
*   **`Hack <message>`**: Displays popup message on victim's screen
*   **`download <filename>`**: Downloads a file from client (supports full paths)
*   **`upload <filename>`**: Uploads a file to client
*   **`quit`**: Closes the connection
