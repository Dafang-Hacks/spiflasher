# spiflasher
Flasher for GD25Q128C
https://4donline.ihs.com/images/VipMasterIC/IC/ELMC/ELMCS00588/ELMCS00588-1.pdf

###  Hardware requirements:

1. An Clip Adapter
2. Bus Pirate


### Software requirements

1. flashrom and/or
2. python2.7


## Flashing the chip:

First get the uboot and prepare it for flashing:
```
cp -r uboot-fullhd.bin fullflash.bin
dd if=/dev/zero of=fullflash.bin bs=1 count=1 seek=16777215
```

Next you can flash using a buspirate(it will take a while:

```

sudo ./flashrom2 -p buspirate_spi:dev=/dev/ttyUSB0,spispeed=1M -VVV -c GD25Q128C --layout rom.layout --image boot -w fullflash.bin

```


## Alternative for impatient

There is a nice script from https://github.com/xwings/yi_home_cam_v1/blob/master/GD25Q128.py

```
./write.py
```