import midi_player
import dancemat
from time import sleep
import pygame
import signal
import display

# Set up pygame
pygame.init()
pygame.display.init()
# create screen for pygame to draw to
screen = pygame.display.set_mode((1000, 700))
clock = pygame.time.Clock()

mat = dancemat.DanceMat(pygame)
track = midi_player.Song(filename='bicycle-ride.mid', is_looping=True)

play = True

disp = display.Display(pygame, screen)


def stop(*args):
    global play
    track.stop()
    play = False


signal.signal(signal.SIGINT, stop)

channels = track.channels

for channel in channels:
    channel.message_send_listener = disp.on_message_received

chord_channel = channels[0]
drum_channel = channels[8]

bass_channel = midi_player.BassChannel(2, chord_channel, drum_channel)
channels[2] = bass_channel

# Relate button names to positions in the scale
position_dict = {dancemat.Button.triangle: 0,
                 dancemat.Button.down: 1,
                 dancemat.Button.square: 2,
                 dancemat.Button.left: 3,
                 dancemat.Button.right: 4,
                 dancemat.Button.x: 5,
                 dancemat.Button.up: 6,
                 dancemat.Button.circle: 7}

channel_numbers_with_fifth = set()

playing_channels = [0, 1, 2, 3]


def toggle_channel(channel):
    print "Toggle {}".format(channel)
    if channel in playing_channels:
        playing_channels.remove(channel)
    else:
        playing_channels.append(channel)


# Function to listen for changes to button state
def listener(status_dict):
    if status_dict[dancemat.Button.triangle]:
        toggle_channel(0)
    if status_dict[dancemat.Button.down]:
        toggle_channel(1)
    if status_dict[dancemat.Button.square]:
        toggle_channel(2)
    if status_dict[dancemat.Button.circle]:
        toggle_channel(3)
    track.set_included_channels(playing_channels)

    def check_fifth(button_name, channel_number):
        if status_dict[button_name] and channel_number not in channel_numbers_with_fifth:
            channels[channel_number].add_effect(midi_player.fifth)
            channel_numbers_with_fifth.add(channel_number)
        elif channel_number in channel_numbers_with_fifth:
            channels[channel_number].remove_effect(midi_player.fifth)
            channel_numbers_with_fifth.remove(channel_number)

    check_fifth(dancemat.Button.left, 0)
    check_fifth(dancemat.Button.right, 1)
    check_fifth(dancemat.Button.up, 2)
    check_fifth(dancemat.Button.down, 3)

    if status_dict[dancemat.Button.select]:
        track.send_command(midi_player.Command.tempo_change, value=0.5)
    elif status_dict[dancemat.Button.start]:
        track.send_command(midi_player.Command.tempo_change, value=2)
    else:
        track.send_command(midi_player.Command.tempo_change, value=1)


# Attach that listener function to the dancemat
mat.set_button_listener(listener)

track.start()

# Keep reading forever
while play:
    mat.read()
    sleep(0.05)
