from logging import StreamHandler

import curses

curses.setupterm()

color_normal = curses.tigetstr('sgr0')
color_green = curses.tparm(curses.tigetstr('setaf'), curses.COLOR_GREEN)
color_blue = curses.tparm(curses.tigetstr('setaf'), curses.COLOR_BLUE)
color_red = curses.tparm(curses.tigetstr('setaf'), curses.COLOR_RED)


class ColorStreamHandler(StreamHandler):

    def _select_color(self, level):
        if level < 20:
            return color_green
        elif level < 30 and level >= 20:
            return color_normal
        else:
            return color_red

    def format(self, record):
        msg = StreamHandler.format(self, record)
        if self.stream.isatty():
            color = self._select_color(record.levelno)
            msg = '%s%s%s' % (color, msg, color_normal)
             
        return msg
