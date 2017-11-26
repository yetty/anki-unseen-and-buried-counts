Copyright: Juda Kaleta <juda.kaleta@gmail.com> and Arthur Milchior <arthur@milchior.fr>
License: GNU GPL, version 3 or later; http://www.gnu.org/copyleft/gpl.html
Feel free to contribute to this plugin: https://github.com/yetty/anki-unseen-and-buried-counts
Add-on number 161964983 in anki web

Allow to control deck's browser display.
By default, for each deck, it shows:
-its number of due cards
-its number of new cards which will be seen today, according to deck's option
-its number of cards in learning
-its number of unseen cards
-its number of buried cards
-the option group of the deck

Furthermore, when a deck has no new cards, its color is red. If a descendant of a deck has no new card, its color is blue. Except if the name of the deck contains a semicolon (;)
This allow you to quickly check whether you have seen at least once every cards of a deck. It allows me to know that it is time for you to add new cards in this deck.

#Configuration
In order to configure this deck do, Tools>add-ons>ConfigureDeck>[NAME OF THIS DECK]>edit
You can choose to deactivate some columns by replacing True by False in the first few lines. 
E.g. if you want to hide the number of due cards, search for the line:
    "new" : True ,#number of new cards
and replace it by
    "new" : True ,#number of new cards

Similarly, if you want to change the colors blue and red to other colors, edit the name of the colors (edit to black, if you want to remove this functionality)


