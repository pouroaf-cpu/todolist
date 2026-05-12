import customtkinter as ctk

from ui.styles import COLORS


def make_entry(parent, placeholder_text=""):
    return ctk.CTkEntry(
        parent,
        height=36,
        corner_radius=10,
        fg_color=COLORS["input_bg"],
        border_color=COLORS["border"],
        text_color=COLORS["text_primary"],
        placeholder_text=placeholder_text,
    )


def make_option_menu(parent, values, command=None):
    return ctk.CTkOptionMenu(
        parent,
        values=values,
        command=command,
        height=36,
        corner_radius=10,
        fg_color=COLORS["input_bg"],
        button_color=COLORS["border"],
        button_hover_color="#36516f",
        text_color=COLORS["text_primary"],
    )


def make_textbox(parent, height):
    return ctk.CTkTextbox(
        parent,
        height=height,
        corner_radius=10,
        fg_color=COLORS["input_bg"],
        border_color=COLORS["border"],
        border_width=1,
        text_color=COLORS["text_primary"],
    )
