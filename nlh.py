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


# Just contains some utility functions, also some general computation
# done before derived classes make their decisions
class ThinkingBot(Bot):
    def __init__(self):
        self.has_raised_street = False
        self.on_button = None
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
    
    def has_pair_using_board(self,cards,hand):
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
        if key=="onButton":
            if value == self.settings['yourBot']:
                self.on_button = True
            else:
                self.on_button = False

        Bot.update_match_info(self,options)

    def make_move(self, timeout):
        
        is_preflop = not 'table' in self.match_settings
        pot = int(self.match_settings["maxWinPot"])
        call_amt = int(self.match_settings["amountToCall"])
        board = []
        if not is_preflop:
            board = self.parse_cards(self.match_settings['table'])
       
        assert self.on_button is not None

        return self.on_make_move(timeout,is_preflop,pot,call_amt,board)

    # Subclasses implment
    def on_make_move(timeout,is_preflop,pot,board):
        assert False
        

# if we don't at least make a pair on the flop. fold
class PairBot(ThinkingBot):

    def __init__(self):
        ThinkingBot.__init__(self)


    def on_make_move(self,timeout,is_preflop,pot,call_amt,board):
        
        if is_preflop:

            average_card_value = 0
            for card in self.bots['me']['pocket']:
                average_card_value += card.number
            average_card_value /= 2
            
            if self.contains_pair(self.bots['me']['pocket'].cards):
                if not self.has_raised_street:
                    return "raise %d" % pot
                else:
                    return "call %d" % call_amt
            elif average_card_value>8:
                return "call %d" % call_amt
            else:
                return 'check 0' # might fold if there's a bet
        else:
            if self.has_best_pair(self.bots['me']['pocket'].cards+board, \
                                    self.bots['me']['pocket'].cards):
                return "raise %d " % pot
            elif self.has_pair_using_board(self.bots['me']['pocket'].cards+board,self.bots['me']['pocket'].cards):
                # TODO: second pair not using board is ok too
                return "call %d" % call_amt
            return 'check 0' # might fold if there's a bet


# TODO: cards_in_top_n_percent(n)
# TODO: more heuristics

class TightBot(ThinkingBot):

    # Button opening ranges. Maybe include K8o..T8o,97o, since this is HU?
    unsuited_button=["A"+c for c in "AKQJT98765432"]+\
                    ["K"+c for c in "KQJT9"]+\
                    ["Q"+c for c in "QJT9"]+\
                    ["J"+c for c in "JT9"]+\
                    ["TT","T9","99","98","88","87","77","76","66","55","44","33","22"]
    suited_button=["A"+c for c in "AKQJT98765432"]+\
                  ["K"+c for c in "KQJT98765432"]+\
                    ["Q"+c for c in "QJT98"]+\
                    ["J"+c for c in "JT98"]+\
                    ["TT","T9","T8","T7","99","98","97","88","87","86","77","76","66","65","55","54","44","33","22"]
    
    unsuited_cutoff=["A"+c for c in "AKQJT98"]+\
                    ["K"+c for c in "KQJT"]+\
                    ["Q"+c for c in "QJT"]+\
                    ["J"+c for c in "JT"]+\
                    ["TT","99","88","77","66","55","44","33","22"]
    suited_cutoff=["A"+c for c in "AKQJT98765432"]+\
                  ["K"+c for c in "KQJT9"]+\
                    ["Q"+c for c in "QJT9"]+\
                    ["J"+c for c in "JT9"]+\
                    ["TT","T9","T8","99","98","88","87","77","76","66","65","55","44","33","22"]
    
    def __init__(self):
        ThinkingBot.__init__(self)

    def has_2nd_pair_or_better(self,board,hand):
        board_ranks = list(set([c.number for c in board]))
        board_ranks.sort()

        h0,h1 = hand[0].number,hand[1].number

        if h0==h1:
            if len(board_ranks)>=2:
                return h0 >= board_ranks[-2]
            else:
                return True
        else:
            b0 = board_ranks[-1]
            if h0==b0 or h1==b0:
                return True
            if len(board_ranks)>=2:
                b1 = board_ranks[-2]
                if h0==b1 or h1==b1:
                    return True
            return False
    
    # for flop,turn,river
    def all_5card_hands(cards):
        if len(cards)==5:
            yield Hand(cards)
        elif len(cards)==6:
            for i in range(0,6):
                yield Hand(cards[0:i]+cards[(i+1):])
        elif len(cards)==7:
            for i in range(0,7):
                for j in range(i+1,7):
                yield Hand(cards[0:i]+cards[(i+1):j]+cards[(j+1):])
        else
            print "not postflop?",cards
            assert False

    def has_made_hand_better_than_pair(self,board,hand):
        # not being smart enough to think about playing the board yet
        for h in self.all_5card_hands(board+hand):
            if h.rank[0]>='2':
                return True
        return False

    def has_flush_draw(self,board,hand):
        return False # FIXME

    def has_straight_draw(self,board,hand):
        return False # FIXME

    def on_make_move(self,timeout,is_preflop,pot,call_amt,board):
        
        if is_preflop:
            return self.on_make_move_preflop(timeout,is_preflop,pot,call_amt,board)
        else:
            hand = self.bots['me']['pocket'].cards
            # FIXME!!
            # bet if we have second pair or better made
            # call if we have a 4 card draw
            # fold otherwise
            if call_amt!=0:
                return "call %d" % call_amt
            else:
                return "check 0"
        assert False
   
   
    # Ordered string representation for looking up in our tables
    def unparse_hand(self)
        hand = self.bots['me']['pocket'].cards
        values = '23456789TJQKA'
        a = hand[0].value
        b = hand[1].value
        hand_str = a+b if values.index(a)>values.index(b) else b+a
        is_suited = hand[0].suit==hand[1].suit
        return (hand_str,is_suited)

    def on_make_move_preflop(self,timeout,is_preflop,pot,call_amt,board):
            (hand_str,is_suited) = self.unparse_hand()

            if self.on_button:
                if not self.has_raised_street:
                    should_open = False
                    if is_suited:
                        should_open = hand_str in TightBot.suited_button
                    else:
                        should_open = hand_str in TightBot.unsuited_button
                    if should_open:
                        self.has_raised_street = True
                        # raises expressed in this protocol as amt above calling
                        return "raise " + str(pot) # 2.5bb total
                    else:
                        return "fold 0"
                else:
                    if call_amt*2 <= pot:
                        return "call %d" % call_amt
                    else:
                        return "fold 0"
            else:
                button_raised = call_amt!=0
                if button_raised:
                    hand_strong_enough = False
                    if is_suited:
                        hand_strong_enough = hand_str in TightBot.suited_cutoff
                    else:
                        hand_strong_enough = hand_str in TightBot.unsuited_cutoff
                    should_call = hand_strong_enough and call_amt*2<=pot
                    if should_call:
                        return "call %d" % call_amt
                    else:
                        return "fold 0"
                else:
                    hand_strong_enough = False
                    if is_suited:
                        hand_strong_enough = hand_str in TightBot.suited_cutoff
                    else:
                        hand_strong_enough = hand_str in TightBot.unsuited_cutoff
                    if hand_strong_enough:
                        return "raise " + str(pot) # 3bb total
                    else:
                        return "check 0"
