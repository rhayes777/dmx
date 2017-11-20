import json
import player
import logging
import os

logging.basicConfig()

logger = logging.getLogger(__name__)

path = os.path.realpath(__file__)
dir_path = os.path.dirname(os.path.realpath(__file__))


class Combinator(object):
    """Interprets a JSON dancemat effects configuration and applies effects corresponding to button combinations"""

    def __init__(self, filename=None, track=None):
        """

        :param filename: The json configuration file (see configurations/effects_1.json)
        :param track: The midi track

        If no arguments are passed this combinator can be used to generate a JSON template by adding combos
        """
        if filename is not None and track is not None:
            self.__current_combos = []
            with open("{}/{}".format(dir_path, filename)) as f:
                self.combos = Combinator.CurrentCombos(map(lambda d: Combo(track, d), json.loads(f.read())))
                self.button_map = {sum(map(hash, combo.buttons)): combo for combo in self.combos}
        else:
            self.combos = Combinator.CurrentCombos()

    def apply_for_buttons(self, buttons):
        """
        Sets the effects that best correspond to the set of buttons. If a specific combo is defined for the set of
        buttons that combo will be applied. Otherwise, effects for each individual buttons will be stacked.
        :param buttons: A list of buttons
        """
        buttons_hash = sum(map(hash, buttons))
        new_combos = []
        if buttons_hash in self.button_map:
            new_combos.append(self.button_map[buttons_hash])
        else:
            for button in buttons:
                if hash(button) in self.button_map:
                    new_combos.append(self.button_map[hash(button)])
        self.combos.replace(new_combos)

    def dict(self):
        return map(Combo.dict, self.combos)

    class CurrentCombos(list):
        """Modified list to track the combos currently in effect"""

        def append(self, p_object):
            """
            Append a combo and apply its effects
            :param p_object: A Combo
            """
            p_object.apply()
            super(Combinator.CurrentCombos, self).append(p_object)

        def remove(self, value):
            """
            Remove a combo and remove its effects
            :param value: A Combo
            """
            if value in self:
                value.remove()
                super(Combinator.CurrentCombos, self).remove(value)

        def replace(self, new_combos):
            """
            Replaces current combos with a new set. If any combos already in effect will be unchanged. Combos that are
            in effect but not present in new_combos will have their effects removed. Combos that are in new combos and
            not currently in effect will be applied.
            :param new_combos: A list of Combos
            """
            for combo in self:
                if combo not in new_combos:
                    self.remove(combo)
            for combo in new_combos:
                if combo not in self:
                    self.append(combo)


class Combo(object):
    """Maps a set of buttons to a set of effects"""

    def __init__(self, track=None, combo_dict=None):
        """

        :param track: The midi track
        :param combo_dict: A dictionary describing
        """
        if combo_dict is not None:
            self.buttons = set(combo_dict["buttons"])
            self.effects = map(lambda d: Effect.from_dict(track, d), combo_dict["effects"])
        else:
            self.buttons = []
            self.effects = []

    def apply(self):
        """
        Apply all of the effects listed in this combo
        """
        for effect in self.effects:
            effect.apply()

    def remove(self):
        """
        Remove all of the effects listed in this combo
        """
        for effect in self.effects:
            effect.remove()

    def dict(self):
        return {"buttons": self.buttons, "effects": map(Effect.dict, self.effects)}

    def __repr__(self):
        return str(map(Effect.__repr__, self.effects))

    def __str__(self):
        return self.__repr__()


class Effect(object):
    """An individual effect that can be applied to change the music"""

    def __init__(self, effect_dict):
        """

        :param effect_dict: A dictionary describing this effect.
        """
        self.name = effect_dict["name"]
        self.value = effect_dict["value"]

    @classmethod
    def from_dict(cls, track, effect_dict):
        """
        Factory method to create an effect class for a dictionary
        :param track: A midi track
        :param effect_dict: A dictionary describing an effect.
        """
        name = effect_dict["name"]
        if name == "pitch_bend":
            return PitchBend(track, effect_dict)
        elif name == "volume_change":
            return VolumeChange(track, effect_dict)
        elif name == "intervals":
            return Intervals(track, effect_dict)
        elif name == "instrument_type":
            return InstrumentType(track, effect_dict)
        elif name == "instrument_version":
            return InstrumentVersion(track, effect_dict)
        elif name == "tempo_shift":
            return TempoShift(track, effect_dict)

        raise AssertionError("No effect named {}".format(name))

    def apply(self):
        raise AssertionError("{}.apply not overridden".format(self.name))

    def remove(self):
        raise AssertionError("{}.default not overridden".format(self.name))

    def dict(self):
        return {"name": self.name, "value": self.value}

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return "<Effect name={} value={}>".format(self.name, self.value)


