#!/usr/bin/python
#-----------------------------------------------------------#
# Heads Up Omaha Challange - Starter Bot                    #
#===========================================================#
#                                                           #
# Last update: 22 May, 2014                                 #
#                                                           #
# @author Nick, orig example Jackie <jackie@starapple.nl>   #
# @version 1.0                                              #
# @license MIT License (http://opensource.org/licenses/MIT) #
#-----------------------------------------------------------#
from sys import stderr, stdin, stdout
import sys
from poker import Card, Hand, Pocket, Table
import random

class Bot(object):
    '''
    Main bot class
    '''
    def __init__(self):
        '''
        Bot constructor

        Add data that needs to be persisted between rounds here.
        '''
        self.settings = {}
        self.match_settings = {}
        self.game_state = {}
        self.pocket = None
        self.bots = {
            'me': {},
            'opponent': {}
        }

    def run(self):
        '''
        Main loop

        Keeps running while begin fed data from stdin.
        Writes output to stdout, remember to flush.
        '''
        while not stdin.closed:
            try:
                rawline = stdin.readline()

                # End of file check
                if len(rawline) == 0:
                    break

                line = rawline.strip()

                # Empty lines can be ignored
                if len(line) == 0:
                    continue

                parts = line.split()
                command = parts[0].lower()

                if command == 'settings':
                    self.update_settings(parts[1:])
                    pass
                elif command == 'match':
                    self.update_match_info(parts[1:])
                    pass
                elif command.startswith('player'):
                    self.update_game_state(parts[0], parts[1], parts[2])
                    pass
                elif command == 'action':
                    stdout.write(self.make_move(parts[2]) + '\n')
                    stdout.flush()
                    pass
                else:
                    stderr.write('Unknown command: %s\n' % (command))
                    stderr.flush()
            except EOFError:
                return

    def update_settings(self, options):
        '''
        Updates game settings
        '''
        key, value = options
        self.settings[key] = value

    def update_match_info(self, options):
        '''
        Updates match information
        '''
        key, value = options
        self.match_settings[key] = value

    def update_game_state(self, player, info_type, info_value):
        '''
        Updates game state
        '''
        # Checks if info pertains self
        if player == self.settings['yourBot']:
            
            # Update bot stack
            if info_type == 'stack':
                self.bots['me']['stack'] = int(info_value)

            # Remove blind from stack
            elif info_type == 'post':
                self.bots['me']['stack'] -= int(info_value)

            # Update bot cards
            elif info_type == 'hand':
                self.bots['me']['pocket'] = Pocket(self.parse_cards(info_value))

            # Round winnings, currently unused
            elif info_type == 'wins':
                pass

            else:
                stderr.write('Unknown info_type: %s\n' % (info_type))

        else:

            # Update opponent stack
            if info_type == 'stack':
                self.bots['opponent']['stack'] = int(info_value)

            # Remove blind from opponent stack
            elif info_type == 'post':
                self.bots['opponent']['stack'] -= int(info_value)

            # Opponent hand on showdown, currently unused
            elif info_type == 'hand':
                pass

            # Opponent round winnings, currently unused
            elif info_type == 'wins':
                pass

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

    def parse_cards(self, cards_string):
        '''
        Parses string of cards and returns a list of Card objects
        '''
        return [Card(card[1], card[0]) for card in cards_string[1:-1].split(',')]




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
        current_best=-1
        for i in range(0,len(cards)):
            for j in range(1,len(cards)):
                if i!=j and cards[i].value==cards[j].value and cards[i].value > current_best:
                    current_best = cards[i].value
        for card in hand:
            if card.value==current_best:
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


if __name__ == '__main__':
    if len(sys.argv)==2:
        name = sys.argv[1]
        botnames = ["ExampleBot","CallBot","AvgValuePotBot","PotBot","RandomBot","FoldBot","PairBot"]
        if name in botnames:
            botclasses = [ExampleBot,CallBot,AvgValuePotBot,PotBot,RandomBot,FoldBot,PairBot]
            c = botclasses[botnames.index(name)]
            c().run()
        else:
            ExampleBot().run()
    else:
        ExampleBot().run()
