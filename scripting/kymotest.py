from bluelake import pause, confocal

iterations = 20
preset_name = "single_kymo"

for i in range(iterations):
    confocal.start_scan(preset_name)
    pause(1)

