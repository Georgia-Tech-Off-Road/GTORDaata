import serial, time

BAUD = 230400
SEND_ENABLE = True
SEND_MS = 400
WINDOW_LEN = 50

ser = serial.Serial(baudrate=BAUD, port='COM3', timeout=2, write_timeout=1)
end_code = [b'\xff', b'\xff', b'\xff', b'\xff', b'\xff', b'\xff', b'\xff', b'\xf0']
packet = []

inc = 0

window = []

last_tx = time.time()
last_rx = time.time()

inc_rx = -1

print('Starting...')

while True:
    now = time.time()

    if ser.in_waiting != 0:
        packet.append(ser.read(1))
        if packet[-8:] == end_code:
            window.append(now - last_rx)
            if len(window) > WINDOW_LEN:
                window.pop(0)
            temp = int.from_bytes(packet[1], 'big')
            if (temp - inc_rx) % 256 != 1:
                print('-----SKIPPED PACKETS-----')
            print(temp, len(packet), sum(window) / len(window))

            inc_rx = temp
            last_rx = now
            packet.clear()
    
    if (now - last_tx) * 1000 > SEND_MS and SEND_ENABLE:
        packet_send = [b'\x02']
        packet_send.extend([inc.to_bytes(1, 'big')] * 10)
        packet_send.extend(end_code)
        ser.write(b''.join(packet_send))
        last_tx = now
        inc = (inc + 1) % 256
    