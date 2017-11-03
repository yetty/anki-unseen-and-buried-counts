# -*- coding: utf-8 -*-
"""Copyright: Juda Kaleta <juda.kaleta@gmail.com> and Arthur Milchior <arthur@milchior.fr>
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

In order to hide one of those field, Tools>add-ons>Unseen_and_buried_counts>Edit and replace True by False in the related line.
E.g. if you want to hide the number of due cards, search for the line:
"new" : True ,#number of new cards
and replace it by
"new" : True ,#number of new cards
"""

#############
#Write False or True depending on whether you want to see the name of the option group
userOption = {
    "option" : True ,#deck's option's name
    "buried" : True ,#number of buried cards
    "new" : True ,#number of new cards
    "unseen" : True ,#number of unsee cards
    "due" : True #number of due cards
}


from aqt.deckbrowser import DeckBrowser

TABLE_HEADER = ("""
<tr><th colspan=5 align=left>%s</th>"""% _("Deck")
                +
                ("""<th class=count>%s</th>"""%_("Due") if userOption["due"] else "")
                +
                ("""<th class=count>%s</th>"""%_("New") if userOption["new"] else "")
                +
                ("""<th class=count>%s</th>"""%_("Unseen") if userOption["unseen"] else "")
                +
                ("""<th class=count>%s</th>"""% _("Buried") if userOption["buried"] else "")
                +
                """<th class=count></th><th></th>"""
                +
                ("""<th class=count>%s</th></tr>""" %_("Option group")) if userOption["unseen"] else "")


"""An id, incremented for each render"""
def renderDeckTree(self, nodes, depth=0):
    """Html used to userOption[" the"] deck tree"""
    if not nodes:
        return ""

    node_rows = "".join([self._deckRow(node, depth, len(nodes)) for node in nodes])
    header = TABLE_HEADER + self._topLevelDragRow() if depth == 0 else ""
    footer = self._topLevelDragRow() if depth == 0 else ""
    return header + node_rows + footer


def deckRow(self, node, depth, cnt):
    """The HTML for a single deck (and its descendant)
    Keyword arguments:
    node -- (name of the deck,
             its id,
             its number of due cards,
             number of cards in learning,
             its number of new cards
             its list of children)
    depth -- indentation argument (number of ancestors)
    cnt --  the number of sibling, counting itself
    """
    name, did, due, lrn, new, children = node
    child_list = self.mw.col.decks.children(did)
    deck = self.mw.col.decks.get(did)
    confId = str(deck["conf"])
    conf = self.mw.col.decks.dconf[confId]
    confName=conf['name']
    unseen = self.mw.col.db.scalar("select count(*) from cards where did = %i and queue=0" % did)
    buried = self.mw.col.db.scalar("select count(*) from cards where did = %i and queue<0" % did)
    for (_, childId) in child_list:
        #Ineficient. It should be better to save the information in the deck.  children could probably be used. But I don't know how it is composed exactly.
        unseen += self.mw.col.db.scalar("select count(*) from cards where did = %i and queue=0" % childId)
        buried += self.mw.col.db.scalar("select count(*) from cards where did = %i and queue<0" % childId)
    
    if did == 1 and cnt > 1 and not children:
        # if the default deck is empty, hide it
        if not self.mw.col.db.scalar("select 1 from cards where did = 1"):
            return ""
    # parent toggled for collapsing
    for parent in self.mw.col.decks.parents(did):
        if parent['collapsed']:
            buff = ""
            return buff
    prefix = "-"
    if self.mw.col.decks.get(did)['collapsed']:
        prefix = "+"
    due += lrn
    def indent():
        return "&nbsp;"*6*depth
    if did == self.mw.col.conf['curDeck']:
        klass = 'deck current'
    else:
        klass = 'deck'
    buf = "<tr class='%s' id='%d'>" % (klass, did)
    # deck link
    if children:
        collapse = "<a class=collapse href='collapse:%d'>%s</a>" % (did, prefix)
    else:
        collapse = "<span class=collapse></span>"
    if deck['dyn']:
        extraclass = "filtered"
    else:
        extraclass = ""
    buf += """
    <td class=decktd colspan=5>%s%s<a class="deck %s" href='open:%d'>%s</a></td>"""% (
        indent(), collapse, extraclass, did, name)
    # due counts
    def nonzeroColour(cnt, colour):
        if not cnt:
            colour = "#e0e0e0"
        # if cnt >= 1000:
        #     cnt = "1000+"
        return "<font color='%s'>%s</font>" % (colour, cnt)
    if userOption["due"]:
        buf += "<td align=right>%s</td>"%nonzeroColour(due, "#007700")
    if userOption["new"]:
        buf += "<td align=right>%s</td>"%nonzeroColour(new, "#007700")
    if userOption["unseen"]:
        buf += "<td align=right>%s</td>"%nonzeroColour(unseen, "#007700") 
    if userOption["buried"]:
        buf += "<td align=right>%s</td>"%nonzeroColour(buried, "#007700")
    buf += "<td></td>"
    # options
    buf += "<td align=right class=opts>%s</td>" % self.mw.button(
        link="opts:%d"%did, name="<img valign=bottom src='qrc:/icons/gears.png'>&#9662;")
    if userOption["option"]:
        buf += "<td>%s</td>"%        confName
    buf += "</tr>"
    # children
    buf += self._renderDeckTree(children, depth+1)
    
    return buf
    
DeckBrowser._renderDeckTree = renderDeckTree
DeckBrowser._deckRow = deckRow
