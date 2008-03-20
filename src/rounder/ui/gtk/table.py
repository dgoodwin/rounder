#   Rounder - Poker for the GNOME Desktop
#
#   Copyright (C) 2006-2008 Devan Goodwin <dgoodwin@dangerouslyinc.com>
#
#   This program is free software; you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation; either version 2 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program; if not, write to the Free Software
#   Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
#   02110-1301  USA

""" The Rounder GTK Table """

import gtk
import gtk.glade

from logging import getLogger
logger = getLogger("rounder.ui.gtk.table")

from rounder.ui.gtk.util import find_file_on_path
from rounder.ui.client import Table
from rounder.currency import Currency
from rounder.event import *
from rounder.action import *

SEAT_BUTTON_INDEX = {
    'seat0-sit-button': 0,
    'seat1-sit-button': 1,
    'seat2-sit-button': 2,
    'seat3-sit-button': 3,
    'seat4-sit-button': 4,
    'seat5-sit-button': 5,
    'seat6-sit-button': 6,
    'seat7-sit-button': 7,
    'seat8-sit-button': 8,
    'seat9-sit-button': 9,
}
# Map seat numbers and other labels to their location in the main GtkFixed 
# widget:
GUI_SEAT_COORDS = {
    0: (5, 115),
    1: (70, 35),
    2: (150, 0),
    3: (240, 0),
    4: (320, 35),
    5: (400, 115),
    6: (320, 195),
    7: (240, 230),
    8: (150, 230),
    9: (70, 195),
    "board-label": (150, 115),
    "pot-label": (150, 135),
}

def colored_card(card):
    """
    Return a colored representation of the given card's suit.
    Uses red for hearts, black for spades, blue for diamonds, and green 
    for clubs.
    """
    suit_char = str(card)[1]
    color = ""
    if suit_char == "h":
        color = "red"
    elif suit_char == "s":
        color = "black"
    elif suit_char == "d":
        color = "blue"
    elif suit_char == "c":
        color = "green"
    return '<span foreground="%s">%s</span>' % (color, str(card))

