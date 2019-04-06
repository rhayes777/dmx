from Queue import Queue
from os import path

import pygame

import config
import model_space_fighter
from audio import audio as pl
from control import input
from visual import visual

pygame.init()
pygame.display.init()
clock = pygame.time.Clock()

directory = path.dirname(path.realpath(__file__))

note_queue = Queue()


def message_read_listener(msg):
    if msg.type == "note_on":
        note_queue.put(msg)


model = model_space_fighter.SpaceFighterModel()

track = pl.Track("{}/../media/audio/{}".format(directory, config.TRACK_NAME), is_looping=True,
                 message_read_listener=message_read_listener, play_notes=False)


class Player(object):
    def __init__(self, number):
        self.is_started = False
        self.number = number
        self.controller = input.ArcadeController(self.button_listener, number)
        self.model_player = model_space_fighter.Player()
        self.cursor = None
        self.start_position = config.PLAYER_ONE_START if number == 0 else config.PLAYER_TWO_START
        self.model_player.position = self.start_position
        self.color = visual.Color.WHITE
        model.add_player(self.model_player)

    def __repr__(self):
        return "<{} {}>".format(self.__class__.__name__, self.number)

    def button_listener(self, button):
        if self.is_started:
            if button == "centre":
                self.model_player.velocity = (0, 0)
            elif button == "left":
                self.model_player.velocity = (-config.SPACE_FIGHTER_PLAYER_VELOCITY, 0)
            elif button == "right":
                self.model_player.velocity = (config.SPACE_FIGHTER_PLAYER_VELOCITY, 0)
            elif button == "a":
                self.model_player.fire()
        elif button != "centre":
            self.is_started = True
            self.cursor = visual.PlayerCursor()
            self.button_listener(button)

    def step(self):
        if self.is_started:
            self.cursor.draw(self.model_player.position)
            for shot in self.model_player.shots:
                visual.Note(visual.sprite_sheet.image_for_angle(shot.angle), shot.position, colour=self.color)
            visual.make_score_notice(self.model_player.score, self.start_position, 5, self.color)
        else:
            visual.make_score_notice("Player {} start".format(self.number + 1), self.start_position, 5, self.color)


players = [Player(0), Player(1)]

play = True

track.start()

if __name__ == "__main__":
    while play:

        clock.tick(24)
        model.step_forward()

        while not note_queue.empty():
            model.add_note(note_queue.get())

        input.ArcadeController.read()
        for player in players:
            player.step()

        for alien in model.aliens:
            visual.Note(visual.sprite_sheet.image_for_angle(alien.angle), alien.position)

        visual.draw()
        visual.sprite_group_notes.empty()