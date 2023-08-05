"""Firepup650's PYPI Package"""
import os, sys, termios, tty, time, sqlite3, ast
import random as r
import fkeycapture as fkey
from warnings import warn as ww
from typing import TypeVar, Type, Optional, List, Any
from collections.abc import Iterable


def clear(ascii: bool = False) -> None:
    """# Function: clear
      Clears the screen
    # Inputs:
      ascii: bool - Controls whether or not we clear with ascii, defaults to False

    # Returns:
      None

    # Raises:
      None"""
    if not ascii:
        os.system("clear")
    else:
        print("\033[H", end="", flush=True)


def cmd(command: str) -> int:
    """# Function: cmd
      Runs bash commands
    # Inputs:
      command: str - The command to run

    # Returns:
      int - Status code returned by the command

    # Raises:
      None"""
    status = os.system(command)
    return status


def randint(low: int = 0, high: int = 10) -> int:
    """# Funcion: randint
      A safe randint function
    # Inputs:
      low: int - The bottom number, defaults to 0
      high: int - The top number, defaults to 10

    # Returns:
      int - A number between high and low

    # Raises:
      None"""
    try:
        out = r.randint(low, high)
    except:
        out = r.randint(high, low)
    return out


def e(code: any = 0) -> None:
    """# Function: e
      Exits with the provided code
    # Inputs:
      code: any - The status code to exit with, defaults to 0

    # Returns:
      None

    # Raises:
      None"""
    sys.exit(code)


def gp(
    keycount: int = 1, chars: list = ["1", "2"], bytes: bool = False
) -> str or bytes:
    """# Function: gp
      Get keys and print them.
    # Inputs:
      keycount: int - Number of keys to get, defaults to 1
      chars: list - List of keys to accept, defaults to ["1", "2"]
      bytes: bool - Wether to return the kyes as bytes, defaults to False

    # Returns:
      str or bytes - Keys pressed

    # Raises:
      None"""
    got = 0
    keys = ""
    while got < keycount:
        key = fkey.getchars(1, chars)
        keys = f"{keys}{key}"
        print(key, end="", flush=True)
        got += 1
    print()
    if not bytes:
        return keys
    else:
        return keys.encode()


def gh(
    keycount: int = 1, chars: list = ["1", "2"], char: str = "*", bytes: bool = False
) -> str or bytes:
    """# Function: gh
      Get keys and print `char` in their place.
    # Inputs:
      keycount: int - Number of keys to get, defaults to 1
      chars: list - List of keys to accept, defaults to ["1", "2"]
      char: str - Character to use to obfuscate the keys, defaults to *
      bytes: bool - Wether to return the kyes as bytes, defaults to False

    # Returns:
      str or bytes - Keys pressed

    # Raises:
      None"""
    got = 0
    keys = ""
    while got < keycount:
        key = fkey.getchars(1, chars)
        keys = f"{keys}{key}"
        print("*", end="", flush=True)
        got += 1
    print()
    if not bytes:
        return keys
    else:
        return keys.encode()


def printt(text: str, delay: float = 0.1, newline: bool = True) -> None:
    """# Function: printt
      Print out animated text!
    # Inputs:
      text: str - Text to print (could technicaly be a list)
      delay: float - How long to delay between characters, defaults to 0.1
      newline: bool - Wether or not to add a newline at the end of the text, defaults to True

    # Returns:
      None

    # Raises:
      None"""
    # Store the current terminal settings
    original_terminal_settings = termios.tcgetattr(sys.stdin)
    # Change terminal settings to prevent any interruptions
    tty.setcbreak(sys.stdin)
    for char in text:
        print(char, end="", flush=True)
        time.sleep(delay)
    if newline:
        print()
    # Restore the original terminal settings
    termios.tcsetattr(sys.stdin, termios.TCSADRAIN, original_terminal_settings)


def sleep(seconds: float = 0.5) -> None:
    """# Function: sleep
      Calls `time.sleep(seconds)`
    # Inputs:
      seconds: float - How long to sleep for (in seconds), defaults to 0.5

    # Returns:
      None

    # Raises:
      None"""
    time.sleep(seconds)


def rseed(seed: any = None, version: int = 2) -> None:
    """# Function: rseed
      reseed the random number generator
    # Inputs:
      seed: any - The seed, defaults to None
      version: int - Version of the seed (1 or 2), defaults to 2

    # Returns:
      None

    # Raises:
      None"""
    r.seed(seed, version)


