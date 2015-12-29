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
        average_card_value /= 4

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
        average_card_value /= 4

        # Check if we have something good
        if average_card_value > 8:
            # playing PLO - engine will adjust for us
            return "raise " + str(self.bots['me']['stack'])
        elif average_card_value > 4:
            return 'call ' + self.match_settings['amountToCall']
        else:
            return 'check 0' # might fold if there's a bet

class PotBot(Bot):
    def make_move(self, timeout):
        # playing PLO - engine will adjust for us
        return "raise " + str(self.bots['me']['stack'])

class RandomBot(Bot):
    def __init__(self):
        Bot.__init__(self)
        random.seed()

    def make_move(self, timeout):
       
        x = random.random()*3
        if x<1:
            # playing PLO - engine will adjust for us
            return "raise " + str(self.bots['me']['stack'])
        elif x<2:
            return "fold 0"
        else:
            if self.match_settings['amountToCall']!=0:
                return 'call ' + (self.match_settings['amountToCall'])
            else:
                return 'check 0'

class FoldBot(Bot):
    def make_move(self, timeout):
        return "fold 0"

# raise with a pair preflop, bet/call with a pair postflop
# probably full of bugs given the haste I coded it in
class PairBot(Bot):

    def __init__(self):
        self.has_raised_street = False
        Bot.__init__(self)

    def contains_pair(self,cards,threshold=0):
        #stderr.write('Checking pairs: %s\n' % str(cards,))
        for i in range(0,len(cards)):
            for j in range(1,len(cards)):
                if i!=j and cards[i].value==cards[j].value and cards[i].value >=threshold:
                    #stderr.write('pair\n')
                    return True
        return False
    
    def contains_good_pair(self,cards):
        return self.contains_pair(cards,8) # Tens

    # have to have at least one of the cards in your hand or you're playing the board
    def has_best_pair(self,cards,hand):
        board_values = [c.value for c in cards]
        highest_board_value=max(board_values)
        highest_nonboard_pair = -1
        for card in hand:
            if card.value in board_values:
                highest_nonboard_pair = card.value
        
        if highest_nonboard_pair==highest_board_value:
            return True
        return False
    
    
    def has_pair(self,cards,hand):
        for card in hand:
            if self.contains_pair(cards+[card]):
                return True
        return False
    
    def update_match_info(self, options):
        key, value = options
        if key=="round":
            self.has_raised_street = False
            if 'table' in self.match_settings:
                stderr.write('Removing runout from last hand\n')
                del self.match_settings['table']
        if key=="table":
            self.has_raised_street = False
        Bot.update_match_info(self,options)

    def make_move(self, timeout):
        
        is_preflop = not 'table' in self.match_settings
        board = []
        if not is_preflop:
            board = self.parse_cards(self.match_settings['table'])

        if is_preflop:
            if self.contains_good_pair(self.bots['me']['pocket'].cards):
                if not self.has_raised_street:
                    return "raise " + str(self.bots['me']['stack']) # pot
                else:
                    return "call " + (self.match_settings['amountToCall'])
            elif self.contains_pair(self.bots['me']['pocket'].cards):
                return "call " + (self.match_settings['amountToCall'])
            else:
                return 'check 0' # might fold if there's a bet
        else:
            if self.has_best_pair(self.bots['me']['pocket'].cards+board,self.bots['me']['pocket'].cards):
                if not self.has_raised_street:
                    return "raise " + str(self.bots['me']['stack']) # pot
                else:
                    return "call " + (self.match_settings['amountToCall'])
            elif self.has_pair(self.bots['me']['pocket'].cards+board,self.bots['me']['pocket'].cards):
                return "call " + (self.match_settings['amountToCall'])
            return 'check 0' # might fold if there's a bet


class RockBot(Bot):

    def __init__(self):
        self.has_raised_street = False
        Bot.__init__(self)

    # have to have at least one of the cards in your hand or you're playing the board
    def has_best_pair(self,cards,hand):
        board_values = [c.value for c in cards]
        highest_board_value=max(board_values)
        highest_nonboard_pair = -1
        for card in hand:
            if card.value in board_values:
                highest_nonboard_pair = card.value
        
        if highest_nonboard_pair==highest_board_value:
            return True
        return False
    
    def update_match_info(self, options):
        key, value = options
        if key=="round":
            self.has_raised_street = False
            if 'table' in self.match_settings:
                stderr.write('Removing runout from last hand\n')
                del self.match_settings['table']
        if key=="table":
            self.has_raised_street = False
        Bot.update_match_info(self,options)

    def make_move(self, timeout):
        
        is_preflop = not 'table' in self.match_settings
        board = []
        if not is_preflop:
            board = self.parse_cards(self.match_settings['table'])

        if is_preflop:
            has_all_high_cards = True
            for card in self.bots['me']['pocket']:
                if card.number < 8:
                    has_all_high_cards = False
            if has_all_high_cards:
                if not self.has_raised_street:
                    return "raise " + str(self.bots['me']['stack']) # pot
                else:
                    return "call " + (self.match_settings['amountToCall'])
        else:
            # FIXME: best hand, not best pair
            if self.has_best_pair(self.bots['me']['pocket'].cards+board,\
             self.bots['me']['pocket'].cards):
                if not self.has_raised_street:
                    return "raise " + str(self.bots['me']['stack']) # pot
                else:
                    return "call " + (self.match_settings['amountToCall'])
        return 'check 0' # might fold if there's a bet