class TableWindow(Table):
    """ Dialog for a poker table. """

    def __init__(self, app, client_table):
        """
        Create a new table window with a reference to the parent application
        window, as well as the client table we can use to perform actions.
        """

        logger.debug("Opening table window.")

        self.app = app
        self.client_table = client_table
        # TODO: Chicken and egg problem here, probably easy to solve:
        self.client_table.ui = self

        glade_file = 'rounder/ui/gtk/data/table.glade'
        self.glade_xml = gtk.glade.XML(find_file_on_path(glade_file))
        self.table_window = self.glade_xml.get_widget('table-window')
        table_title = "%s: %s %s" % (client_table.state.name, 
                client_table.state.limit, "Texas Hold'em")
        self.table_window.set_title(table_title)

        self.chat_textview = self.glade_xml.get_widget('chat-textview')

        self.deal_button = self.glade_xml.get_widget('deal-button')
        self.deal_button.set_sensitive(False)

        self.call_button = self.glade_xml.get_widget('call-button')
        self.raise_button = self.glade_xml.get_widget('raise-button')
        self.fold_button = self.glade_xml.get_widget('fold-button')
        # Signal handlers we reuse:
        self.__call_handler_id = None
        self.__raise_handler_id = None
        self.__fold_handler_id = None
        self.__disable_action_buttons()

        # Setup and display the player seats:
        self.fixed_table = self.glade_xml.get_widget('fixed-table')
        self.board_label = gtk.Label()
        self.board_label.set_use_markup(True)
        coords = GUI_SEAT_COORDS['board-label']
        self.fixed_table.put(self.board_label, coords[0], coords[1])
        self.pot_label = gtk.Label("Pot:")
        coords = GUI_SEAT_COORDS['pot-label']
        self.fixed_table.put(self.pot_label, coords[0], coords[1])
        
        self.gui_seats = []
        for i in range(0, 10):
            seat = GuiSeat(self, i)
            self.gui_seats.append(seat)
        # Will be a pointer to our GuiSeat:
        self.my_seat = None
        self.my_seat_num = None

        # Map usernames to seats for dealing with incoming actions:
        self.__username_to_seat = {}
        for player_state in self.client_table.state.seats:
            if player_state == None:
                continue
            self.__username_to_seat[player_state.username] = \
                    self.gui_seats[player_state.seat]

        # Signal handling:
        # TODO: Replace these all with one signal?
        signals = {
            'on_seat0_sit_button_clicked': self.handle_sit_button,
            'on_seat1_sit_button_clicked': self.handle_sit_button,
            'on_seat2_sit_button_clicked': self.handle_sit_button,
            'on_seat3_sit_button_clicked': self.handle_sit_button,
            'on_seat4_sit_button_clicked': self.handle_sit_button,
            'on_seat5_sit_button_clicked': self.handle_sit_button,
            'on_seat6_sit_button_clicked': self.handle_sit_button,
            'on_seat7_sit_button_clicked': self.handle_sit_button,
            'on_seat8_sit_button_clicked': self.handle_sit_button,
            'on_seat9_sit_button_clicked': self.handle_sit_button,
            'on_deal_button_clicked': self.handle_deal_button,
        }
        self.glade_xml.signal_autoconnect(signals)
        self.table_window.connect("delete_event", self.confirm_window_close)

        # Render the initial table state:
        self.__render_table_state(self.client_table.state)

        # Clear these when a hand ends:
        self.my_hole_cards = None

        self.table_window.show_all()

    def confirm_window_close(self, widget, event, data=None):
        logger.debug("Confirming window close.")
        # NOTE: Just closing the window here for now, confirmation comes 
        # later:
        self.client_table.leave()
        return False # set to true for confirm screen

    def handle_sit_button(self, widget):
        seat = SEAT_BUTTON_INDEX[widget.get_name()]
        logger.info("Requesting seat %s" % seat)
        self.client_table.sit(seat)

    def handle_deal_button(self, widget):
        logger.info("Requesting to start a hand.")
        self.client_table.start_game()

    def sit_success(self, seat):
        self.my_seat = self.gui_seats[seat]
        self.my_seat_num = seat
        if not self.client_table.state.hand_underway:
            self.deal_button.set_sensitive(True)
        for seat in self.gui_seats:
            seat.disable_sit_button()

    def chat_line(self, msg):
        """ Append a line to the chat area on the table. """
        buf = self.chat_textview.get_buffer()
        buf.insert(buf.get_end_iter(), msg + "\n")
        mark = buf.create_mark("end", buf.get_end_iter())
        self.chat_textview.scroll_to_mark(mark, 0.0)
    
    def __disable_action_buttons(self):
        self.call_button.set_label("Call")
        self.call_button.set_sensitive(False)

        self.raise_button.set_label("Raise")
        self.raise_button.set_sensitive(False)

        self.fold_button.set_label("Fold")
        self.fold_button.set_sensitive(False)

    def handle_call_button(self, widget, data):
        """ Handle a call button press. """

        action_index = data[0]
        action = data[1]

        self.__disable_action_buttons()

        logger.debug("Calling $%s." % action.amount)
        self.client_table.act(action_index, [])

    def handle_raise_button(self, widget, data):
        """ Handle a raise button press. """

        action_index = data[0]
        action = data[1]
        raise_amount = data[2]
        current_bet = data[3]

        self.__disable_action_buttons()

        logger.debug("Raising $%s." % raise_amount)
        self.client_table.act(action_index, [raise_amount])

    def handle_fold_button(self, widget, data):
        """ Handle a fold press. """

        action_index = data[0]
        action = data[1]

        self.__disable_action_buttons()

        logger.debug("Folding.")
        self.client_table.act(action_index, [])

    def prompt(self, actions):
        """ Prompt player to act. """
        index = 0
        logger.debug("Prompting with actions:")
        for action in actions:
            logger.debug("   %s" % action)
            if isinstance(action, PostBlind):
                self.call_button.set_label("Post blind: $%s" % action.amount)
                self.call_button.set_sensitive(True)
                if self.__call_handler_id != None:
                    self.call_button.disconnect(self.__call_handler_id)
                self.__call_handler_id = self.call_button.connect('clicked',
                        self.handle_call_button, (index, action))

            elif isinstance(action, Call):
                if action.amount == 0:
                    self.call_button.set_label("Check" % action.amount)
                else:
                    self.call_button.set_label("Call: $%s" % action.amount)
                self.call_button.set_sensitive(True)
                if self.__call_handler_id != None:
                    self.call_button.disconnect(self.__call_handler_id)
                self.__call_handler_id = self.call_button.connect('clicked', 
                        self.handle_call_button, (index, action))

            elif isinstance(action, Raise):
                # TODO: Note this is only for limit holdem currently:
                if action.current_bet == 0:
                    self.raise_button.set_label("Bet: $%s" % action.min_bet)
                else:
                    self.raise_button.set_label("Raise: $%s" % action.min_bet)
                self.raise_button.set_sensitive(True)
                if self.__raise_handler_id != None:
                    self.raise_button.disconnect(self.__raise_handler_id)
                self.__raise_handler_id = self.raise_button.connect('clicked', 
                        self.handle_raise_button, (index, action, 
                            action.min_bet, action.current_bet))

            elif isinstance(action, Fold):
                self.fold_button.set_label("Fold")
                self.fold_button.set_sensitive(True)
                if self.__fold_handler_id != None:
                    self.fold_button.disconnect(self.__fold_handler_id)
                self.__fold_handler_id = self.fold_button.connect('clicked', 
                        self.handle_fold_button, (index, action)) 

            index = index + 1

    def process_event(self, event):
        """
        Display the incoming event to the user.

        Currently the event's all contain a table state DTO object which we
        can use to display the entire table. This obviously duplicates a lot
        of data and may have to change in the future to reduce bandwidth.
        For now we can get away with just using the table state to update
        everything at the table.
        """

        # Render the generic table state first, let the event specific code
        # expand on this:
        self.__render_table_state(event.table_state)

        if isinstance(event, PlayerJoinedTable):
            self.__username_to_seat[event.username] = \
                self.gui_seats[event.seat_num]
            self.chat_line("%s took seat %s." % (event.username, 
                    event.seat_num))

        if isinstance(event, PlayerLeftTable):
            self.__username_to_seat.pop(event.username)
            self.chat_line("%s left table." % event.username) 
            self.gui_seats[event.seat_num].player_left(self.my_seat 
                    != None)

        elif isinstance(event, PlayerPrompted):
            # If our deal button is enabled this is likely the initial
            # prompt to post blinds and we can disable the button as the
            # hand will soon be underway. If the server is unable to find
            # player's willing to post blinds a HandCancelled event will
            # be sent out.
            self.deal_button.set_sensitive(False)
            seat = self.__username_to_seat[event.username]
            seat.prompted()

        elif isinstance(event, HandCancelled):
            self.chat_line("Hand cancelled.")
            self.deal_button.set_sensitive(True)

        elif isinstance(event, NewHandStarted):
            # TODO: Show who's dealing better:
            self.chat_line("New hand!")
            self.chat_line("%s is dealing." % self.gui_seats[
                event.table_state.dealer_seat].name_label.get_text())
            for seat_num in event.seats_dealt_in:
                self.gui_seats[seat_num].show_hole_cards(None)

        elif isinstance(event, PlayerPostedBlind):
            self.chat_line("%s posts blind: $%s" % (event.username,
                event.amount))
            seat = self.__username_to_seat[event.username]
            seat.posted_blind(event.amount)

        elif isinstance(event, PlayerCalled):
            if event.amount == 0:
                self.chat_line("%s checks." % (event.username))
            else:
                self.chat_line("%s calls: $%s" % (event.username,
                    event.amount))
            seat = self.__username_to_seat[event.username]
            seat.called(event.amount)

        elif isinstance(event, PlayerRaised):
            self.chat_line("%s raises: $%s" % (event.username,
                event.amount))
            seat = self.__username_to_seat[event.username]
            seat.raised(event.amount)

        elif isinstance(event, PlayerFolded):
            self.chat_line("%s folds." % event.username)
            seat = self.__username_to_seat[event.username]
            seat.folded()

        elif isinstance(event, HoleCardsDealt):
            self.chat_line("Dealt hole cards: %s %s" % (event.cards[0], 
                event.cards[1]))
            self.my_hole_cards = event.cards
            self.my_seat.show_hole_cards(self.my_hole_cards)

        elif isinstance(event, CommunityCardsDealt):
            self.chat_line("Community cards: %s" % event.cards)
            # Implicit new round of betting, clear actions from the last one.
            for seat in self.gui_seats:
                if seat.is_occupied():
                    seat.clear_action()

        elif isinstance(event, GameEnding):
            self.chat_line("End of hand.")
            for seat in self.gui_seats:
                if seat.is_occupied():
                    seat.clear_action()

        elif isinstance(event, PlayerShowedCards):
            self.chat_line("%s shows: %s" % (event.username, event.cards))
            seat = self.__username_to_seat[event.username]
            seat.show_hole_cards(event.cards)

        elif isinstance(event, GameOver):
            for tuple in event.results:
                pot_state = tuple[0]
                for pot_winner in tuple[1]:
                    pot_type = "main"
                    if not pot_state.is_main_pot:
                        pot_type = "side"
                    self.chat_line("%s wins $%s from %s pot" %
                            (pot_winner.username, pot_winner.amount, 
                                pot_type))
            self.deal_button.set_sensitive(True)


    def __render_table_state(self, state):
        """
        Renders table state every time an event is received.

        Transition this slowly to a state where this is only used when
        initially joining a table. Let individual event handlers change
        only the relevant widgets for incoming events.
        """
        logger.debug("Rendering table state:")
        state.print_state()
    
        # Render board cards:
        cards_string = ""
        for c in state.community_cards:
            cards_string = "%s %s" % (cards_string, colored_card(c))
        self.board_label.set_markup(cards_string)

        # Render pot size:
        # TODO: Rendering all side pots + pending round bets as one
        # master pot here for now:
        pots = Currency(0.00)
        for pot_state in state.pots:
            pots = pots + pot_state.amount
        pots = pots + state.round_bets
        self.pot_label.set_text("Pot: $%s" % pots)

        for i in range(0, 10):
            seat = self.gui_seats[i]

            if state.seats[i] != None:
                player_state = state.seats[i]
                if not seat.is_occupied():
                    # First time we've seen this seat occupied:
                    seat.display_player_state(player_state)
                else:
                    assert(seat.name_label.get_text() == 
                            player_state.username)
                    # Set only what we need to frequently update:
                    # TODO: get updated player chip counts from events!
                    seat.set_chips(player_state.chips)



