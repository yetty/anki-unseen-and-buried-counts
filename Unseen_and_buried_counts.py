# -*- coding: utf-8 -*-
# Copyright: Juda Kaleta <juda.kaleta@gmail.com>
# License: GNU GPL, version 3 or later; http://www.gnu.org/copyleft/gpl.html
#

from aqt.deckbrowser import DeckBrowser

TABLE_HEADER = """
<tr><th colspan=5 align=left>%s</th><th class=count>%s</th>
<th class=count>%s</th><th class=count>%s</th><th class=count>%s</th><th class=count></th></tr>""" % (
        _("Deck"), _("Due"), _("New"), _("Unseen"), _("Buried"))


def renderDeckTree(self, nodes, depth=0):
    if not nodes:
        return ""

    node_rows = "".join([self._deckRow(node, depth, len(nodes)) for node in nodes])
    header = TABLE_HEADER + self._topLevelDragRow() if depth == 0 else ""
    footer = self._topLevelDragRow() if depth == 0 else ""
    return header + node_rows + footer


def deckRow(self, node, depth, cnt):
    name, did, due, lrn, new, children = node
    deck = self.mw.col.decks.get(did)
    unseen = self.mw.col.db.scalar("select count(*) from cards where did = %i and queue=0" % did)
    buried = self.mw.col.db.scalar("select count(*) from cards where did = %i and queue<0" % did)
    
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
        if cnt >= 1000:
            cnt = "1000+"
        return "<font color='%s'>%s</font>" % (colour, cnt)
    buf += "<td align=right>%s</td><td align=right>%s</td><td align=right>%s</td><td align=right>%s</td>" % (
        nonzeroColour(due, "#007700"),
        nonzeroColour(new, "#000099"),
        nonzeroColour(unseen, "#550000"),
        nonzeroColour(buried, "#555500"))
    # options
    buf += "<td align=right class=opts>%s</td></tr>" % self.mw.button(
        link="opts:%d"%did, name="<img valign=bottom src='qrc:/icons/gears.png'>&#9662;")
    # children
    buf += self._renderDeckTree(children, depth+1)
    return buf
    
DeckBrowser._renderDeckTree = renderDeckTree
DeckBrowser._deckRow = deckRow