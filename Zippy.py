# Zippy.py - Tries to observe the speed limit
# by Jack Beal, 2018

import libpyAI as ai

class Zippy:

    def __init__(self, speedLimit):
        self.speedLimite = speedLimit
        self.frameCount = 0

        # Autostart
        ai.start(self.AI_loop,["-name","Zippy","-join","localhost"])

    # MAIN LOOP =============================================================

    def AI_loop(self):

        # Release keys
        ai.thrust(0)

        # Controller logic
        if ai.selfSpeed() < self.speedLimit:
            ai.thrust(1)

        # Track updated information
        self.frameCount += 1


def main(*args):
    agent = Zippy()

if __name__ == "__main__":
    main()
