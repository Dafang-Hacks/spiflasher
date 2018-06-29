import sys
import struct
import math


from pyBusPirateLite.SPI import *

class GD25Q128Reader:
    def __init__(self):
        self.status_byte = PIN_POWER | PIN_CS
        self.spi = None

        #Chip Size
        #self.chip_block = 256
        #self.chip_sectors = 16
        #self.chip_pages = 4096
        self.chip_bytes = 0x1000000

        #Commands
        self.CMD_WREN           = 0x06              #Write Enable
        self.CMD_WRDI           = 0x04              #Write Disable
        self.CMD_RDSR1          = 0x05              #Read status register 0-7
        self.CMD_RDSR2          = 0x35              #Read status register 8-15
        self.CMD_RDSR3          = 0x15              #Read status register 16-23
        self.CMD_READ           = 0x03              #Read data bytes
        self.CMD_PP             = 0x02              #Page Program
        #self.CMD_SE             = 0x20              #Sector Erase
        #self.CMD_BE32           = 0x52              #32kb Block Erase
        #self.CMD_BE64           = 0xD8              #64kb Block Erase
        self.CMD_CE             = 0xC7              #Chip Erase
        self.CMD_REMS           = 0x90              #Read Manufacture ID/Device ID
        self.CMD_RDID           = 0x9F              #Read Identification

        #Status Registers
        self.SR_HOLD_RST    = 7
        self.SR_DRV1        = 6
        self.SR_DRV0        = 5
        self.SR_WPS         = 2

        self.SR_SUS1        = 7
        self.SR_CMP         = 6
        self.SR_LB3         = 5
        self.SR_LB2         = 4
        self.SR_LB1         = 3
        self.SR_SUS2        = 2
        self.SR_QE          = 1
        self.SR_SRP1        = 0

        self.SR_SRP0        = 7
        self.SR_BP4         = 6
        self.SR_BP3         = 5
        self.SR_BP2         = 4
        self.SR_BP1         = 3
        self.SR_BP0         = 2
        self.SR_WEL         = 1
        self.SR_WIP         = 0

    def connect(self, usb_port):
        self.spi = SPI(usb_port, 115200)

        print "Entering binmode: ",
        if self.spi.BBmode():
            print "OK."
        else:
            print "failed."
            sys.exit()

        print "Entering raw SPI mode: ",
        if self.spi.enter_SPI():
            print "OK."
        else:
            print "failed."
            sys.exit()

        print "Configuring SPI."
        if not self.spi.cfg_pins(self.status_byte):
            print "Failed to set SPI peripherals."
            sys.exit()
        if not self.spi.set_speed(SPISpeed._4MHZ):
            print "Failed to set SPI Speed."
            sys.exit()
        if not self.spi.cfg_spi(SPICfg.CLK_EDGE | SPICfg.OUT_TYPE):
            print "Failed to set SPI configuration.";
            sys.exit()
        self.spi.timeout(0.2)

        #Bring PROG to High
        self.status_byte |= PinCfg.AUX
        if not self.spi.cfg_pins(self.status_byte):
            print "Failed to set PROG pin to HIGH"
            sys.exit()

    def disconnect(self):
        #Cleanup
        print "Reset Bus Pirate to user terminal: ",
        if self.spi.resetBP():
            print "OK."
        else:
            print "failed."
            sys.exit()

    def send_single_spi_command(self, data=[]):
        self.spi.CS_Low()
        ret = self.spi.bulk_trans(len(data), data)
        self.spi.CS_High()
        return ret

    def send_spi_command(self, data=[]):
        return self.spi.bulk_trans(len(data), data)

    def is_bit_set(self, check, bit):
        return (check & (1 << bit) != 0)

    def set_bit(self, check, bit):
        return check | (1 << bit)

    def unset_bit(self, check, bit):
        return check & ~(1 << bit)

    def parse_SR(self):
        SR1, SR2, SR3 = self.get_SR()

        print "Parsing STATUS_REGISTERS"
        SR1_Dict = {
            "SR_SRP0": self.is_bit_set(SR1, self.SR_SRP0), "SR_BP4": self.is_bit_set(SR1, self.SR_BP4),
            "SR_BP3": self.is_bit_set(SR1, self.SR_BP3), "SR_BP2": self.is_bit_set(SR1, self.SR_BP2),
            "SR_BP1": self.is_bit_set(SR1, self.SR_BP1), "SR_BP0": self.is_bit_set(SR1, self.SR_BP0),
            "SR_WEL": self.is_bit_set(SR1, self.SR_WEL), "SR_WIP": self.is_bit_set(SR1, self.SR_WIP)
        }

        SR2_Dict = {
            "SR_SUS1": self.is_bit_set(SR1, self.SR_SUS1), "SR_CMP": self.is_bit_set(SR1, self.SR_CMP),
            "SR_LB3": self.is_bit_set(SR1, self.SR_LB3), "SR_LB2": self.is_bit_set(SR1, self.SR_LB2),
            "SR_LB1": self.is_bit_set(SR1, self.SR_LB1), "SR_SUS2": self.is_bit_set(SR1, self.SR_SUS2),
            "SR_QE": self.is_bit_set(SR1, self.SR_QE), "SR_SRP1": self.is_bit_set(SR1, self.SR_SRP1)
        }

        SR3_Dict = {
            "SR_HOLD_RST": self.is_bit_set(SR1, self.SR_HOLD_RST), "SR_DRV1": self.is_bit_set(SR1, self.SR_DRV1),
            "SR_DRV0": self.is_bit_set(SR1, self.SR_DRV0), "SR_WPS": self.is_bit_set(SR1, self.SR_WPS),
        }
        for i in [SR1_Dict, SR2_Dict]:
            for item in i:
                if i[item]:
                    print "ENABLED: " + repr(item)

    def get_SR(self, SR_NUM=None):
        if SR_NUM:
            dsrnum = {1:self.CMD_RDSR1, 2:self.CMD_RDSR2, 3:self.CMD_RDSR3}
            ret = ord(self.send_single_spi_command([dsrnum[SR_NUM], 0x00])[1])
            return ret

        ret1 = ord(self.send_single_spi_command([self.CMD_RDSR1, 0x00])[1])    
        ret2 = ord(self.send_single_spi_command([self.CMD_RDSR2, 0x00])[1])
        ret3 = ord(self.send_single_spi_command([self.CMD_RDSR3, 0x00])[1])

        return [ret1, ret2, ret3]

    def read_id(self):
        ret = self.send_single_spi_command([self.CMD_RDID, 0x00, 0x00, 0x00])[1:]
        ret2 = self.send_single_spi_command([self.CMD_REMS, 0x00, 0x00, 0x00, 0x00, 0x00])[1:]

        print "Manufacturer ID: " + hex(ord(ret[0]))
        print "Memory Type: " + hex(ord(ret[1]))
        print "Capacity: " + hex(ord(ret[2]))
        print "DeviceID: " + hex(ord(ret2[4]))
        return ret
        
    def write_enable(self):
        #print "Sending Write Enable"
        self.send_single_spi_command([self.CMD_WREN])

    def write_disable(self):
        #print "Sending Write Disable"
        self.send_single_spi_command([self.CMD_WRDI])

    def dump_rom(self, output_file):
        read_size = 16

        self.spi.CS_Low()
        self.send_spi_command([self.CMD_READ, 0, 0, 0])

        with open(output_file, "wb") as f:
            for pAddress in xrange(self.chip_bytes/read_size):
                data = self.spi.bulk_trans(read_size, list([0] * read_size))
                f.write("".join(data))

                #if(pAddress % (0x100 / read_size) == 0):
                    #print "%.6X : %s" % (pAddress*read_size, repr(map(ord,list(data))))

        self.spi.CS_High()

    def is_busy(self):
        SR = self.get_SR(1)
        if self.is_bit_set(SR, self.SR_WIP):
            return True
        return False

    def chip_erase(self):
        print "Erasing Entire Chip..."

        #Enable WREN
        self.write_enable()

        #Send chip erase
        self.send_single_spi_command([self.CMD_CE])

        while self.is_busy():
            self.spi.timeout(0.1)
        print "Erase Complete..."

    def chunk(self, data, chunk_size):
        return [data[i:i + chunk_size] for i in xrange(0, len(data), chunk_size)]

    def write_rom(self, input_file):
        write_size = 16

        with open(input_file, "rb") as f:
            input_data = f.read()

        input_data_len = len(input_data)
        if input_data_len > self.chip_bytes:
            print "Input file is bigger than maximum flash size"
            return

        if input_data_len % write_size != 0:
            print "Data is not divisible by %d" % (write_size)
            return

        self.chip_erase()

        print "Writing file to flash..."

        chunk_size = 256    #Datasheet indicates each transfer is 255 bytes at a time
        data_chunks = self.chunk(input_data, chunk_size)

        total_written = 0
        for dc in xrange(len(data_chunks)):
            prog_address = dc << 8
            #Enable WREN
            self.write_enable()

            self.spi.CS_Low()
            spi_write_cmd = [self.CMD_PP,] + map(ord, list(struct.pack(">L",prog_address)))[1:]
            self.send_spi_command(spi_write_cmd)

            to_write_chunks = self.chunk(data_chunks[dc], write_size)   #bus pirate can only latch in 16 byes each time
            
            for twc in to_write_chunks:
                conv_arr = map(int, list(ord(i) for i in twc))
                self.spi.bulk_trans(write_size, conv_arr)
                total_written += write_size
            self.spi.CS_High()

            if total_written % 4096 == 0:
                print "Total bytes written: %s of %s" % ("{:,}".format(total_written), "{:,}".format(input_data_len))

        print "Total bytes written: %s" % ("{:,}".format(total_written))