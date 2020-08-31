#trapping dna with ping pong automation
#will catch your beads

from bluelake import Trap, stage, fluidics, pause, reset_force, timeline, traps
import numpy as np

trap = Trap("1", "XY")
trap2 = Trap("2","XY")
pt=0.1
echannel=1 #change this to 1 if you want to end in an experiment channel
dnadwell=1 #how long to dwell in dna channel (sec)
makessDNA=1

#functions that we need to catch DNA
def pingpongforce():
    trap.move_by(dx=10,speed=5.5)
    ppf=trap.current_force
    trap.move_by(dx=-10,speed=6.5)
    return ppf

def pingpongforce2():
    trap.move_by(dx=9,speed=5.5)
    ppf1=trap2.current_force
    move_by2(1.2,5.5)
    ppf2=trap2.current_force
    trap.move_by(dx=-10.2,speed=6.5)
    print("  "+str(round(ppf1,2))+" to "+str(round(ppf2,2)))
    if (ppf1*0.77)>ppf2 or ppf2>(ppf1*1.23):
        return 1
    else:
        return 0

def pingpongforce3(): #false positive success threshold
    trap.move_by(dx=5,speed=6)
    f1=trap2.current_force
    trap.move_by(dx=5.5,speed=5)
    f2=trap2.current_force
    trap.move_by(dx=-10.5,speed=5)
    print("  -PPF"+str(round(f1,2))+" to "+str(round(f2,2)))
    if f2>(2*f1) and f2>20:
        return 1
    else:
        return 0

def move_by2(x,s): #to print the force every 0.1 step increment
    for i in np.arange(0,x,0.1):
        trap.move_by(dx=0.1,speed=s)
        print(round(trap2.current_force,2))

def gohome():
    trap.move_to(waypoint="catch DNA",speed=7)
    print("trap1 bead is home")

def pressurecycle():
    while fluidics.pressure < .6:
        fluidics.increase_pressure()
        pause(pt) #important!
    while fluidics.pressure > 0.22:
        fluidics.decrease_pressure()
        pause(pt) #important!
    print("pressure cycled")

def setpressure(pres):
    curpres=fluidics.pressure
    if curpres<pres:
        while fluidics.pressure < pres:
            fluidics.increase_pressure()
            pause(pt) #important!
    else:
        while fluidics.pressure > pres:
            fluidics.decrease_pressure()
            pause(pt) #important!

def movetoch4():
    fluidics.stop_flow()
    stage.move_to("J1")
    stage.move_to("Ch1")
    setpressure(0.1)
    fluidics.open(1,2,3,4,6)
    reset_force()
    print("setup should be ready to go")

def beadtest():
    bead1 = timeline['Tracking Match Score']['Bead 1']
    bead2 = timeline['Tracking Match Score']['Bead 2']
    bead_scores = [bead1, bead2]
    if all(bead.latest_value > 0.85 for bead in bead_scores):
        print("you already have beads")
        return 1
    else:
        print("gotta get beads")
        return 0

def catch_beads(min_score = 30) : #from Zsombor
    stage.move_to("beads")
    target_traps = traps[:2]

    target_traps[1].clear()
    target_traps[0].clear()
    bead1 = timeline['Tracking Match Score']['Bead 1']
    bead2 = timeline['Tracking Match Score']['Bead 2']
    bead_scores = [bead1, bead2]

    while any(bead.latest_value < min_score for bead in bead_scores):
        if any(0 < bead.latest_value < min_score for bead in bead_scores):
            for trap in target_traps:
                trap.clear()  # bad beads
                print('bad beads')
            pause(1)
    print("beads should be caught")

def false_positive(): #1 if it was ok, 0 if false positive
    fluidics.close(1,2,3,4,5,6)
    gohome()
    pause(0.8)
    reset_force()
    trap.move_by(dx=5,speed=6)
    f1=trap2.current_force
    trap.move_by(dx=5.5,speed=6)
    f2=trap2.current_force
    trap.move_by(dx=-10.5,speed=6)
    print("  -FP"+str(round(f1,2))+" to "+str(round(f2,2)))
    if f2>(4*f1):
        return 1
    else:
        return 0

