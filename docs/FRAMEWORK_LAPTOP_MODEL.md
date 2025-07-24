## Get Processpr
sudo dmidecode -s processor-version
11th Gen Intel(R) Core(TM) i5-1135G7 @ 2.40GHz

## SHould get model, does not work on my 11th gen
sudo dmidecode -s system-product-name 2>/dev/null || echo 'Unknown'
Laptop
sudo dmidecode -s system-version 2>/dev/null || echo 'Unknown'
A3

## Current Method
cat /sys/class/dmi/id/board_name
FRANBMCP03