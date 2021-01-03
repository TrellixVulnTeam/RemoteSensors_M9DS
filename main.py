"""
Retrieve Raspberry pi information over SSH
"""

from SSH import *
import utils
import time
import curses


def finalize(stdscr):
    curses.nocbreak()
    stdscr.keypad(0)
    curses.echo()
    curses.endwin()
    conn.finalize_conn()


def print_menu(stdscr, cols, rows):

    stdscr.addstr(rows - 1, 2, " Exit (q) ")
    stdscr.addstr(rows - 1, 17, " Update disks (d) ")
    stdscr.addstr(rows - 1, 40, " Update status (s) ")


def main(stdscr):
    stdscr.refresh()
    curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_YELLOW, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_RED, curses.COLOR_BLACK)

    stdscr.nodelay(1)
    stdscr.timeout(0)

    bar = "█"  # an extended ASCII 'fill' character
    try:

        curses.curs_set(0)
        stdscr.keypad(1)

        stdscr.clear()
        stdscr.border()

        kernel = conn.get_kernel_info(True)
        disk = conn.get_disk_usage()

        while not utils.FINALIZE:

            # Get screen dimensions
            rows, cols = stdscr.getmaxyx()

            if utils.UPDATE_DISK_INFO:
                disk = conn.get_disk_usage()
                utils.UPDATE_DISK_INFO = False

            # Show IP we are connected to
            stdscr.addstr(1, 2, "Connected to " + conn.HOST)

            # Show kernel version
            stdscr.addstr(1, cols - (len(str(kernel)) + 10), "Kernel: " + str(kernel))

            # Show disk usage (updatable with 'd' key)
            contline = 1
            for line in disk.split("\n"):
                if line == "":
                    break

                aux = line.split("\t")
                stdscr.addstr(3 + contline, 3, aux[0])
                stdscr.addstr(3 + contline, 15, aux[1])
                stdscr.addstr(3 + contline, 25, aux[2])
                stdscr.addstr(3 + contline, 35, aux[3])
                stdscr.addstr(3 + contline, 45, aux[4])

                contline += 1

            # Show GPU and CPU temperatures in bar mode (max temp is 70ºC)
            temp = float(conn.get_GPU_temp())

            if temp < 55:
                colorindex = 1
            elif temp < 65:
                colorindex = 2
            else:
                colorindex = 3
            value = (temp * utils.MAX_BAR_COLS) / utils.MAX_TEMP
            text = bar * int(value)
            stdscr.addstr(10, 3, "GPU Temp:")
            stdscr.addstr(10, 14, text.ljust(utils.MAX_BAR_COLS, " "), curses.color_pair(colorindex))
            stdscr.addstr(10, 14 + utils.MAX_BAR_COLS + 2, str(temp) + " ºC")

            temp = float(conn.get_CPU_temp())
            if temp < 55:
                colorindex = 1
            elif temp < 65:
                colorindex = 2
            else:
                colorindex = 3
            value = (temp * utils.MAX_BAR_COLS) / 70
            text = bar * int(value)
            stdscr.addstr(11, 3, "CPU Temp:")
            stdscr.addstr(11, 14, text.ljust(utils.MAX_BAR_COLS, " "), curses.color_pair(colorindex))
            stdscr.addstr(11, 14 + utils.MAX_BAR_COLS + 2, str(temp) + " ºC")

            # Display CPU usage (all cores) and RAM usage
            usage = conn.get_CPU_use()
            stdscr.addstr(13, 3, "CPU usage: " + str(usage) + " %")

            ram = conn.get_RAM_usage()
            stdscr.addstr(14, 3, "RAM usage: " + str(ram))

            # Display processes information (running and total)
            stdscr.addstr(13, 28, "Processes")

            average = conn.get_avg_load()
            processes = int(average[3].split("/")[0]) - 1
            stdscr.addstr(13, 40, "Active: ")
            stdscr.addstr(13, 50, str(processes))

            total_proc = int(average[3].split("/")[1]) - 1
            stdscr.addstr(14, 40, "Total: ")
            stdscr.addstr(14, 50, str(total_proc))

            # Display average load on 1, 5 and 5 minutes
            stdscr.addstr(13, 60, "Average load")
            stdscr.addstr(13, 75, "1 min")
            stdscr.addstr(13, 85, "5 min")
            stdscr.addstr(13, 95, "15 min")

            stdscr.addstr(14, 75, average[0])
            stdscr.addstr(14, 85, average[1])
            stdscr.addstr(14, 95, average[2])

            # Display CPU freq
            freq = conn.get_CPU_freq()
            stdscr.addstr(16, 3, "CPU freq: " + freq)
            stdscr.addstr(16, 18, "Mhz")

            # Display throttling info and status (undervoltage, temp throttling, etc) updatable with 's' key
            stdscr.addstr(3, cols - 50, "Throttling status")
            stdscr.addstr(4, cols - 60, "Current")
            stdscr.addstr(4, cols - 30, "Since last boot")
            status = conn.get_status()
            contcurrent = 0
            contboot = 0
            contbit = 0
            for bit in status:
                if bit == "1":
                    if contbit == 0:
                        stdscr.addstr(5 + contcurrent, cols - 60, "Under voltage", curses.color_pair(3))
                        contcurrent += 1
                    elif contbit == 1:
                        stdscr.addstr(5 + contcurrent, cols - 60, "Arm frequency capping", curses.color_pair(3))
                        contcurrent += 1
                    elif contbit == 2:
                        stdscr.addstr(5 + contcurrent, cols - 60, "Throttling", curses.color_pair(3))
                        contcurrent += 1
                    elif contbit == 3:
                        stdscr.addstr(5 + contcurrent, cols - 60, "Soft temperature limit", curses.color_pair(3))
                        contcurrent += 1
                    elif contbit == 16:
                        stdscr.addstr(5 + contboot, cols - 30, "Under voltage", curses.color_pair(2))
                        contboot += 1
                    elif contbit == 17:
                        stdscr.addstr(5 + contboot, cols - 30, "Arm frequency capped", curses.color_pair(2))
                        contboot += 1
                    elif contbit == 18:
                        stdscr.addstr(5 + contboot, cols - 30, "Throttled", curses.color_pair(2))
                        contboot += 1
                    elif contbit == 19:
                        stdscr.addstr(5 + contboot, cols - 30, "Soft temperature limit", curses.color_pair(2))
                        contboot += 1
                contbit += 1

            # Print options menu
            stdscr.addstr(rows - 2, 2, "Refresh rate: " + str(utils.REFRESH.__round__(2)) + " s")
            stdscr.addstr(rows - 2, 30, "Human units: " + str(utils.HUMAN_DISK_INFO))

            # Display screen size in (rows X cols)
            text = "Size: " + str(rows) + "x" + str(cols)
            stdscr.addstr(rows - 2, cols - len(text) - 1, text)
            print_menu(stdscr, cols, rows)
            stdscr.refresh()

            key = stdscr.getch()

            if key == curses.KEY_RESIZE:
                stdscr.clear()
                stdscr.border()
            elif key == ord('q'):
                utils.FINALIZE = True
            elif key == ord('d'):
                utils.UPDATE_DISK_INFO = True
            elif key == ord('h'):
                utils.HUMAN_DISK_INFO = not utils.HUMAN_DISK_INFO
                utils.UPDATE_DISK_INFO = True
            elif key == ord('+'):
                utils.REFRESH += 0.1
            elif key == ord('-'):
                utils.REFRESH -= 0.1
                if utils.REFRESH <= 0:
                    utils.REFRESH = 0.1

            time.sleep(utils.REFRESH)

        finalize(stdscr)
    except Exception as ex:
        finalize(stdscr)
        print()
        print(ex)


if __name__ == '__main__':
    import sys
    if len(sys.argv) != 4:
        print("Incorrect arguments number")
        print()
        print("Usage: RemoteSensors.sh <destination IP> <user> <password>")
        exit(-1)

    print()

    conn = SSH(sys.argv[1], sys.argv[2], sys.argv[3])
    curses.wrapper(main)


