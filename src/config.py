import os
from ConfigParser import ConfigParser
from sys import argv

directory = os.path.realpath(os.path.dirname(__file__))

parser = ConfigParser()

if len(argv) > 1:
    parser.read(argv[1])
else:
    parser.read("{}/config.ini".format(directory))

MASS = float(parser.get("physics", "MASS"))
DISTANT_MASS = float(parser.get("physics", "DISTANT_MASS"))
COLLISION_RADIUS = float(parser.get("physics", "COLLISION_RADIUS"))
SPEED = float(parser.get("physics", "SPEED"))
ELASTIC_FORCE = float(parser.get("physics", "ELASTIC_FORCE"))
BOOST_SPEED = float(parser.get("physics", "BOOST_SPEED"))
DAMPING_RATE = float(parser.get("physics", "DAMPING_RATE"))
POINTS_PER_NOTE = int(parser.get("physics", "POINTS_PER_NOTE"))
DECAY_RATE = int(parser.get("physics", "DECAY_RATE"))
ROTATION_SPEED = int(parser.get("physics", "ROTATION_SPEED"))

TRACK_NAMES = [n.strip() for n in parser.get("music", "TRACK_NAMES").split(",")]
HIGH_SCORE_TRACK = parser.get("music", "HIGH_SCORE_TRACK")

MINIM = parser.get("visual", "MINIM")
CROTCHET = parser.get("visual", "CROTCHET")
QUAVER = parser.get("visual", "QUAVER")
SEMIQUAVER = parser.get("visual", "SEMIQUAVER")
CROTCHET_GLOW_ROTATION = parser.get("visual", "CROTCHET_GLOW_ROTATION")
ENERGY_GLOW = parser.get("visual", "ENERGY_GLOW")
PLAYER_CURSOR = parser.get("visual", "PLAYER_CURSOR")
INDENT = int(parser.get("visual", "INDENT"))
BULLET = parser.get("visual", "BULLET")
PLAYER_EXPLOSION = parser.get("visual", "PLAYER_EXPLOSION")

GAP = int(parser.get("scoreboard", "GAP"))

screen_shape = tuple(map(int, parser.get("visual", "screen_shape").split(",")))
FULLSCREEN = "t" in parser.get("visual", "FULLSCREEN").lower()
DOUBLEBUF = "t" in parser.get("visual", "DOUBLEBUF").lower()

mido_backend = parser.get("interface", "mido_backend")

SPACE_FIGHTER_PLAYER_VELOCITY = float(parser.get("space_fighter", "PLAYER_VELOCITY"))

NOTES_PER_SIDE = int(parser.get("space_fighter", "NOTES_PER_SIDE"))
SHOT_SPEED = int(parser.get("space_fighter", "SHOT_SPEED"))

PLAYER_ONE_START = tuple(map(int, parser.get("space_fighter", "PLAYER_ONE_START").split(",")))
PLAYER_TWO_START = tuple(map(int, parser.get("space_fighter", "PLAYER_TWO_START").split(",")))
PLAYER_ANIMATION_SPEED = float(parser.get("space_fighter", "PLAYER_ANIMATION_SPEED"))
PLAYER_LIVES = int(parser.get("space_fighter", "player_lives"))

LIVES_OFFSET = int(parser.get("space_fighter", "LIVES_OFFSET"))

NUMBER_OF_SCORES = int(parser.get("scoreboard", "NUMBER_OF_SCORES"))

TEMPO = list(map(float, parser.get("mode", "TEMPO").split(",")))
PITCH = list(map(float, parser.get("mode", "PITCH").split(",")))
LIMITS = list(map(int, parser.get("mode", "LIMITS").split(",")))

SOUND_EFFECTS_CHANNEL = int(parser.get("sound_effects", "output_channel"))

# noinspection PyProtectedMember
banned_words = parser._sections['banned_words']
clockspeed_scoreboard = int(parser.get("clockspeed", "scoreboard"))
clockspeed_runner = int(parser.get("clockspeed", "runner"))


class ChannelMapper(object):
    def __init__(self, name):
        self.name = name
        self.input_channels = tuple(map(int, parser.get(name, "channels").split(",")))
        self.output_channel = int(parser.get(name, "output_channel"))
