#Xpilot-AI Team 2012
#Run: python3 Spinner.py

import libpyAI as ai
def AI_loop():
    ai.setPower(((ai.selfX()/3)%60)+4)
    ai.setTurnSpeed(((ai.selfY()/1.5)%60)+4)
    ai.turnRight(1)
    ai.thrust(1)

ai.start(AI_loop,["-name","Spinner"])
