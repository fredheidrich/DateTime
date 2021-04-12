"""

License: public domain
Author: Fred Heidrich 07/04/2021

IDEAS
- nudge time up or down
- time zones
- some kind of verification test
- strings into source code? auto-detect scope context

"""

import datetime

import sublime
import sublime_plugin


__version__ = "0.1dev130421"
VERSION = __version__
SETTINGS = {}


def plugin_loaded():
    global SETTINGS
    SETTINGS = sublime.load_settings("Now.sublime-settings")


class NowCommand(sublime_plugin.TextCommand):

    CLASS_WORD_START = 1
    CLASS_WORD_END = 2
    CLASS_PUNCTUATION_START = 4
    CLASS_PUNCTUATION_END = 8
    CLASS_SUB_WORD_START = 16
    CLASS_SUB_WORD_END = 32
    CLASS_LINE_START = 64
    CLASS_LINE_END = 128
    CLASS_EMPTY_LINE = 256
    CLASS_MIDDLE_WORD = 512
    CLASS_WORD_START_WITH_PUNCTUATION = 1024
    CLASS_WORD_END_WITH_PUNCTUATION = 2048
    CLASS_OPENING_PARENTHESIS = 4096
    CLASS_CLOSING_PARENTHESIS = 8192

    DEFAULT_FORMATS = {
        "date_format": "%d/%m/%y",
        "date_time_format": "%d/%m/%y %H:%M",
        "time_format": "%H:%M",
    }

    def run(self, edit, part="date"):

        locale = SETTINGS.get("locale")
        if not locale:
            # todo/fred: diagnose
            sublime.status_message("Error/DateTime: Unable to load locale '{}'".format(locale))
            return
        locales = SETTINGS.get("locales")
        locale_formats = locales.get(locale)

        fmt = locale_formats.get(part + "_format")
        
        # note/fred: defaults
        if not fmt:
            sublime.status_message("Warning/DateTime: " + part + " not recognised: using default format")
            fmt = NowCommand.DEFAULT_FORMATS.get(
                part + "_format", NowCommand.DEFAULT_FORMATS["date_time_format"])

        regions = [r for r in self.view.sel()]
        regions.reverse()

        text = datetime.datetime.now().strftime(fmt)
        # todo/fred: invert this? it's a bit buggy
        start_mask = (
            NowCommand.CLASS_WORD_END |
            NowCommand.CLASS_PUNCTUATION_END |
            NowCommand.CLASS_SUB_WORD_END |
            NowCommand.CLASS_MIDDLE_WORD |
            NowCommand.CLASS_WORD_END_WITH_PUNCTUATION |
            NowCommand.CLASS_CLOSING_PARENTHESIS
        )
        for s in regions:

            if s.empty() and (self.view.classify(s.begin()) & start_mask):
                text = " " + text

            num = self.view.insert(edit, s.begin(), text)
            self.view.erase(edit, sublime.Region(s.begin() + num, s.end() + num))
