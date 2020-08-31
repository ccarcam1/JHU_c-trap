# imaging automation for SSB
# pull DNA for n time, then return it and start imaging

from bluelake import pause, confocal, excitation_lasers, Trap

# FUNCTIONS =================================
def timeprogression(time,numsteps):
    stepsize=round(time/numsteps,2)
    for i in range(1,numsteps+1):
        pause(stepsize)
        print(" "+str(round(i*stepsize*100/time)) + "% of time has elapsed ("+str(round(i*stepsize/60,1))+" min)")

# MAIN ======================================
hangtime = 5 #how long it stays stretched
imagetime = 500 #how long to image for
proteintime = 5 #waiting for protein to bind

excitation_lasers.green = 0
trap = Trap("1", "XY")
# stretching
print("stretching for "+str(hangtime)+" sec")
trap.move_to(waypoint="more streatch", speed=5)
timeprogression(hangtime,5)
trap.move_to(waypoint="measure point", speed=5)
print("stretch done")

print("just hanging out for a bit for protein binding ("+str(proteintime)+" sec)") 
timeprogression(proteintime,5)
#turn on laser
excitation_lasers.green = 20

#start imaging
confocal.start_scan("SSB kymo")
print("Scan started: "+str(imagetime)+"sec")
timeprogression(imagetime,10)

# stop imaging
confocal.abort_scan()
#turn off laser
excitation_lasers.green = 0
print("!!!! Scan ended !!!!")