setattr(Iterable, "__class_getitem__", lambda x: None)
T = TypeVar("T")


def robj(iterable: Iterable[T]) -> T:
    """# Function: robj
      Returns a random object from the provided iterable
    # Input:
      iterable: Iterable[T] - Any valid Iterable

    # Returns:
      T - A random object of type `T` from the provided iterable

    # Raises:
      None"""
    return r.choice(iterable)


def Color(r: int = 0, g: int = 0, b: int = 0, bcolor: bool = False) -> None or str:
    """# Function: Color
      Set the text to a specific color.
    # Inputs:
      r: int - The red value, range of 0-255, defaults to 0
      g: int - The green value, range of 0-255, defaults to 0
      b: int - The blue value, range of 0-255, defaults to 0
      bcolor: bool - Wether to return the color as a str, defaults to False

    # Returns:
      None or str - The color code if `bcolor` is True. Otherwise, returns nothing

    # Raises:
      None"""
    if r < 0:
        r = 0
    if r > 255:
        r = 255
    if g < 0:
        g = 0
    if g > 255:
        g = 255
    if b < 0:
        b = 0
    if b > 255:
        b = 255
    if bcolor == True:
        return f"\033[38;2;{r};{g};{b}m"
    else:
        print("\003[0m")
        print(f"\033[38;2;{r};{g};{b}m")


class bcolors:
    """
    This class contains various pre-defined color codes.
    """

    INVERSE = "\033[8m"

    def fINVERSE() -> None:
        """INVERTs foreground and background colors"""
        print("\033[8m", end="")

    RESET = "\033[0m"
    RWHITE = f"\033[0m{Color(255,255,255,bcolor=True)}"
    WHITE = f"{Color(255,255,255,bcolor=True)}"
    FAILINVERSE = f"{Color(255,bcolor=True)}\033[49m\033[7m"

    def fWHITE() -> None:
        """Sets the text color to WHITE"""
        print(f"{Color(255,255,255,bcolor=True)}", end="")

    def fRWHITE() -> None:
        """RESETs the text color, then sets it to WHITE"""
        print(f"\033[0m{Color(255,255,255,bcolor=True)}", end="")

    def fFAILINVERSE() -> None:
        """Sets the text color RED, then inverses it."""
        print(f"{Color(255,bcolor=True)}\033[49m\033[7m", end="")

    def fRESET() -> None:
        """RESETs the formatting"""
        print("\033[0m", end="")

    BROWN = f"{Color(205,127,50,bcolor=True)}"

    def fBROWN() -> None:
        """Sets the text color to BROWN"""
        print(f"{Color(205,127,50,bcolor=True)}", end="")

    WARNING = f"{Color(236,232,26,bcolor=True)}"

    def fWARNING() -> None:
        """Sets the text color to YELLOW"""
        print(f"{Color(236,232,26,bcolor=True)}", end="")

    FAIL = f"{Color(255,bcolor=True)}"

    def fFAIL() -> None:
        """Sets the text color to RED"""
        print(f"{Color(255,bcolor=True)}", end="")

    OK = f"{Color(g=255,bcolor=True)}"

    def fOK() -> None:
        """Sets the text color to GREEN"""
        print(f"{Color(g=255,bcolor=True)}", end="")

    CYAN = f"{Color(g=255,b=255,bcolor=True)}"

    def fCYAN() -> None:
        """Sets the text color to CYAN"""
        print(f"{Color(g=255,b=255,bcolor=True)}", end="")

    WOOD = f"{Color(120,81,45,bcolor=True)}\033[46m\033[7m"

    def fWOOD() -> None:
        """Sets the text color to CYAN, and the background to a WOODen color"""
        print(f"{Color(120,81,45,bcolor=True)}\033[46m\033[7m", end="")

    REPLIT = f"{Color(161, 138, 26, True)}"

    def fREPLIT() -> None:
        """Sets the text color to 161,138,26 in RGB"""
        print(f"{Color(162, 138, 26, True)}")

    GREEN = OK
    fGREEN = fOK
    YELLOW = WARNING
    fYELLOW = fWARNING
    RED = FAIL
    fRED = fFAIL

    class bold:
        """
        Contains bold versions of the other color codes
        """

        BROWN = f"\033[1m{Color(205,127,50,bcolor=True)}"

        def fBROWN() -> None:
            """Sets the text color to BROWN"""
            print(f"\033[1m{Color(205,127,50,bcolor=True)}", end="")

        WARNING = f"\033[1m{Color(236,232,26,bcolor=True)}"

        def fWARNING() -> None:
            """Sets the text color to YELLOW"""
            print(f"\033[1m{Color(236,232,26,bcolor=True)}", end="")

        FAIL = f"\033[1m{Color(255,bcolor=True)}"

        def fFAIL() -> None:
            """Sets the text color to RED"""
            print(f"\033[1m{Color(255,bcolor=True)}", end="")

        OK = f"\033[1m{Color(g=255,bcolor=True)}"

        def fOK() -> None:
            """Sets the text color to GREEN"""
            print(f"\033[1m{Color(g=255,bcolor=True)}", end="")

        CYAN = f"\033[1m{Color(g=255,b=255,bcolor=True)}"

        def fCYAN() -> None:
            """Sets the text color to CYAN"""
            print(f"\033[1m{Color(g=255,b=255,bcolor=True)}", end="")

        WOOD = f"\033[1m{Color(120,81,45,bcolor=True)}\033[46m\033[7m"

        def fWOOD() -> None:
            """Sets the text color to CYAN, and the background to a WOODen color"""
            print(f"\033[1m{Color(120,81,45,bcolor=True)}\033[46m\033[7m", end="")

        WHITE = f"\033[1m{Color(255,255,255,bcolor=True)}"

        def fWHITE() -> None:
            """Sets the text color to WHITE"""
            print(f"\033[1m{Color(255,255,255,bcolor=True)}", end="")

        RWHITE = f"\033[0m\033[1m{Color(255,255,255,bcolor=True)}"

        def fRWHITE() -> None:
            """RESETs the text color, then sets it to WHITE"""
            print(f"\033[0m\033[1m{Color(255,255,255,bcolor=True)}", end="")

        REPLIT = f"\033[1m{Color(161, 138, 26, True)}"

        def fREPLIT() -> None:
            """Sets the text color to 161,138,26 in RGB"""
            print(f"\033[1m{Color(162, 138, 26, True)}")

        GREEN = OK
        fGREEN = fOK
        YELLOW = WARNING
        fYELLOW = fWARNING
        RED = FAIL
        fRED = fFAIL


