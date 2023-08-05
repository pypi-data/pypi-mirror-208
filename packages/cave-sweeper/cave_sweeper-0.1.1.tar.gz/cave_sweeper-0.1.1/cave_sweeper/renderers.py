import os
from tkinter import Tk, Label, Radiobutton, ttk, StringVar, Button, Frame
from field_slot import Field
from utils import count_digits


def render_selection_window():
    def _render_minefield_window():
        os.environ["MINEFIELD_COLUMNS"] = cols_combo.get()
        os.environ["MINEFIELD_ROWS"] = rows_combo.get()
        os.environ["DIFFICULTY"] = difficulty.get()
        selection_window.destroy()
        render_minefield_window()

    selection_window = Tk()
    selection_window.title("Pick your settings")
    selection_window.geometry("350x400")

    rows_combo_label = Label(master=selection_window, text="Rows: ")
    rows_combo_label.place(x=125, y=150)

    rows_combo = ttk.Combobox(selection_window, width=5)
    rows_combo['values'] = (10, 15, 20, 25)
    rows_combo.set(10)
    rows_combo.place(x=170, y=150)

    cols_combo_label = Label(master=selection_window, text="Cols: ")
    cols_combo_label.place(x=125, y=175)

    cols_combo = ttk.Combobox(selection_window, width=5)
    cols_combo['values'] = (10, 15, 20, 25)
    cols_combo.set(10)
    cols_combo.place(x=170, y=175)

    difficulty = StringVar()
    difficulty.set("easy")

    rb_easy = Radiobutton(master=selection_window, text="Easy", variable=difficulty, value="easy")
    rb_easy.place(x=125, y=225)

    rb_hard = Radiobutton(master=selection_window, text="Hard", variable=difficulty, value="hard")
    rb_hard.place(x=200, y=225)

    btn_ok = Button(master=selection_window, text="OK", width=4, height=2, command=_render_minefield_window)
    btn_ok.place(x=100, y=300)

    btn_close = Button(master=selection_window, text="Close", width=4, height=2, command=selection_window.quit)
    btn_close.place(x=200, y=300)

    selection_window.mainloop()


def render_minefield_window():
    MINEFIELD_COLUMNS = int(os.environ.get("MINEFIELD_COLUMNS", 8))
    MINEFIELD_ROWS = int(os.environ.get("MINEFIELD_ROWS", 8))
    countdown_time = MINEFIELD_COLUMNS * MINEFIELD_COLUMNS * 2

    root = Tk()
    # styling of the main app window
    root.title("Minefield")
    root.geometry(f"{MINEFIELD_COLUMNS*48 + 20}x{MINEFIELD_ROWS*38 + 130}")
    root.resizable(width=True, height=True)
    root.configure(bg="lightgray")

    # display
    display_frame = Frame(master=root, bg="grey21", width=MINEFIELD_COLUMNS*48, height=100)
    display_frame.place(x=10, y=10)

    # label to display amount of fields remaining
    remaining_label = Label(master=display_frame, bg="dim gray")
    remaining_label.config(
        font=("consolas", 50),
        width=count_digits(MINEFIELD_COLUMNS * MINEFIELD_ROWS),
        height=1,
        fg="brown1",
        text=MINEFIELD_COLUMNS * MINEFIELD_ROWS
    )
    remaining_label.place(x=10, y=14)


    # label to display amount of mines
    mines_label = Label(master=display_frame, bg="dim gray")
    mines_label.config(
        font=("consolas", 50),
        width=2,
        height=1,
        fg="brown1",
    )
    mines_label.place(x=(MINEFIELD_COLUMNS*48 + 20)/2 - 50, y=14)

    # minefield
    mf_frame = Field(
        remaining_label=remaining_label,
        mines_label=mines_label,
        master=root, bg="gray38",
        width=MINEFIELD_COLUMNS*48,
        height=MINEFIELD_ROWS*38
    )
    mf_frame.place(x=10, y=120)

    for c in range(MINEFIELD_COLUMNS):
        for r in range(MINEFIELD_ROWS):
            new_field_btn_kwargs = {
                "column": c,
                "row": r,
                "bd": 0,
                "pady": 0,
                "padx": 0,
                "width": 2,
                "height": 2,
                "highlightbackground": "gray38"
            }
            mf_frame.add_button(**new_field_btn_kwargs)

    mf_frame.place_mines()

    # label to display countdown timer
    countdown_label = Label(master=display_frame, bg="dim gray")
    countdown_label.config(
        font=("consolas", 50),
        width=4,
        height=1,
        fg="brown1",
    )
    countdown_label.place(x=(MINEFIELD_COLUMNS * 48 + 20) - 160, y=14)

    def update_label():
        nonlocal countdown_time
        if countdown_time >= 0:
            countdown_label.config(text=str(countdown_time))
            countdown_time -= 1
            root.after(1000, update_label)
        else:
            mf_frame.game_over(timeout=True)
            pass

    root.after(1000, update_label)
    # renders the app window
    root.mainloop()