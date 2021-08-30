# PokerNowPy

This module, which I've addapted from [PokerNowKit](https://github.com/pj4533/PokerNowKit),
parses and translates [PokerNow.club](https://www.pokernow.club/) log files to
the PokerStars format for easy importing into poker tracking software.


## Why this fork?
The original is written in swift, and I didn't feel like getting a swift instance up
and running on my machine. This meant that  I didn't get around to writing fixes when
[PokerNow.club](https://www.pokernow.club/) updated their logging format in a way that
broke the [PokerNowKit](https://github.com/pj4533/PokerNowKit) library. I figure that
there are probably others who have had the same experience.

I also chatted with the maintainer of PokerNowKit and he said he didn't plan on
maintaining the library in the near future, so this seemed like a valuable
contribution to the community.

## Running

To run you need Python 3.x.

To run, first download the log file you want to run (it should be a csv file). Then, from
the root directory of this project (that is, the one containing this README file), run 
 the following from your terminal (MacOS/Linux) or Powershell (Windows):

```
python pn2ps HERONAME PATH_TO_LOG -o OUTPUT_FILE_NAME
```

+ `HERONAME`: the name of Hero used in the PokerNow session. This is used to
  attribute hole cards (they show up as "Your hole cards: Ac9d" in PokerNow, and
  we need to know the hero name to know who to attribute them to).

+ `PATH_TO_LOG`: Path to the log file you downloaded. To get the path in Window's
  Explorer you can **Shift+Right-Click** > **Copy as path**, and the paste the
  result in your terminal/Powershell

+ `OUTPUT_FILE_NAME` the name of the output file you want to use. If you don't
  provide `-o OUTPUT_FILE_NAME` then it will just be printed to you screen and
  you can copy/paste the contents.