replit_cursor = f"{bcolors.REPLIT}{bcolors.RESET}"

Oinput = input
cast = TypeVar("cast")


def input(prompt: str = "", cast: Type = str, bad_cast_message: str = "") -> cast:
    """# Function: input
      Displays your `prompt`, supports casting by default, with handling!
    # Inputs:
      prompt: str - The prompt, defaults to ""
      cast: Type - The Type to cast the input to, defaults to str
      bad_cast_message: str - The message to dispaly upon reciving input that can't be casted to `cast`, can be set to "No message" to not have one, defaults to f"That is not a vaild {cast.__name__}, please try again."

    # Returns:
      cast - The user's input, casted to `cast`

    # Raises:
      None"""
    if not bad_cast_message:
        bad_cast_message = f"That is not a vaild {cast.__name__}, please try again."
    ret = ""
    while ret == "":
        try:
            ret = cast(Oinput(prompt))
            break
        except ValueError:
            if bad_cast_message != "No Message":
                print(bad_cast_message)
    return ret


def replit_input(
    prompt: str = "", cast: Type = str, bad_cast_message: str = ""
) -> cast:
    """# Function: replit_input
      Displays your `prompt` with the replit cursor on the next line, supports casting by default, with handling!
    # Inputs:
      prompt: str - The prompt, defaults to ""
      cast: Type - The Type to cast the input to, defaults to str
      bad_cast_message: str - The message to dispaly upon reciving input that can't be casted to `cast`, can be set to "No message" to not have one, defaults to f"That is not a vaild {cast.__name__}, please try again."

    # Returns:
      cast - The user's input, casted to `cast`

    # Raises:
      None"""
    if prompt:
        print(prompt)
    return input(f"{replit_cursor} ", cast, bad_cast_message)