class GuiSeat:
    """
    Tiny object to encapsulate hard coded assumptions about the widgets
    that compose a seat.
    """
    def __init__(self, parent_table, seat_number):
        self.parent_table = parent_table
        self.seat_number = seat_number
        self.__fixed = parent_table.fixed_table # GtkFixed widget
        logger.debug("Creating GuiSeat %s" % seat_number)

        # Set if we're displaying a button:
        self.sit_button = None

        # These get set when someone takes the seat:
        self.cards_label = None
        self.name_label = None
        self.chips_label = None
        self.action_label = None

        # Initially create the seat as a Sit button, will change to a player
        # the first time we render the table state, or when someone grabs
        # the seat.
        self.vbox = gtk.VBox(homogeneous=True)
        coords = GUI_SEAT_COORDS[self.seat_number]
        self.__fixed.put(self.vbox, coords[0], coords[1])
        self.display_button()
        self.vbox.show_all()

    def is_occupied(self):
        if self.sit_button == None:
            return True
        return False

    def display_button(self):

        for c in self.vbox.get_children():
            c.destroy()

        # Destroy any fields displaying player info:
        self.cards_label = None
        self.name_label = None
        self.chips_label = None
        self.action_label = None

        self.sit_button = gtk.Button(label="Sit")
        self.sit_button.set_name("seat%s-sit-button" % self.seat_number)
        self.sit_button.connect("clicked", 
                self.parent_table.handle_sit_button)
        self.vbox.pack_start(self.sit_button)

        self.vbox.show_all()

    def display_player_state(self, player_state):
        """
        Switch this seat to display actual player info.

        Called only once per player occupation. If a player leaves we 
        must switch back to Sit button mode. Otherwise we just update
        the fields we need to change.
        """

        # Throw an exception if we're already displaying player state:
        if self.name_label != None or self.sit_button == None:
            raise Exception("Don't re-call display_player_state")

        for c in self.vbox.get_children():
            c.destroy()

        self.sit_button = None

        cards = ""
        if player_state.num_cards > 0:
            cards = "XX XX"
        self.cards_label = gtk.Label(cards)
        self.cards_label.set_use_markup(True)
        #self.cards_label.set_name("seat%s-cards-label" % self.seat_number)

        self.name_label = gtk.Label()
        uname = '<span size="large">%s</span>' % player_state.username
        self.name_label.set_use_markup(True)
        self.name_label.set_markup(uname)
        #self.name_label.set_name("seat%s-player-label" % self.seat_number)

        self.chips_label = gtk.Label()
        self.chips_label.set_use_markup(True)
        self.set_chips(player_state.chips)

        self.action_label = gtk.Label()
        self.action_label.set_use_markup(True)
        self.__set_action("")

        self.vbox.pack_start(self.cards_label)
        self.vbox.pack_start(self.name_label)
        self.vbox.pack_start(self.chips_label)
        self.vbox.pack_start(self.action_label)

        self.vbox.show_all()

    def set_chips(self, chips):
        logger.debug("updating chips")
        chips = '<span size="small">$%s</span>' % chips
        self.chips_label.set_markup(chips)

    def player_left(self, i_am_seated=True):
        """
        Player left the table, render their spot as a sit button again.
        """
        self.display_button()
        if i_am_seated:
            self.disable_sit_button()

    def disable_sit_button(self):
        """
        Disable our Sit button if we're displaying one.
        """
        if self.sit_button != None:
            self.sit_button.set_sensitive(False)

    def show_hole_cards(self, cards):
        """
        Display hole cards.

        Called when we receive our hole cards, or someone else shows theirs.
        If the hole cards are unknown (i.e. indicating player is in hand only),
        cards will be None.
        """
        if cards == None:
            self.cards_label.set_text("XX XX")
        else:
            self.cards_label.set_markup("%s %s" % (colored_card(cards[0]), 
                colored_card(cards[1])))

    def clear_hole_cards(self):
        self.cards_label.set_text("")

    def __set_action(self, txt):
        text = '<span size="small">%s</span>' % txt
        self.action_label.set_markup(text)

    def clear_action(self):
        """ Clear the action column. """
        self.__set_action("")

    def prompted(self):
        """ Indicate in the UI that this seat has been prompted to act. """
        self.action_label.set_text("><")

    def posted_blind(self, amount):
        """ Indicate that this player has posted a blind. """
        self.__set_action("posts")

    def folded(self):
        """ Indicate that this player has folded. """
        self.__set_action("fold")

    def called(self, amount):
        """ Indicate that this player has called. """
        if amount == 0:
            self.__set_action("check")
        else:
            self.__set_action("call")

    def raised(self, amount):
        """ Indicate that this player has raised. """
        self.__set_action("raise $%s" % amount)