def themainloop(): #will return 1 if caught, 0 if attempted 60 times and failed
    #check for beads first
    bt=beadtest()
    fluidics.close(1,2,3,4,5,6)
    if bt==0:
        setpressure(0.3)
        fluidics.open(1,2,3,6)
        stage.move_to("beads")
        catch_beads(86)
    else:
        #turn on fluidics
        fluidics.open(1, 2, 3, 6)

    # set up the pressure
    stage.move_to("buffer")
    setpressure(0.22)

    #set traps at initial position and reset force
    gohome()
    reset_force()
    print("initialized position")
    caught=pingpongforce3()
    attempts=1

    #moving into dna channel and starting pingpong
    while caught!=1:
        print(" we've attempted "+str(attempts)+" times")
        #print("    new force ="+str(round(pforce,2)))
        stage.move_to("DNA")
        pause(dnadwell)
        stage.move_to("buffer")
        caught=pingpongforce3();
        if attempts==10:
            return 0
        #if (attempts%10)==0:
         #   pressurecycle()
        #    attempts+=1
        else:
            attempts+=1

    print("hopefully we finished")
    return 1

def thelooploop(): #return 1 if done
    chk=0
    while chk==0:
        print("starting loop loop")
        chk=themainloop()
        if chk==1:
            chk=false_positive()
        else:
            target_traps = traps[:2]
            target_traps[1].clear()
            target_traps[0].clear()

    #hopefully caught something, move to buffer channel and reset all
    stage.move_to("buffer")
    gohome()
    fluidics.stop_flow()
    reset_force()
    print("in the buffer channel with all reset")

    #0 for no ssDNA, 1 for good, 2 for failed to pull
    if makessDNA==1:
        print("time to try for ssDNA")
        s=0
        while s != 1:
            s = ssDNAstretch()
            if s == 0:
                setpressure(0.3)
                fluidics.open(3,6)
                target_traps = traps[:2]
                target_traps[1].clear()
                target_traps[0].clear()
                fluidics.close(3,6)
                return s
            if s==2:
                continue
    else:
        return 1

def ssDNAstretch(): #0 if nothing/broke, 1 if good, 2 if unsuccessful pull
    success=0
    trap.move_to(waypoint="stretched",speed=6)
    trap.move_by(dx=12,speed=1)
    pause(0.5)
    highforce=trap2.current_force
    trap.move_by(dx=-12,speed=1)
    lowforce = trap2.current_force
    print("  -ssDNA: "+str(round(lowforce,2))+" to "+str(round(highforce,2)))
    if highforce>50:
        print("  extension ok")
        success = 1
        if lowforce>20:
            print("  looks like its still dsDNA")
            success = 2
    if success==0:
        print("  ssDNA broke ;-;")
        fluidics.open(1,2,3,6)
    if success==1:
        print("  ssDNA done !!!!")
    return success


def bigbird():
    bb = """        )_)_)__)_)_)_)__)_.
         )_))_))_ _))_ ))) )
          )_))  )~)  )_))~)  )
           )  ) )  )_) )  ) ) )  )
           )  )))  ) )  ) )~_)   ))
           | _(~   ((~ C(C( (  _(~(
          (~  (    C(   ((~ ((C(~ C(
         _(  _(   (~   (  _=~  _C(~
         (   (   (        _C=(~~
         (_    __   ~~~==(X
         _(_  _@@_  _     ~(C_
       C(~ (_ ~((~   (_      ~(C_
      (~  _C(_       _(         (C_
      (C_C(C_(     _=~            (C_
        ~(  C(                      (C
           _(                        ~(_
           (                    _      (C
           (                    ~C      ~(_
           (                     (_       (C
           (_                     ~C       ~(
            (_                      (_      ~(
    """
    print(bb)




#THIS IS THE START OF THE MAIN -----------------------------------------
finished = 0
while finished == 0:
    finished = thelooploop()

#if want to move to ch4 to ready for experiment start
if echannel==1:
    movetoch4()
    trap.move_to(waypoint="stretched",speed=3)
    print('ready to image!')

bigbird()
