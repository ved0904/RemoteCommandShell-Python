# Troubleshooting Guide

This document covers common errors you might run into while setting up or using the Remote Command Shell, along with how to fix them. For general setup instructions, refer to the main [README.md](../README.md) in the root directory.

## Connection Issues

### "Connection refused" when starting the client

This means the client cannot reach the server. There are a few reasons this can happen:

1.  **Server is not running.** Make sure you start `server.py` first, before running `client.py`. You should see `Waiting for incoming connections...` in the server terminal before you start the client.

2.  **Wrong IP address in config.json.** Open `config.json` and check that `server_ip` under the `client` section matches the actual IP address of the machine running the server.
    ```json
    "client": {
        "server_ip": "192.168.1.100",
        "server_port": 9999
    }
    ```
    If both are on the same machine, use `127.0.0.1`. If they are on different machines, use the server's local IP. You can find this by running `ipconfig` (Windows) or `ifconfig` (Linux/macOS) on the server machine.

3.  **Firewall is blocking the port.** Your OS firewall might be blocking port 9999. On Windows, you can allow it through:
    ```bash
    netsh advfirewall firewall add rule name="ReverseShell" dir=in action=allow protocol=TCP localport=9999
    ```
    On Linux:
    ```bash
    sudo ufw allow 9999/tcp
    ```

### "Socket binding error" on server startup

This usually means another program is already using port 9999. You can either close that program or change the port in `config.json`:
```json
"server": {
    "host": "0.0.0.0",
    "port": 8888
}
```
Make sure to update the `server_port` in the client section as well so they match.

On Windows, you can find what is using the port with:
```bash
netstat -ano | findstr :9999
```

## Dependency Errors

### "ModuleNotFoundError: No module named 'PIL'" when using screenshot

The `pillow` library is not installed on the client machine. Install it with:
```bash
pip install pillow
```

### "ModuleNotFoundError: No module named 'cv2'" when using webcam

The `opencv-python` library is not installed on the client machine. Install it with:
```bash
pip install opencv-python
```

### "No webcam found or webcam in use"

This happens when the client machine either does not have a webcam, or another application (like Zoom or Teams) is already using it. Close any application that might be accessing the camera and try again.

## Configuration Issues

### "config.json not found, using default values"

The program cannot find the `config.json` file. Make sure it is in the same directory as `server.py` and `client.py`. If you are running the client as a standalone `.exe`, the `config.json` file must be placed in the same folder as the executable.

### "Invalid JSON in config file"

There is a syntax error in your `config.json`. Common mistakes include:
*   Missing commas between fields
*   Trailing commas after the last field in a section
*   Using single quotes instead of double quotes

You can validate your JSON by pasting it into [jsonlint.com](https://jsonlint.com/).

## File Transfer Issues

### "File not found" during download

The file path you specified does not exist on the client machine. Remember that the path is relative to the client's current working directory. You can use `cd` to navigate to the right folder first, or provide the full absolute path:
```
download C:\Users\someone\Documents\file.txt
```

### "Hash mismatch! File may be corrupted"

The file was modified or corrupted during transfer. This can happen on unstable network connections. Try downloading the file again. If the problem persists, check your network connection.

## PyInstaller / Executable Issues

### The .exe closes immediately after opening

This is expected if the server is not running or the client cannot connect. Since the executable is built with `--noconsole`, you will not see any error messages on screen. Check `client.log` in the same directory as the executable for error details.

### "Failed to execute script client" when running the .exe

This can happen if the `.exe` was built on a different version of Windows. Rebuild the executable on the same OS version where you plan to run it:
```bash
python -m PyInstaller --onefile --noconsole client.py
```

### Client .exe does not reconnect after losing connection

Make sure `reconnect_enabled` is set to `true` in your `config.json`:
```json
"client": {
    "reconnect_enabled": true,
    "reconnect_delay": 5,
    "max_reconnect_attempts": 0
}
```
Setting `max_reconnect_attempts` to `0` means unlimited retries.
