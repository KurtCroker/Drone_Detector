def main():
    try:
        from serial.tools import list_ports
    except ImportError:
        print("PySerial is not installed.")
        print("Run: pip install -r requirements.txt")
        return

    ports = list(list_ports.comports())

    if not ports:
        print("No serial ports found.")
        return

    print("Serial ports:")
    for port in ports:
        print(
            f"  {port.device}  "
            f"{port.description}"
        )


if __name__ == "__main__":
    main()
