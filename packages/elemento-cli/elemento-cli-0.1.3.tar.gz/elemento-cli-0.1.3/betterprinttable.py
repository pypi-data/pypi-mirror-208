import curses
from tabulate import tabulate


def better_ncurses_table(stdscr, data):
    height = curses.LINES - 1
    width = curses.COLS - 1
    win = curses.newwin(height, width, 0, 0)
    win.keypad(True)
    win.clear()
    iny = 0
    inx = 0
    header_size_y = 3
    border_y = height - 5
    border_x = width - 5
    ylen = len(data)
    xlen = max(map(lambda row: sum(map(len, row)), data))

    curses.init_color(curses.COLOR_YELLOW,
                      int(round(255. / 255 * 1000)),
                      int(round(166. / 255 * 1000)),
                      int(round(1. / 255. * 1000)))
    curses.init_pair(1, curses.COLOR_YELLOW, curses.COLOR_BLACK)

    def scroll(window):
        # header
        window.addstr(0, 0, data[0][inx:inx + border_x])
        for jch, ch in enumerate(data[1][inx:inx + border_x]):
            if ch != '│':
                window.attron(curses.A_BOLD)
                window.addstr(1, jch, ch, curses.color_pair(1))
                window.attroff(curses.A_BOLD)
            else:
                window.addch(1, jch, ch)
        window.addstr(2, 0, data[2][inx:inx + border_x])

        for y, row in enumerate(data[header_size_y + iny:header_size_y + iny + border_y]):
            window.addstr(header_size_y + y, 0, row[inx:inx + border_x])

        window.addstr(header_size_y + border_y, 0, "Press q to exit.")

        # window.addstr(header_size_y+border_y, 0, data[-1][inx:inx+border_x])
        window.refresh()
    scroll(win)

    ###    KEY PRESS    ###
    while (True):
        ch = win.getkey()
        if ch == 'KEY_UP':
            if (iny > 0):
                iny -= 1
                scroll(win)
        elif ch == 'KEY_DOWN':
            if (iny < ylen - border_y):
                iny += 1
                scroll(win)
        elif ch == 'KEY_RIGHT':
            if (inx < xlen - border_x):
                inx += 1
                scroll(win)
        elif ch == 'KEY_LEFT':
            if (inx > 0):
                inx -= 1
                scroll(win)
        elif ch == 'q':
            break


def betterprint(obj: str):
    try:
        _data = obj.__repr__()
        width = len(_data.split("\\n")[0])
        max_ch = 1
        data = []
        while max_ch < len(_data):
            data.append(_data.replace("\\n", "")[max_ch:max_ch + width - 1])
            max_ch += width - 1
        # print(data[:-1])
        curses.wrapper(better_ncurses_table, data[:-1])
    except Exception as e:
        # print(e)
        print("\n" + obj + "\n")


if __name__ == "__main__":
    data = [[f"very important info ({row},{col})" for col in range(10)] for row in range(100)]
    headers = [f"Header {col}" for col in range(10)]
    betterprint(tabulate(data, headers=headers, tablefmt="fancy_grid"))
