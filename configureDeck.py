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
    "learning" : True ,#number of cards in learning (a card may required to be reviewed  many times)
    "new" : True ,#number of new cards
    "unseen" : True ,#number of unsee cards
    "due" : True, #number of due cards
    "no_new": True, #Show a ! is some descendant has no new cards. Show !! if this deck has no new card. Only on deck without ";" 
}

hide_symbol =";"
default_color ="black"
color_empty = "red"
color_empty_descendant = "blue"
###########################
#code beginning
#################
kinds = [#"due",
    "learning",
    #"new",
    "unseen",
    "buried"]
#due and new are considered apart because:
#1 - they are already considered in anki's code
#2 - they consider both database state and dec's option, which means it'd be hard to compute again
from aqt.deckbrowser import DeckBrowser
import re
TABLE_HEADER = ("""
<tr><th colspan=5 align=left>%s</th>"""% _("Deck")
                +
                ("""<th class=count>%s</th>"""%_("Due") if userOption["due"] else "")
                +
                ("""<th class=count>%s</th>"""%_("New") if userOption["new"] else "")
                +
                ("""<th class=count>%s</th>"""%_("Learning") if userOption["learning"] else "")
                +
                ("""<th class=count>%s</th>"""%_("Unseen") if userOption["unseen"] else "")
                +
                ("""<th class=count>%s</th>"""% _("Buried") if userOption["buried"] else "")
                +
                """<th class=count></th><th></th>"""
                +
                ("""<th class=count></th><th></th>""" if userOption["no_new"] else "")
                +
                ("""<th class=count>%s</th></tr>""" %_("Option group")) if userOption["unseen"] else "")


def initialize_local(col,id_to_name=None):
    if id_to_name is None:
        _, id_to_name= initialize_name__id(col)
    """an array such that [di]d[kind] is the number of elements of this kind in the deck whith id did"""
    query =""" select did ,count(*) as c
    from cards
    where (%s)
    group by did"""
    cond={#"due":"queue=2",
          "learning":"queue=1",
          #"new":"queue=0",
          "unseen": "queue=0",
          "buried":"queue<0"}
    local_list ={}
    for kind in kinds:
        local_list[kind]=col.db.all(query % cond[kind])
    local = {}
    for kind in kinds:
        local[kind]={}
        for id_val in local_list[kind]:
            (id,value)= id_val
            local[kind][id_to_name[str(id)]]=value or 0#value may be None
    decks = col.decks.all()
    for deck in decks:
        for kind in kinds:
            dname=deck['name']
            if dname not in local[kind]:
                local[kind][dname]=0
    return local

def initialize_name__id(col):
    """dic from name to did (as string). And reciprocally"""
    decks = col.decks.all()
    name_to_id = {}
    id_to_name ={}
    for deck in decks:
        name_to_id[deck['name']]=str(deck['id'])
        id_to_name[str(deck['id'])]=deck['name']
    return name_to_id, id_to_name

def initialize_deck_to_child(col):
    """from deck's name the deck's children's name."""
    decks = col.decks.all()
    deck_child = {}
    for deck in decks:
        deck_child[deck['name']]=[]
        
    for deck in decks:
        if "::" in deck['name']:
            parent=re.sub("::(?:[^:]|:[^:])*$","",deck['name'])
            deck_child[parent].append(deck['name'])

    return deck_child

def initialize_global(col):
    """
    Array from [kind][dname] to the number of cards of kind in deck dname
    The set of decks with a descendant without new cards (without ";" in its name"""

    local=initialize_local(col)
    deck_child = initialize_deck_to_child(col)
    glob = {}
    for kind in kinds:
        glob[kind]={}
    empty_descendant = set()
    def aux(dname,glob,empty_descendant):
        """add the correct value for glob and empty_descendant, for dname and its descendant

        did as string"""
        if (dname in glob["unseen"]):
            try:
                print "Warning: %s present in glob['unseen']"% dname
            except Exception as e:
                print "Exception: %s" %e
        if (not deck_child[dname]
            and local["unseen"][dname]==0
            and not hide_symbol in dname
        ):
            empty_descendant.add(dname)

        for child_name in deck_child[dname]:
            aux(child_name,glob,empty_descendant)
            if child_name in empty_descendant :
                empty_descendant.add(dname)
        for kind in kinds:
            glob[kind][dname] = local[kind][dname]
            for child_name in deck_child[dname]:
                glob[kind][dname]+=glob[kind][child_name]
    for deck in col.decks.all():
        if "::" not in deck['name']:
            aux(deck['name'],glob,empty_descendant)

    return glob, empty_descendant

def renderDeckTree(self, nodes, depth=0 , glob=None, empty_descendant=None, deck_to_child=None):
    """Html used for the deck tree. Colomns according to userOption"""
    col = self.mw.col
    if not glob:
        glob,empty_descendant= initialize_global(col)
    if not deck_to_child:
        deck_to_child = initialize_deck_to_child(col)
    
    if not nodes:
        return ""

    node_rows = "".join([deckRow(self,node, depth, len(nodes), glob, empty_descendant, deck_to_child) for node in nodes])
    header = TABLE_HEADER + self._topLevelDragRow() if depth == 0 else ""
    footer = self._topLevelDragRow() if depth == 0 else ""
    return header + node_rows + footer


def deckRow(self, node, depth, cnt, glob=None, empty_descendant=None,deck_to_child=None):
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
    if not glob:
        glob,empty_descendant= initialize_global(self.mw.col)
    if not deck_to_child:
        deck_to_child = initialize_deck_to_child(col)

    name, did, due, lrn, new, children = node
    if did == "1" and cnt > 1 and not children:
        # if the default deck is empty, hide it
        if not self.mw.col.db.scalar("select 1 from cards where did = 1"):
            return ""

    deck = self.mw.col.decks.get(did)
    dname = deck["name"]
    if "conf" in deck:#a classical deck
        confId = str(deck["conf"])
        conf = self.mw.col.decks.dconf[confId]
        confName=conf['name']
    else:
        confName="Filtered"
    prefix = "-"
    if self.mw.col.decks.get(did)['collapsed']:
        prefix = "+"
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
    color=default_color
    if userOption["no_new"]:
            if dname in empty_descendant:
                if glob["unseen"][dname]==0:
                    color= color_empty
                else:
                    color=color_empty_descendant
    buf += """
    <td class=decktd colspan=5>%s%s<a class="deck %s" href='open:%d'><font color='%s'>%s</font></a></td>"""% (
        indent(), collapse,  extraclass, did, color,name)

    # due counts
    if userOption["due"]:
        buf += "<td align=right>%s</td>"% (str(due) if due else "")
    if userOption["new"]:
        buf += "<td align=right>%s</td>"%(str(new) if new else "")
    for kind in kinds:
        if userOption[kind]:
            buf +="<td align=right>"
            val=glob[kind][dname]
            if val >0: 
                buf+=str(val)
            buf +="</td>"
    buf += "<td></td>"
    # options
    buf += "<td align=right class=opts>%s</td>" % self.mw.button(
        link="opts:%d"%did, name="<img valign=bottom src='qrc:/icons/gears.png'>&#9662;")
    if userOption["option"]:
        buf += "<td>%s</td>"% confName
    buf += "</tr>"
    # children
    if not self.mw.col.decks.get(did)['collapsed']:
        buf += self._renderDeckTree(children, depth+1, glob=glob, empty_descendant=empty_descendant, deck_to_child = deck_to_child)
    
    return buf
    
DeckBrowser._renderDeckTree = renderDeckTree
DeckBrowser._deckRow = deckRow
