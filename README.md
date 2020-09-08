# Stop "Fiddling" With It Twitter - sfwiT

This repository contains a small Twitter client.  It uses python3 and Node.js.  Python serves as the interface between the Twitter server and my node.js web server (which uses express) that displays the information. My Twitter interface uses python-twitter which is documented at https://python-twitter.readthedocs.io/en/latest/

I run this client on one of my Raspberry PIs on my home network.  From my phone or any browsing device, I browse to that computer's port 2999 to see the latest Tweets from those I follow.  The main page displays a list of those I follow.  When I select from the list, their latest tweets are displayed.  This particular client does not tweet, I very rarely tweet since I'm mostly interested in "news".

I have a whole series of applications that I run as servers on my home network.  This application series, SFWI (stop 'fiddling' with it), provides simple applications that do only what I want and don't leak private information.  I use this application to avoid advertising, Twitter produced trends, and "customized" home timelines.  Twitter insists that it knows what I want to see.  It doesn't.  I don't want to see the same stuff over and over, I don't want to be only associating with people of "like mind".  This client is my first attempt at providing the interface I want.

# Setup

I'm running this on a Raspberry PI under Raspbian (buster).  You don't have to have a Raspberry PI or Raspbian.  This should run fine on most Debian Linux systems.

You will need git, python3, pip3, Node.js, and npm.

From a bash shell:

1) git clone https://github.com/mbroihier/sfwiT
2) cd sfwiT
3) ./configure (if you supply a port number, this alternative port number will be used for the web server)
4) Add the necessary Twitter tokens to TwitterToken.py with your favorite editor
5) Start the client using the wrapper script
   - ./sfwiTWrapper
6) Use a browser to see a list of your "friends" and their timelines
   - http://myComputer:2999 (in your browser)
