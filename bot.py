from sys import stderr, stdin, stdout
from poker import Card, Hand, Pocket, Table

# Copied or simplified from initial example code
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
        
        # XXX:
        # Don't always get amountToCall preflop for some reason,
        # so need to remember the blinds
        self.sb = 0

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
                elif command == 'match':
                    self.update_match_info(parts[1:])
                elif command.startswith('player'):
                    self.update_game_state(parts[0], parts[1], parts[2])
                elif command == 'action':
                    stdout.write(self.make_move(parts[2]) + '\n')
                    stdout.flush()
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

        if key=='smallBlind':
            self.sb = int(value)


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

            elif info_type == 'call':
                self.bots['me']['stack'] -= int(info_value)

            elif info_type == 'raise':
                amt = int(info_value) + int(self.match_settings['amountToCall']) if 'amountToCall' in self.match_settings else self.sb
                self.bots['me']['stack'] -= amt

            # Update bot cards
            elif info_type == 'hand':
                self.bots['me']['pocket'] = Pocket(self.parse_cards(info_value))

            # Round winnings, currently unused
            elif info_type == 'wins':
                self.bots['me']['stack'] += int(info_value)
            elif info_type == 'fold':
                pass # no state adjustment needed
            elif info_type == 'check':
                pass # no state adjustment needed
            else:
                stderr.write('Unknown info_type (me): %s %s\n' % (info_type, info_value))

        else:

            # Update opponent stack
            if info_type == 'stack':
                self.bots['opponent']['stack'] = int(info_value)

            # Remove blind from opponent stack
            elif info_type == 'post':
                self.bots['opponent']['stack'] -= int(info_value)

            elif info_type == 'call':
                self.bots['opponent']['stack'] -= int(info_value)

            elif info_type == 'raise':
                amt = int(info_value) + int(self.match_settings['amountToCall']) if 'amountToCall' in self.match_settings else self.sb
                self.bots['opponent']['stack'] -= amt

            # Opponent hand on showdown, currently unused
            elif info_type == 'hand':
                pass

            # Opponent round winnings, currently unused
            elif info_type == 'wins':
                self.bots['opponent']['stack'] += int(info_value)
            elif info_type == 'fold':
                pass # no state adjustment needed
            elif info_type == 'check':
                pass # no state adjustment needed
            else:
                stderr.write('Unknown info_type (me): %s %s\n' % (info_type, info_value))

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

