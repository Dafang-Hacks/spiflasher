from GD25Q128 import GD25Q128Reader
flasher = GD25Q128Reader()
flasher.connect("/dev/ttyUSB0")
flasher.dump_rom("flash.bin")