def cprint(text: str = "") -> None:
    """# Function: cprint
      Displays your `text` in a random color (from bcolors).
    # Inputs:
      text: str - The text to color, defaults to ""

    # Returns:
      None

    # Raises:
      None"""
    colordict = {
        "GREEN": bcolors.GREEN,
        "RED": bcolors.RED,
        "YELLOW": bcolors.YELLOW,
        "CYAN": bcolors.CYAN,
        "REPLIT": bcolors.REPLIT,
        "BROWN": bcolors.BROWN,
        "WHITE": bcolors.WHITE,
    }
    colornames = ["GREEN", "RED", "YELLOW", "CYAN", "REPLIT", "BROWN", "WHITE"]
    color = colordict[robj(colornames)]
    print(f"{color}{text}")


def flush_print(text: str = ""):
    """# Function: flush_print
      Prints and flushes the specified `text`.
    # Inputs:
      text: str - The text to print, defaults to ""

    # Returns:
      None

    # Raises:
      None"""
    print(text, end="", flush=True)


class ProgramWarnings(UserWarning):
    """Warnings Raised for user defined Warnings in `console.warn` by default."""


class AssertationWarning(UserWarning):
    """Warnings Raised for assertion errors in `console._assert()`."""


class console:
    """Limited Functionality version of JavaScript's console functions"""

    _counters = {"default": 0}
    _warnings = []

    def log(*args, **kwargs) -> None:
        """print(value, ..., sep=' ', end='\n', file=sys.stdout, flush=False)

        Prints the values to a stream, or to sys.stdout by default.
        Optional keyword arguments:
        file:  a file-like object (stream); defaults to the current sys.stdout.
        sep:   string inserted between values, default a space.
        end:   string appended after the last value, default a newline.
        flush: whether to forcibly flush the stream."""
        print(*args, **kwargs)

    def info(*args, **kwargs) -> None:
        """print(value, ..., sep=' ', end='\n', file=sys.stdout, flush=False)

        Prints the values to a stream, or to sys.stdout by default.
        Optional keyword arguments:
        file:  a file-like object (stream); defaults to the current sys.stdout.
        sep:   string inserted between values, default a space.
        end:   string appended after the last value, default a newline.
        flush: whether to forcibly flush the stream."""
        print(*args, **kwargs)

    def debug(*args, **kwargs) -> None:
        """print(value, ..., sep=' ', end='\n', file=sys.stdout, flush=False)

        Prints the values to a stream, or to sys.stdout by default.
        Optional keyword arguments:
        file:  a file-like object (stream); defaults to the current sys.stdout.
        sep:   string inserted between values, default a space.
        end:   string appended after the last value, default a newline.
        flush: whether to forcibly flush the stream."""
        print(*args, **kwargs)

    def warn(warning: any, _class: Optional[Type[Warning]] = ProgramWarnings) -> None:
        """# Function: console.warn
          Issue a warning
        # Inputs:
          warning: any - The variable to use as a warning
          _class: class - The class to raise the warning from, defaults to ProgramWarnings

        # Returns:
          None

        # Raises:
          None"""
        ind = 1
        while warning in console._warnings:
            warning = "{message}({ind})"
            ind += 1
        console._warnings.append(warning)
        ww(warning, _class)

    def error(*args, **kwargs) -> None:
        """print(value, ..., sep=' ', end='\n', file=sys.stderr, flush=False)

        Prints the values to sys.stderr.
        Optional keyword arguments:
        sep:   string inserted between values, default a space.
        end:   string appended after the last value, default a newline.
        flush: whether to forcibly flush the stream."""
        print(bcolors.FAIL, *args, bcolors.RESET, file=sys.stderr, **kwargs)

    def _assert(condition: bool, message: str = "Assertion Failed") -> None:
        """# Function: console._assert
          Makes an assertion check
        # Inputs:
          condition: bool - The condition to run an assert check on
          message: str - The message to raise if the assertion is False, defaults to "Assertion Failed"

        # Returns:
          None

        # Raises:
          None"""
        if not condition:
            console.warn(message, AssertationWarning)

    def count(label: str = "default") -> None:
        """# Function: console.count
          Increment a counter by one
        # Inputs:
          label: str - The counter to increment, defaults to "default"

        # Returns:
          None

        # Raises:
          None"""
        if console._counters[label]:
            console._counters[label] += 1
        else:
            console._counters[label] = 1
        print(f"{label}: {console._counters[label]}")

    def countReset(label: str = "default") -> None:
        """# Function: console.countReset
          Reset a counter to 0
        # Inputs:
          label: str - The counter to reset, defaults to "default"

        # Returns:
          None

        # Raises:
          None"""
        console._counters[label] = 0

    def clear(ascii: bool = False) -> None:
        """# Function: console.clear
          Clears the screen
        # Inputs:
          ascii: bool - Wether to use ASCII to clear the screen, defaults to False

        # Returns:
          None

        # Raises:
          None"""
        clear(ascii)


