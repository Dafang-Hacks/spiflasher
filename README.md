# spiflasher
Flasher for GD25Q128C
https://4donline.ihs.com/images/VipMasterIC/IC/ELMC/ELMCS00588/ELMCS00588-1.pdf

###  Hardware requirements:

Ch341 Flasher


### Software requirements

flashrom


## Flashing the chip:

First get the uboot and prepare it for flashing:
```
cp -r uboot-fullhd.bin fullflash.bin
dd if=/dev/zero of=fullflash.bin bs=1 count=1 seek=16777215
```

Next you can flash it(it will take a while:

```

sudo flashrom -p ch341a_spi -V -c GD25Q128C --layout rom.layout --image boot -w fullflash.bin

```


