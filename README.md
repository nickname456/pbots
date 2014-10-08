pbots
=====


1) Setup

- Grab the server from https://github.com/theaigames/poker-engine
(i.e. git clone https://github.com/theaigames/poker-engine.git)
- Follow build instructions
- For non-Java people: make sure your JDK and JRE are the same or compatible versions (may be out of sync if your java packages on linux were just pulled in as dependencies any old way, like me)
    - "java -version" and "javac -version"
- "chmod 755 multibot.py"
- Test run, something like: "java -classpath /home/nick/projects/pokerbot/theaigames/poker-engine/bin nl.starapple.backend.RunPoker 2000 ./multibot.py ./multibot.py"


2) Details

- The engine exec()s the supplied commands as the 2 players and communicates via  simple protocol on stdin/stdout. So you can use any language you want
- Protocol here http://theaigames.com/competitions/heads-up-omaha/getting-started#
- Engine does the second most popular variant of poker, PLO, by default (http://en.wikipedia.org/wiki/Omaha_hold_%27em), because it is a less solved game than the more popular No Limit Texas Holdem. Depending on what people want, we could go either way


3) Evaluation
- Does the "score" say how many hands the match took? That's not a very good metric. 
- % of games won over a large sample would be better
- Note GNU parallel "bug" in Debian, where --tollef is default
- To experiment I have been doing something like "seq 50 | parallel --gnu  java -classpath /home/nick/projects/pokerbot/theaigames/poker-engine/bin nl.starapple.backend.RunPoker 2000 "./multibot.py\ ExampleBot" "./multibot.py\ PairBot" 2> err2.txt 1> out2.txt" and then `egrep "Winner|Score" out.*.txt`
- Haven't decided how best for bot writers to compare their results without sharing code. % won against an agreed set of dumber bots?

