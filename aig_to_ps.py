# convert aigames hand history to ps hand history, for visualisation
import sys
import poker

hand_names = {'9': "royal flush",
              '8': "straight flush",
              '7': "four of a kind",
              '6': "full house",
              '5': "a flush",
              '4': "a straight",
              '3': "three of a kind",
              '2': "two pair",
              '1': "a pair of",
              '0': "high card",
                }
value_names = ["Deuce","Three","Four","Five","Six","Seven","Eight","Nine","Ten","Jack","Queen","King","Ace"]

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

# FIXME: output 2 dumps, one from each players' point of view/
# If you import everything at once into universal replayer, it shows
# each hand "twice"
def main():
    #header = "PokerStars Game #27738502010: Tournament #160417133, $0.25+$0.00 Hold'em No Limit - Level XV (250/500) - 2009/05/02 13:32:38 ET"
    #header_fmt = "PokerStars Game #%d: Tournament #%d, $0.25+$0.00 Hold'em No Limit - Level %s (%s/%s) - %s ET"
    #header_fmt = "PokerStars Hand #%s: Tournament #%d, $0.25+$0.00 USD Hold'em No Limit - Level %s (%s/%s) - %s ET"
    header_fmt = "PokerStars Hand #%s: Tournament #%d, $0.25+$0.00 USD Omaha Pot Limit - Level %s (%s/%s) - %s ET"
    hand_no = '0'
    tourney_no = 0
    lvl = 0
    (sb,bb) = ("250","500")
    time_str = '2009/05/02 13:32:38' # TODO: advance

    header = header_fmt % (hand_no,tourney_no,lvl,sb,bb,time_str)

    # FIXME: what's the table numbering here?
    # FIXME: what's heads up lablled as?
    #hand_header_fmt = "Table '160417133 3' 9-max Seat #8 is the button "
    hand_header_fmt = "Table '160417133 %s' 2-max Seat #%d is the button "

    mystery_no= "1" # guess at meaning
    button_no = 1
    p1_chips = -1
    p2_chips = -1
    p1_in_pot = 0
    p2_in_pot = 0
    amount_to_call=0 # from start of street
    current_bet = 0
    hole_cards_done = False # assuming we see 1 player'scards per dump
    showdown_started = False
    full_board = None  # XXX: Do we only print eval on river, or for eg say they have 2 pair on the flop if we're all in?

    for line in sys.stdin:
        bits = line.strip().split(" ")
        if bits[0]=='Match':
            data = bits[2]
            if bits[1]=='round':
                hand_no = data
                hole_cards_done = False
                showdown_started = False
            elif bits[1]=='smallBlind':
                sb = data
            elif bits[1]=='bigBlind':
                if data!=bb:
                    bb = data
                    lvl += 1
                    roman_lvl= int_to_roman(lvl)
            elif bits[1]=='onButton':
                if data=='player1':
                    button_no = 1
                elif data=='player2':
                    button_no = 2
                else:
                    print line
                    assert False
                
                print
                print "*********** # %s **************" % (hand_no,)

                header = header_fmt % (hand_no,tourney_no,roman_lvl,sb,bb,time_str)
                print header
                hand_header = hand_header_fmt % (mystery_no,button_no)
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
                    full_board = cards
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
                print "player1: posts %s %s" % (blind_type,bits[2])
                p1_in_pot += int(bits[2])
            elif bits[0]=='player2':
                blind_type = "small blind" if button_no==2 else "big blind"
                print "player2: posts %s %s" % (blind_type,bits[2])
                p2_in_pot += int(bits[2])
            else:
                print line
                assert False
            assert p1_in_pot <= p1_chips
            assert p2_in_pot <= p2_chips
        elif bits[1]=='finished':
            continue
        elif bits[1]=='hand':
            # Phontaz: shows [9s 9h] (two pair, Nines and Deuces)
            # ElT007: shows [Qd Qc] (two pair, Queens and Deuces)
            if not hole_cards_done:
                print "*** HOLE CARDS ***" # XXX: assuming only get 1 player'shand per dump
                if bits[0]=='player1':
                    print "Dealt to player1",bits[2].replace(","," ")
                elif bits[0]=='player2':
                    print "Dealt to player2",bits[2].replace(","," ")
                else:
                    print line
                    assert False
                hole_cards_done = True
            else:
                if not showdown_started:
                    print "*** SHOW DOWN ***"
                    showdown_started = True
                hole_cards = bits[2][1:-1].split(",")
                best_combo = None
                for i in range(0,4):
                    for j in range(i+1,4):
                        c1,c2 = hole_cards[i],hole_cards[j]
                        for b1 in range(0,5):
                            for b2 in range(b1+1,5):
                                for b3 in range(b2+1,5):
                                    c3,c4,c5 = full_board[b1],full_board[b2],full_board[b3]
                                    cards = [poker.Card(c[1],c[0]) for c in [c1,c2,c3,c4,c5]]
                                    hand = poker.Hand(cards)
                                    if best_combo is None or hand > best_combo:
                                        best_combo = hand
                # XXX: after the hand rank, unique card values in the hand 
                #print best_combo.cards,best_combo.rank
                hand_repr=""
                r = best_combo.rank
                if r[0]=='0':
                    hand_repr = "%s, %ss" % (hand_names[r[0]],
                                        value_names[r[1]])
                elif r[0]=='1':
                    hand_repr = "%s %ss" % (hand_names[r[0]],
                                        value_names[r[1]])
                elif r[0]=='2':
                    hand_repr = "%s, %ss and %ss" % (hand_names[r[0]],
                                        value_names[r[1]],
                                        value_names[r[2]],)
                elif r[0]=='3':
                    hand_repr = "%s, %ss" % (hand_names[r[0]],
                                        value_names[r[1]])
                elif r[0]=='4':
                    hand_repr = "%s, %s high" % (hand_names[r[0]],
                                        value_names[r[1]])
                elif r[0]=='5':
                    hand_repr = "%s, %s high" % (hand_names[r[0]],
                                        value_names[r[1]])
                elif r[0]=='6':
                    # TODO: not validated against actual hh
                    hand_repr = "%s, %ss over %ss" % (hand_names[r[0]],
                                        value_names[r[1]],
                                        value_names[r[2]],)
                elif r[0]=='7':
                    # TODO: not validated against actual hh
                    hand_repr = "%s, %ss" % (hand_names[r[0]],
                                        value_names[r[1]])
                elif r[0]=='8':
                    # TODO: not validated against actual hh
                    hand_repr = "%s, %s high" % (hand_names[r[0]],
                                        value_names[r[1]])
                elif r[0]=='9':
                    # TODO: not validated against actual hh
                    hand_repr = "%s" % (hand_names[r[0]],)
                else:
                    print r
                    assert False
                print "%s: shows %s (%s)" % (bits[0],bits[2].replace(","," "),hand_repr)

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
            # calls X where X is amount remaining. eg. sb 10, bb 20, sb "calls 10"    
            print "%s: calls %s%s" % (bits[0],bits[2],suffix)
            assert p1_in_pot <= p1_chips
            assert p2_in_pot <= p2_chips
        elif bits[1]=='check':
            print "%s: checks" % (bits[0],)
            continue
        elif bits[1]=='fold':
            print "%s: folds" % (bits[0],)
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
                print "%s: bets %s%s" % (bits[0],bits[2],suffix)
            else:
                # raise
                print "%s: raises %s to %d%s" % (bits[0],bits[2],current_bet,suffix)
            assert p1_in_pot <= p1_chips
            assert p2_in_pot <= p2_chips
        elif bits[1]=='wins':
            # TODO Who wins what
            # TODO: uncalled bets...
            # TODO mucking hands on showdown? poker-engine never does that?
            # no side pots if heads up 

            print "%s collected %s from pot" % (bits[0],bits[2])
            
            # player1 post 10
            # player2 post 20
            # player1 hand [Jh,Kd,Ac,Kc]
            # Match maxWinPot 30
            # Match amountToCall 10
            # Action player1 10000
            # Output from your bot: "raise 40"
            # player1 raise 40
            # player2 fold 0
            # player1 wins 80
            # Match round 7
            #
            # mvinc131: raises 2710 to 2770 and is all-in
            # person456: folds
            # Uncalled bet (2710) returned to mvinc131
            # mvinc131 collected 130 from pot
            #
            # b3rimba: raises 433 to 453 and is all-in
            # mvinc131: calls 273 and is all-in
            # Uncalled bet (160) returned to b3rimba
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
# read https://github.com/HHSmithy/PokerHandHistoryParser/blob/master/HandHistories.Parser/Parsers/FastParser/PokerStars/PokerStarsFastParserImpl.cs http://poker.readthedocs.org/en/latest/handhistory.html
# cat poker-engine/out.txt| python pbots/aig_to_ps.py 
if __name__=='__main__':
    main()
