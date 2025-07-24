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



## Keyboard Backlight
➜ sudo ectool pwmgetkblight
Current keyboard backlight percent: 50

➜ sudo ectool pwmsetkblight 90
Keyboard backlight set.


## Battery
### Percentage
➜ cat /sys/class/power_supply/BAT1/capacity
90

### Charging
➜ cat /sys/class/power_supply/BAT1/status
Charging

### Health
➜ cat /sys/class/power_supply/BAT1/charge_full_design
3572000

FrameworkApp on  main [!] 
➜ cat /sys/class/power_supply/BAT1/charge_full
3016000

➜ echo $(( 100 * $(cat /sys/class/power_supply/BAT1/charge_full) / $(cat /sys/class/power_supply/BAT1/charge_full_design) ))