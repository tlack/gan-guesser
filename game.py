import random
from threading import Timer

import data
import text
import util

TERM_DUPE_MEMORY = 50

class Game:
    def __init__(self):
        self.clue_delay = 15
        self.state = 'waiting'
        self.term = ''
        self.recent_terms = []
        self.bot_cb = None
        self.conversation = None

    def new(self, conversation, bot_cb):
        if self.state == 'waiting':
            self.bot_cb = bot_cb
            self.conversation = conversation
            self.term = self.get_new_term()
            self.recent_terms.append(self.term)
            if len(self.recent_terms) > TERM_DUPE_MEMORY:
                self.recent_terms = self.recent_terms[-TERM_DUPE_MEMORY:];
            self.state = 'playing'
            self.start_clues()
            return True
        else:
            return False

    def playing(self):
        if self.state == 'waiting':
            return False
        else:
            return True

    def guess(self, term, message, sender_id):
        if term.lower().strip() == self.term:
            self.state = 'waiting'
            self.send_you_won(message)
            data.leader.add_win(sender_id)
        else:
            self.send_wrong(term, message)
            data.leader.add_guess(sender_id)

    def get_new_term(self):
        while 1:
            word = random.choice(list(data.game_data.keys()))
            if word not in data.banned_words and word not in self.recent_terms:
                return word
        return ""

    def start_clues(self):
        print(f'start_clues(): term = {self.term}')
        self.clue = 0
        self.send_clue_image()
        t = Timer(self.clue_delay, self.next_clue)
        t.start()

    def next_clue(self):
        print(f'next_clue(): term = {self.term}, clue = {self.clue}')
        if self.state == 'waiting':
            return

        self.clue = self.clue + 1
        num_clues = data.num_clues(self.term)
        if self.clue >= num_clues:
            self.send_you_lost()
            self.state = 'waiting'
        else:
            self.bot_cb(self.conversation, 'group', 'text', f'Clue {self.clue+1} of {num_clues}..')
            self.send_clue_image()
            t = Timer(self.clue_delay, self.next_clue)
            t.start()

    def send_clue_image(self):
        image = data.clue_image(self.term, self.clue)
        print(f'send_clue_image()')
        self.bot_cb(self.conversation, 'group', 'image', image)

    def send_you_lost(self):
        print(f'send_you_lost(): term = {self.term}')
        slander = random.choice(text.text['lost__insult'])
        self.bot_cb(self.conversation, 'group', 'text', f'You all lost! {slander}\n\nThe term was "{self.term}"\n\nType `/new` to play again.')

    def send_you_won(self, message):
        self.bot_cb(message, 'reply', 'text', f'** YOU ARE CORRECT, SIR! **\n\nGame over.. type `/new` to play again!')

    def send_wrong(self, term, message):
        self.bot_cb(message, 'reply', 'text', f'{term} is incorrect')

