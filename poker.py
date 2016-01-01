#-----------------------------------------------------------#
# Heads Up Omaha Challange - Starter Bot                    #
#===========================================================#
#                                                           #
# Last update: 22 May, 2014                                 #
#                                                           #
# @author Jackie <jackie@starapple.nl>                      #
# @version 1.0                                              #
# @license MIT License (http://opensource.org/licenses/MIT) #
#-----------------------------------------------------------#

class Card(object):
    '''
    Card class
    '''
    def __init__(self, suit, value):
        self.suit = suit
        self.value = value
        self.number = '23456789TJQKA'.find(value)

    def __repr__(self):
        return self.value+self.suit

    def __cmp__(self,other):
        n_cmp = cmp(self.number,other.number)
        if n_cmp!=0:
            return n_cmp
        return cmp(self.suit,other.suit)

class Pocket(object):
    '''
    Pocket class
    '''
    def __init__(self, cards):
        self.cards = cards

    def __iter__(self):
        return iter(self.cards)

class Table(object):
    '''
    Table class
    '''
    def __init__(self, cards):
        self.cards = cards

class Hand(object):
    '''
    Hand class
    '''
    def __init__(self, cards):
        self.cards = cards
        self.rank = Ranker.rank_five_cards(cards)

    def __gt__(self, hand):
        return self.rank > hand.rank

    def __ge__(self, hand):
        return self.rank >= hand.rank

    def __lt__(self, hand):
        return self.rank < hand.rank

    def __le__(self, hand):
        return self.rank <= hand.rank

    def __eq__(self, hand):
        return self.rank == hand.rank

    def __repr__(self):
        return "Hand:"+str(self.cards)+" rank"+str(self.rank)

class Ranker(object):
    '''
    Ranker class
    '''
    @staticmethod
    def rank_five_cards(cards):

        # List of all card values
        values = sorted(['23456789TJQKA'.find(card.value) for card in cards])

        # Checks if hand is a straight
        is_straight = all([values[i] == values[0] + i for i in range(5)])

        # Additional straight check
        if not is_straight:

            # Wheel
            is_straight = all(values[i] == values[0] + i for i in range(4)) \
                            and values[4] == 12 \
                            and values[0] == 0

            # Rotate values as the ace is weakest in this case
            values = values[1:] + values[:1]

        # Checks if hand is a flush
        is_flush = all([card.suit == cards[0].suit for card in cards])

        # Get card value counts
        value_count = {value: values.count(value) for value in values}

        # Sort value counts by most occuring
        sorted_value_count = sorted([(count, value) for value, count in value_count.items()], reverse = True)

        # Get all kinds (e.g. four of a kind, three of a kind, pair)
        kinds = [value_count[0] for value_count in sorted_value_count]

        # Get values for kinds
        kind_values = [value_count[1] for value_count in sorted_value_count]

        # Royal flush
        if is_straight and is_flush and values[0] == 8:
            return ['9'] + values        
        # Straight flush
        if is_straight and is_flush:
            return ['8'] + kind_values
        # Four of a kind
        if kinds[0] == 4:
            return ['7'] + kind_values
        # Full house
        if kinds[0] == 3 and kinds[1] == 2:
            return ['6'] + kind_values
        # Flush
        if is_flush:
            return ['5'] + kind_values
        # Straight
        if is_straight:
            return ['4'] + kind_values
        # Three of a kind
        if kinds[0] == 3:
            return ['3'] + kind_values
        # Two pair
        if kinds[0] == 2 and kinds[1] == 2:
            return ['2'] + kind_values
        # Pair
        if kinds[0] == 2:
            return ['1'] + kind_values
        # No pair
        return ['0'] + kind_values
