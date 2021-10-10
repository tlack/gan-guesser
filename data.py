import glob
import json
from os import path
import string
from threading import Timer

import text
import util

LEADERBOARD_FILE = 'leaderboard-byname.json'
SAVE_DELAY = 60 
SOURCE_DIR = 'game_data/terms'
game_data = {}
leaderboard = {}

for filename in glob.glob(path.join(SOURCE_DIR, "*png")):
    filename = path.basename(filename)
    p = filename.split("-")
    term = p[0].lower().strip()
    game_data[term] = game_data.get(term, []) + [filename]


def clue_image(term, num):
    fn = game_data[term][num]
    d = util.read_bytes(path.join(SOURCE_DIR, fn))
    return d

def num_clues(term):
    return len(game_data[term])

def num_insults():
    return len(text.text['lost__insult'])

def num_terms():
    return len(game_data.keys())

class Leaderboard:
    blank = {'guesses': 0, 'wins': 0}

    def __init__(self):
        if path.exists(LEADERBOARD_FILE):
            self.by_name = json.loads(util.read_file(LEADERBOARD_FILE))
        else:
            self.by_name = {}
        self.dirty = False
        self.schedule_save()

    def schedule_save(self):
        t = Timer(SAVE_DELAY, self.save_if_dirty)
        t.start()

    def add_guess(self, sender):
        info = self.by_name.get(sender, self.blank.copy())
        info['guesses'] = info['guesses'] + 1
        self.by_name[sender] = info
        self.dirty = True

    def add_win(self, sender):
        info = self.by_name.get(sender, self.blank.copy())
        info['wins'] = info['wins'] + 1
        self.by_name[sender] = info
        self.dirty = True

    def save_if_dirty(self):
        if self.dirty:
            print('saving leaderboard to', LEADERBOARD_FILE)
            out = json.dumps(self.by_name)
            f = open(LEADERBOARD_FILE, 'w')
            f.write(out)
            f.close()
            self.dirty = False
        self.schedule_save()

    def summary(self):
        summary = []
        for name, info in self.by_name.items():
            if info['guesses'] == 0:
                score = 0
            else:
                score = info['wins'] / info['guesses']
            record = {'name': name, 'wins': info['wins'], 'guesses': info['guesses'], 'score': score}
            summary.append(record)
        summary.sort(key=lambda x: x['score'], reverse=True)
        return summary

leader = Leaderboard()

