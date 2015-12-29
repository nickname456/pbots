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
import sys
import argparse
import plo
import nlh

# eg. java -classpath /home/nick/projects/pokerbot/theaigames/poker-engine/bin nl.starapple.backend.RunPoker 2000 "./pbots/multibot.py --game=PLO --bot-name=ExampleBot" "./pbot_nick/nickbot.py" 123 18
# I've patched the engine to take an rng seed and a game type (13 for NLH 18 for PLO)

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Run a poker bot')
    parser.add_argument('--bot-name',default="ExampleBot",type=str)
    parser.add_argument('--game',default="PLO",type=str)
    args = parser.parse_args()

    botnames = []
    botclasses = []
    if args.game=="PLO":
        botnames = ["ExampleBot","CallBot","AvgValuePotBot","PotBot","RandomBot","FoldBot","PairBot","RockBot"]
        botclasses = [plo.ExampleBot,plo.CallBot,plo.AvgValuePotBot,plo.PotBot,plo.RandomBot,plo.FoldBot,plo.PairBot,plo.RockBot]
    elif args.game=="NLH":
        botnames = ["ExampleBot","CallBot","AvgValuePotBot","PotBot","RandomBot","FoldBot"]
        botclasses = [nlh.ExampleBot,nlh.CallBot,nlh.AvgValuePotBot,nlh.PotBot,nlh.RandomBot,nlh.FoldBot,]
    else:
        print "--game NLH|PLO"
        sys.exit(1)

    if args.bot_name in botnames:
        c = botclasses[botnames.index(args.bot_name)]
        c().run()
    else:
        print "for game %s bot names are %s" % (args.game,str(botnames))