class ChannelEffect(Effect):
    """An effect that modifies one or more channels"""

    def __init__(self, track, effect_dict):
        """

        :param track: A midi track
        :param effect_dict: An effect dictionary that includes one or more channels or instrument types
        (see player.InstrumentType)
        """
        super(ChannelEffect, self).__init__(effect_dict)
        self.instrument_types = None
        self.instrument_group = None
        self.__channels = None
        self.track = track
        if "channels" in effect_dict:
            self.__channels = effect_dict["channels"]
        if "instrument_types" in effect_dict:
            self.instrument_types = effect_dict["instrument_types"]
        if "instrument_group" in effect_dict:
            self.instrument_group = effect_dict["instrument_group"]
        if all(map(lambda p: p is None, [self.__channels, self.instrument_types, self.instrument_group])):
            self.channels = self.track.channels_with_instrument_group("all")
        else:
            self.channels = []
            if self.__channels is not None:
                self.channels.extend([channel for channel in self.track.channels if channel.number in self.__channels])
            if self.instrument_types is not None:
                for instrument_type in self.instrument_types:
                    self.channels.extend(self.track.channels_with_instrument_type(instrument_type))
            if self.instrument_group is not None:
                self.channels.extend(self.track.channels_with_instrument_group(self.instrument_group))

    @property
    def dict(self):
        d = super(ChannelEffect, self).dict()
        if self.__channels is not None:
            d["channels"] = self.__channels
        if self.instrument_types is not None:
            d["instrument_types"] = self.instrument_types
        if self.instrument_group is not None:
            d["instrument_group"] = self.instrument_group
        return d


class PitchBend(ChannelEffect):
    """Bends the pitch of one or more channels"""

    def apply(self):
        for channel in self.channels:
            channel.pitch_bend(self.value)

    def remove(self):
        for channel in self.channels:
            channel.pitch_bend(player.PITCHWHEEL_DEFAULT)


class VolumeChange(ChannelEffect):
    """Changes the volume of one or more channels"""

    def apply(self):
        for channel in self.channels:
            channel.volume = self.value

    def remove(self):
        for channel in self.channels:
            channel.volume = player.VOLUME_DEFAULT


class Intervals(ChannelEffect):
    """Converts notes played through a channel into one or more relative intervals in the key"""

    def apply(self):
        for channel in self.channels:
            channel.intervals = self.value

    def remove(self):
        for channel in self.channels:
            channel.intervals = None


class InstrumentType(ChannelEffect):
    """Changes the type of instrument of one or more channels. See player.InstrumentType"""

    def __init__(self, track, effect_dict):
        super(InstrumentType, self).__init__(track, effect_dict)
        self.defaults = [channel.instrument_type for channel in self.channels]

    def apply(self):
        for channel in self.channels:
            channel.instrument_type = self.value

    def remove(self):
        for n, channel in enumerate(self.channels):
            channel.instrument_type = self.defaults[n]


class InstrumentVersion(ChannelEffect):
    """Changes the version of the instrument for one or more channels. e.g. from one piano to a different piano"""

    def __init__(self, track, effect_dict):
        super(InstrumentVersion, self).__init__(track, effect_dict)
        self.defaults = [channel.instrument_version for channel in self.channels]

    def apply(self):
        for channel in self.channels:
            channel.instrument_version = self.value

    def remove(self):
        for n, channel in enumerate(self.channels):
            channel.instrument_version = self.defaults[n]


class TrackEffect(Effect):
    """An effect that is applied to the whole track"""

    def __init__(self, track, effect_dict):
        super(TrackEffect, self).__init__(effect_dict)
        self.track = track


class TempoShift(TrackEffect):
    """Shifts the tempo of the whole track by some factor. 0.5 is half tempo and 2 double tempo"""

    def apply(self):
        self.track.tempo_shift = self.value

    def remove(self):
        self.track.tempo_shift = player.TEMPO_SHIFT_DEFAULT


if __name__ == "__main__":
    import sys

    """This code generates a template with every single buttons and double buttom combination"""

    combinator = Combinator()
    all_buttons = ['up', 'down', 'left', 'right', 'triangle', 'circle', 'square', 'x']

    for button1 in all_buttons:
        c = Combo()
        c.buttons = [button1]
        combinator.combos.append(c)
        for button2 in all_buttons:
            if button1 < button2:
                c = Combo()
                c.buttons = [button1, button2]
                combinator.combos.append(c)
    with open(sys.argv[1], 'w+') as f:
        f.write(json.dumps(combinator.dict()))
