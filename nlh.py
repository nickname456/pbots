#
# Some simple NLH bots for benchmarking
#

import sys
from sys import stderr, stdin, stdout
from poker import Card, Hand, Pocket, Table
from bot import Bot
import random

class ExampleBot(Bot):
    
    def make_move(self, timeout):
        '''
        Checks cards and makes a move
        '''
        
        # Get average card value
        average_card_value = 0
        for card in self.bots['me']['pocket']:
            average_card_value += card.number
        average_card_value /= 2

        # Check if we have something good
        if average_card_value > 8:
            return 'raise ' + str(2 * int(self.match_settings['bigBlind']))
        elif average_card_value > 4:
            return 'call ' + self.match_settings['amountToCall']

        return 'check 0'

class CallBot(Bot):
    def make_move(self, timeout):
        if self.match_settings['amountToCall']!=0:
            return 'call ' + self.match_settings['amountToCall']
        else:
            return 'check 0'

class AvgValuePotBot(Bot):
    def make_move(self, timeout):
        
        # Get average card value
        average_card_value = 0
        for card in self.bots['me']['pocket']:
            average_card_value += card.number
        average_card_value /= 2

        # Check if we have something good
        if average_card_value > 8:
            pot = self.match_settings["maxWinPot"]
            # pot 120, 30 for me to call, "raise 120" means "raise 120 after calling 30" in this protocol
            return "raise " + str(pot)
        elif average_card_value > 4:
            return 'call ' + self.match_settings['amountToCall']
        else:
            return 'check 0' # might fold if there's a bet

class PotBot(Bot):
    def make_move(self, timeout):
        pot = self.match_settings["maxWinPot"]
        # pot 120, 30 for me to call, "raise 120" means "raise 120 after calling 30" in this protocol
        return "raise " + str(pot)

class RandomBot(Bot):
    def __init__(self):
        Bot.__init__(self)
        random.seed()

    def make_move(self, timeout):
       
        x = random.random()*4
        if x<1:
            return "raise " + str(self.bots['me']['stack'])
        elif x<2:
            return "fold 0"
        elif x<3:
            return "fold 0"
            pot = self.match_settings["maxWinPot"]
            return "raise " + str(pot)
        else:
            if self.match_settings['amountToCall']!=0:
                return 'call ' + (self.match_settings['amountToCall'])
            else:
                return 'check 0'

class FoldBot(Bot):
    def make_move(self, timeout):
        return "fold 0"

