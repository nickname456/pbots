# convert aigames hand history to ps hand history, for visualisation
import sys

def print_stacks(s1,s2):
    print "Seat 1: player1 (%d in chips)" % (s1,)
    print "Seat 2: player2 (%d in chips)" % (s2,)

# http://code.activestate.com/recipes/81611-roman-numerals/
# PSF licence (http://opensource.org/licenses/Python-2.0)
def int_to_roman(input):
   if type(input) != type(1):
      raise TypeError, "expected integer, got %s" % type(input)
   if not 0 < input < 4000:
      raise ValueError, "Argument must be between 1 and 3999"   
   ints = (1000, 900,  500, 400, 100,  90, 50,  40, 10,  9,   5,  4,   1)
   nums = ('M',  'CM', 'D', 'CD','C', 'XC','L','XL','X','IX','V','IV','I')
   result = ""
   for i in range(len(ints)):
      count = int(input / ints[i])
      result += nums[i] * count
      input -= ints[i] * count
   return result


def main():
    #header = "PokerStars Game #27738502010: Tournament #160417133, $0.25+$0.00 Hold'em No Limit - Level XV (250/500) - 2009/05/02 13:32:38 ET"
    header_fmt = "PokerStars Game #%d: Tournament #%d, $0.25+$0.00 Hold'em No Limit - Level %s (%s/%s) - %s ET"
    game_no = 0
    tourney_no = 0
    lvl = 0
    (sb,bb) = ("250","500")
    time_str = '2009/05/02 13:32:38'

    header = header_fmt % (game_no,tourney_no,lvl,sb,bb,time_str)

    # FIXME: what's the table numbering here?
    # FIXME: what's heads up?
    #hand_header_fmt = "Table '160417133 3' 9-max Seat #8 is the button "
    hand_header_fmt = "Table '160417133 %s' 2-max Seat #%d is the button "

    hand_no= "1" # guess at meaning
    button_no = 1
    p1_chips = -1
    p2_chips = -1
    p1_in_pot = 0
    p2_in_pot = 0
    amount_to_call=0 # from start of street
    current_bet = 0
    

    for line in sys.stdin:
        bits = line.strip().split(" ")
        if bits[0]=='Match':
            data = bits[2]
            if bits[1]=='round':
                hand_no = data
            elif bits[1]=='smallBlind':
                sb = data
            elif bits[1]=='bigBlind':
                if data!=bb:
                    bb = data
                    lvl += 1
                    roman_lvl= int_to_roman(lvl)
                    header = header_fmt % (game_no,tourney_no,roman_lvl,sb,bb,time_str)
                    print header
            elif bits[1]=='onButton':
                if data=='player1':
                    button_no = 1
                elif data=='player2':
                    button_no = 2
                else:
                    print line
                    assert False
                hand_header = hand_header_fmt % (hand_no,button_no)
                print hand_header
                
            elif bits[1]=='maxWinPot':
                continue
            elif bits[1]=='amountToCall':
                amount_to_call = int(bits[2])
                current_bet = amount_to_call*2 # sb preflop, 0 postflop streets
            elif bits[1]=='table':
                # Match table [Kd,Tc,6c]
                # *** FLOP *** [2d 2c 3c]
                # *** TURN *** [2d 2c 3c] [8h]
                # *** RIVER *** [2d 2c 3c 8h] [4d]
                cards = bits[2][1:-1].split(",")
                if len(cards)==3:
                    print "*** FLOP *** [%s %s %s]" % (cards[0],cards[1],cards[2])
                elif len(cards)==4:
                    print "*** TURN *** [%s %s %s] [%s]" % (cards[0],cards[1],cards[2],cards[3])
                elif len(cards)==5:
                    print "*** RIVER *** [%s %s %s %s] [%s]" % (cards[0],cards[1],cards[2],cards[3],cards[4])
                else:
                    print line
                    assert False
            else:
                print line
                assert False

        if bits[0] not in ["player1","player2"]:
            continue
        
        if bits[1]=='stack':
            data = bits[2]
            if bits[0]=='player1':
                p1_chips = int(data)
                p1_in_pot = 0
            elif bits[0]=='player2':
                p2_chips = int(data)
                p2_in_pot = 0
                print_stacks(p1_chips,p2_chips)
            else:
                print line
                assert False
        elif bits[1]=='post':
            if bits[0]=='player1':
                blind_type = "small blind" if button_no==1 else "big blind"
                print "player1: posts the %s %s" % (blind_type,bits[2])
                p1_in_pot += int(bits[2])
            elif bits[0]=='player2':
                blind_type = "small blind" if button_no==2 else "big blind"
                print "player2: posts the %s %s" % (blind_type,bits[2])
                p2_in_pot += int(bits[2])
            else:
                print line
                assert False
            assert p1_in_pot <= p1_chips
            assert p2_in_pot <= p2_chips
        elif bits[1]=='finished':
            continue
        elif bits[1]=='hand':
            # FIXME: get these messages at showdown too
            # Phontaz: shows [9s 9h] (two pair, Nines and Deuces)
            # ElT007: shows [Qd Qc] (two pair, Queens and Deuces)

            print "*** HOLE CARDS ***" # XXX: assuming only get 1 player'shand per dump
            if bits[0]=='player1':
                print "Dealt to player1",bits[2]
            elif bits[0]=='player2':
                print "Dealt to player2",bits[2]
            else:
                print line
                assert False
        elif bits[1]=='call':
            # player2 call 10
            # kovilen007: calls 8293 and is all-in
            suffix = ""
            if bits[0]=='player1':
                p1_in_pot += int(bits[2])
                if p1_in_pot==p1_chips:
                    suffix=" and is all-in"
            elif bits[0]=='player2':
                p2_in_pot += int(bits[2])
                if p2_in_pot==p2_chips:
                    suffix=" and is all-in"
            else:
                print line
                assert False
            print "%s: calls %s%s" % (bits[0],bits[2],suffix)
            assert p1_in_pot <= p1_chips
            assert p2_in_pot <= p2_chips
        elif bits[1]=='check':
            print "%s: check" % (bits[0],)
            # player1 check 0
            # kovilen007: checks ???
            continue
        elif bits[1]=='fold':
            print "%s: folds" % (bits[0],)
            # player1 fold 0
            # kovilen007: folds
            continue
        elif bits[1]=='raise':
            # aig doesn't distinguish between bet and raise
            # player1 raise 40
            # 
            # Orlando I: raises 15484 to 17984 and is all-in

            # XXX: raise 200 == 200 ontop of amounttocall
            # verified this for only one example
            suffix = ""
            if bits[0]=='player1':
                p1_in_pot += int(bits[2]) + amount_to_call
                current_bet += int(bits[2])
                if p1_in_pot==p1_chips:
                    suffix=" and is all-in"
            elif bits[0]=='player2':
                p2_in_pot += int(bits[2]) + amount_to_call
                current_bet += int(bits[2])
                if p2_in_pot==p2_chips:
                    suffix=" and is all-in"
            else:
                print line
                assert False

            if amount_to_call==0:
                # FIXME: bet. have no example
                print "%s: bets %s%s" % (bits[0],bits[2],suffix)
            else:
                # raise
                print "%s: raises %s to %d%s" % (bits[0],bits[2],current_bet,suffix)
            assert p1_in_pot <= p1_chips
            assert p2_in_pot <= p2_chips
        elif bits[1]=='wins':
            # TODO need to eval hands, what happens if not all pot won
            # player1 wins 40
            #
            # ElT007 collected 11018 from side pot-2
            # Orlando I: shows [5d 5h] (two pair, Fives and Deuces)
            # ElT007 collected 29073 from side pot-1
            # kovilen007: shows [Kh As] (a pair of Deuces)
            # ElT007 collected 34212 from main pot
            continue
        else:
            print line
            assert False

# cat poker-engine/out.txt| python pbots/aig_to_ps.py 
if __name__=='__main__':
    main()
