Copyright: Juda Kaleta <juda.kaleta@gmail.com> and Arthur Milchior <arthur@milchior.fr>
License: GNU GPL, version 3 or later; http://www.gnu.org/copyleft/gpl.html
Feel free to contribute to this plugin: https://github.com/yetty/anki-unseen-and-buried-counts
Add-on number 161964983 in anki web

Allow to control deck's browser display.
By default, for each deck, it shows:
-its number of due cards
-its number of new cards
-its number of unseen cards
-its number of buried cards
-the option group of the deck

In order to hide one of those field, Tools>add-ons>ConfigureDeck>Edit and replace True by False in the related line.
E.g. if you want to hide the number of due cards, search for the line:
"new" : True ,#number of new cards
and replace it by
"new" : True ,#number of new cards