class sql:
    """# Class: sql
    Easy SQL manipulation"""

    def addTable(self, tableName: str) -> None:
        """# Function: sql.addTable
          Adds a table to the database
        # Inputs:
          tableName: str - The name of the table to create

        # Returns:
          None

        # Raises:
          None"""
        create = f"""CREATE TABLE IF NOT EXISTS {tableName}
                (id INTEGER PRIMARY KEY AUTOINCREMENT"""
        indent = "                "
        tableProperties = [
            {"name": "name", "type": "TEXT"},
            {"name": "value", "type": "TEXT"},
        ]
        for property in tableProperties:
            create = f"""{create},
{indent}{property["name"]} {property["type"]} NOT NULL"""
        create = f"{create});"
        self.con.execute(create)
        self.con.commit()
        self.table = tableName

    def __init__(self, filename: str):
        """# Function: sql.__init__
          Constructs an SQL instance
        # Inputs:
          filename: str - The name of the database file to connect to (or `:memory:`)

        # Returns:
          None

        # Raises:
          None"""
        if filename.endswith(".db") or filename == ":memory:":
            self.db = filename if filename == ":memory:" else "file:" + filename
        else:
            self.db = "file:" + filename + ".db"
        self.con = sqlite3.connect(self.db)
        self.addTable("default")

    def setTable(self, tableName: str) -> None:
        """# Function: sql.setTable
          Sets the currently active table
        # Inputs:
          tableName: str - The name of the table to use

        # Returns:
          None

        # Raises:
          None"""
        self.table = tableName

    def get(self, name: str) -> object or None:
        """# Function: sql.get
          Gets the value of a key
        # Inputs:
          name: str - The name of the key to retrieve

        # Returns:
          object or None - If the key exists, return it's value, otherwise, return `None`

        # Raises:
          AttributeError - If the table is unset"""
        if not self.table:
            raise AttributeError("Attempted to read from unset table")
        cur = self.con.execute(
            f"SELECT value FROM {self.table} WHERE name = ?", (name,)
        )
        data = cur.fetchone()
        if data:
            try:
                return ast.literal_eval(data[0])
            except:
                return data[0]
        return None

    def set(self, name: str, value: object) -> int:
        """# Function: sql.set
          Sets the value of a key
        # Inputs:
          name: str - The name of the key to set
          value: object - The value of the key

        # Returns:
          int - `1` if the key was created, `2` if it was updated

        # Raises:
          AttributeError - If the table is unset"""
        if not self.table:
            raise AttributeError("Attempted to write to unset table")
        if self.get(name):
            self.con.execute(
                f"UPDATE {self.table} SET value = ? WHERE name = ?", (str(value), name)
            )
            self.con.commit()
            return 2
        else:
            self.con.execute(
                f"INSERT INTO {self.table} (name, value) VALUES (?, ?)",
                (name, str(value)),
            )
            self.con.commit()
            return 1

    def delete(self, name: str) -> None:
        """# Function: sql.delete
          Deletes a key from the table
        # Inputs:
          name: str - The name of the key to delete

        # Returns:
          None

        # Raises:
          AttributeError - If the table is unset"""
        if not self.table:
            raise AttributeError("Attempted to delete from unset table")
        if get(name):
            self.con.execute(f"""DELETE FROM {self.table} WHERE name = ?""", (name,))
            self.con.commit()

    def delete_all(self) -> None:
        """# Function: sql.delete_all
          Deletes all keys from the table
        # Inputs:
          None

        # Returns:
          None

        # Raises:
          AttributeError - If the table is unset"""
        if not self.table:
            raise AttributeError("Attempted to delete from unset table")
        if get(name):
            self.con.execute(f"""DELETE FROM {self.table}""")
            self.con.commit()

    def close(self) -> None:
        """# Function: sql.close
          Closes the database connection
        # Inputs:
          None

        # Returns:
          None

        # Raises:
          None"""
        self.con.close()
        self.con = None
        self.db = None
        self.table = None
