#!/usr/bin/python
# -*- coding: utf-8 -*-
import curses

class MocurseList(object):
    SIZE = 1000

    def __init__(self, x, y, width, height):
        self.window = curses.newpad(self.SIZE, height)
        self.mods = []
        self.index = 0
        self.scroll = 0
        self.x = x
        self.y = y
        self.width = width
        self.height = height

    def add(self, mod):
        win = self.window
        self.mods.append(mod)
        win.addstr(len(self.mods) - 1, 2, "Module %s/1.0" % mod, curses.A_BOLD)
        win.chgat(len(self.mods) - 1, 2, -1, curses.A_NORMAL)

    def refresh(self):
        self.window.refresh(self.scroll, 0, self.y, self.x,
                                           self.height, self.width)
    def up(self):
        self.deselect()
        self.index -= 1
        if self.index <= 0:
            self.index = 0
        if self.index - self.scroll < 0:
            self.scroll -= 1
        self.select()
        return self.mods[self.index]

    def down(self):
        self.deselect()
        self.index += 1
        limit = len(self.mods) - 1
        if self.index >= limit:
            self.index = limit
        elif self.index >= self.height - self.y:
            self.scroll += 1
        self.select()
        return self.mods[self.index]

    def deselect(self, color=curses.A_NORMAL):
        self.window.chgat(self.index, self.x, self.width, color)

    def select(self, color=curses.A_REVERSE):
        self.window.chgat(self.index, self.x, self.width, color)
        self.refresh()

    def mod_select(self):
        self.select(color=curses.color_pair(4))

    def mod_deselect(self):
        self.deselect()

class MocurseInfo(object):
    SIZE = 1000

    def __init__(self, x, y, width, height):
        self.window = curses.newpad(self.SIZE, height)
        self.mods = []
        self.scroll = 0
        self.x = x
        self.y = y
        self.width = width
        self.height = height

    def add(self, mod):
        self.window.addstr(0, 0, "Module Information:", curses.A_BOLD)
        self.window.addstr(2, 0, "This should display information about"
                                 " module %s HAHA" % mod, curses.A_NORMAL)
        self.refresh()

    def refresh(self):
        self.window.refresh(self.scroll, 0, self.y, self.x,
                                           self.height, self.width)
    def up(self):
        self.scroll -= 1
        if self.scroll < 0:
            self.scroll = 0
        self.refresh()

    def down(self):
        limit = len(self.mods) - 1
        self.scroll += 1
        if self.scroll > self.SIZE:
            self.scroll = self.SIZE
        self.refresh()


def main():
    # Initialize curses
    stdscr = curses.initscr()
    curses.noecho()
    curses.cbreak()
    curses.curs_set(0)
    stdscr.keypad(True)
    stdscr.refresh()

    # Manage colors
    curses.start_color()
    curses.init_pair(1, curses.COLOR_RED, curses.COLOR_WHITE)
    curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_GREEN, curses.COLOR_WHITE)
    curses.init_pair(4, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(5, curses.COLOR_BLACK, curses.COLOR_BLUE)

    # Application Title
    stdscr.addstr(0, 0, "MoGui", curses.A_REVERSE)
    stdscr.chgat(0, 0, -1, curses.A_REVERSE)
    stdscr.addstr(curses.LINES - 1, 0, "Use UP and DOWN to scroll, Enter to select a module and Q to quit")
    stdscr.chgat(curses.LINES - 1, 0, -1, curses.color_pair(4))

    # Create the module list
    stdscr.addstr(1, 0, "Module list")
    stdscr.chgat(1, 0, -1, curses.color_pair(2))
    half_cols = int(curses.COLS / 2)
    half_lines = int(curses.LINES / 2)
    moduleslist = MocurseList(0, 2, half_cols - 1, half_lines - 1)
    # FIXME: For testing purpose: create 100 modules
    for mod in range(0, 99):
        moduleslist.add(mod)
    ###
    moduleslist.select()
    moduleslist.refresh()

    # Create the module choice
    stdscr.addstr(1, half_cols, "Chosen modules")
    stdscr.chgat(1, half_cols, -1, curses.color_pair(4))
    moduleschoice = MocurseList(half_cols, 2, curses.COLS - 1,
                                              half_lines - 1)
    moduleschoice.refresh()

    # Create the info box
    modulesinfos = MocurseInfo(0, half_lines, curses.COLS - 1, curses.LINES - 2)
    modulesinfos.refresh()

    stdscr.refresh()
    # Main loop
    while True:
        c = stdscr.getch()
        if c == ord('q'):
            break  # Exit the while loop
        elif c == curses.KEY_HOME:
            x = y = 0
        elif c == curses.KEY_DOWN:
            modulesinfos.add(moduleslist.down())
        elif c == curses.KEY_UP:
            modulesinfos.add(moduleslist.up())
        elif c == ord('\n'):
            moduleschoice.add("module %s" % moduleslist.index)
            moduleschoice.refresh()

    # Reset to default
    curses.nocbreak()
    stdscr.keypad(False)
    curses.echo()
    curses.endwin()

if __name__ == '__main__':
    main()
