import os
from tkinter import Button, Frame, messagebox
from random import randint
from utils import count_digits
from settings import DIFFICULTY_MAPPING






class Field(Frame):

    def __init__(self, remaining_label, mines_label, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.remaining_label = remaining_label
        self.mines_label = mines_label

        # a dict in which each key is a (x,y) tuple coordinate
        # and the associated value is a FieldButton object
        self._all_buttons = {}

        # a list in which each element is a (x,y) tuple coordinate
        # for a mine
        self._mines = []

        # a counter to keep track of how many buttons have been
        # opened or flagged
        self.swept = 0

    @property
    def columns(self):
        return int(os.environ.get("MINEFIELD_COLUMNS", 8))

    @property
    def rows(self):
        return int(os.environ.get("MINEFIELD_ROWS", 8))

    @property
    def difficulty(self):
        return DIFFICULTY_MAPPING[os.environ.get("DIFFICULTY", "easy")]

    def is_valid_coordinate(self, x, y):
        return (0 <= x <= self.rows - 1) and (0 <= y <= self.columns - 1)

    @property
    def all_buttons(self):
        return self._all_buttons

    def add_button(self, *args, **kwargs):
        field_btn = FieldButton(master=self, *args, **kwargs)
        row, col = kwargs["row"], kwargs["column"]
        field_btn.grid(column=col, row=row)
        self._all_buttons[(row, col)] = field_btn

    @property
    def mines(self):
        return self._mines

    def place_mines(self):
        if self.mines:
            return

        # DIFFICULTY 1 = Between 10% - 20%
        # DIFFICULTY 2 = Between 20% - 40%
        field_size = self.rows * self.columns
        mines_amount = randint(
            round(self.difficulty * 10 / 100 * field_size),
            round(self.difficulty * 2 * 10 / 100 * field_size)
        )
        self.mines_label.config(text=mines_amount,  width=count_digits(mines_amount))
        for _ in range(0, mines_amount):
            while True:
                col = randint(0, self.columns - 1)
                row = randint(0, self.rows - 1)
                mine = (row, col)

                if mine not in self.mines:
                    self.mines.append(mine)
                    break

    @property
    def remaining_fields(self):
        return len(self.all_buttons) - self.swept

    def update_remaining_fields(self):
        self.remaining_label.config(text=self.remaining_fields)
        if self.remaining_fields == len(self.mines):
            # TODO: victory!
            pass

    def _destroy(self):
        self.master.destroy()

    def game_over(self, timeout=False):
        if not timeout:
            msg =  "You stept on a mine..."
        else:
            msg = "You ran out of time..."
        messagebox.showwarning(title="You blew it!", message=msg)
        self.master.destroy()


class FieldButton(Button):
    def __init__(self, column, row, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.coordinates = (row, column)
        self.bind("<Button-1>", self.on_left_click)
        self.bind("<Button-2>", self.on_right_click)


    @property
    def is_mine(self):
        return self.coordinates in self.master.mines


    def on_left_click(self, event):
        if self.is_mine:
            if not self.cget("text"):
                self.config(text="💣")
                self.master.game_over()
                return

        elif not self.cget("text"):
            self.master.swept += 1
            self.config(text=str(self.surrounding_mines))
            fg = "black"

            if self.surrounding_mines == 0 and not self.cget('state') == 'disabled':
                self.config(state="disabled")
                for coordinate in self.neighbors:
                    self.master.all_buttons[coordinate].on_left_click(None)

            elif self.surrounding_mines == 1:
                fg = "blue"
            elif self.surrounding_mines == 2:
                fg = "green"
            elif self.surrounding_mines == 3:
                fg = "red"
            elif self.surrounding_mines == 4:
                fg = "magenta4"
            else:
                fg = "purple4"

            self.config(fg=fg)

        elif self.cget("text") == "🚩" and event:
            self.config(text="")
            self.master.swept -= 1

        elif self.cget("text").isnumeric():
            # do nothing... this field has been swept.
            return

        self.master.update_remaining_fields()


    def on_right_click(self, event):
        if self.cget("text") == "🚩":
            self.config(text="")
            self.master.swept -= 1

        elif not self.cget("text"):
            self.config(text="🚩")
            self.master.swept += 1

        elif self.cget("text").isnumeric():
            # do nothing... this field has been swept.
            return

        self.master.update_remaining_fields()

    @property
    def neighbors(self):
        row, col = self.coordinates
        left_range = [(x, col-1) for x in range(row-1, row+2) if self.master.is_valid_coordinate(x, col-1)]
        middle_range = [(x, col) for x in range(row-1, row+2) if x != row and self.master.is_valid_coordinate(x, col)]
        right_range = [(x, col+1) for x in range(row-1, row+2) if self.master.is_valid_coordinate(x, col+1)]
        return left_range + middle_range + right_range


    @property
    def surrounding_mines(self):
        return len([coordinate for coordinate in self.neighbors if coordinate in self.master.mines])

