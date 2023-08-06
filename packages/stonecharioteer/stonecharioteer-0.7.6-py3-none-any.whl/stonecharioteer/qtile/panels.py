"""This is the list of panels and widgets for those panels."""
from libqtile.widget import (
    Battery,
    CPU,
    CapsNumLockIndicator,
    Clock,
    CurrentLayout,
    GroupBox,
    HDDGraph,
    Memory,
    Net,
    QuickExit,
    Spacer,
    Sep,
    Systray,
    TextBox,
    Volume,
    WindowName,
)

from libqtile.bar import Bar, STRETCH

from stonecharioteer.constants import colors

FONT = "JetBrainsMono Nerd Font Mono"
FONT_SIZE = 14


def autorandr(config):
    from libqtile import qtile

    qtile.cmd_spawn(f"/opt/qtile/bin/autorandr {config}")


def get_top_bar(cfg: dict):
    """Gets default top bar"""
    system_tray = Systray(foreground=colors[6], background=colors[0], padding=5)
    capslock_numlock_indicator = CapsNumLockIndicator(
        foreground=colors[6],
        background=colors[0],
        font=cfg.get("font", FONT),
        fontsize=cfg.get("font_size", FONT_SIZE),
    )
    cpu_indicator = CPU(
        foreground=colors[6],
        background=colors[0],
        font=cfg.get("font", FONT),
        fontsize=cfg.get("font_size", FONT_SIZE),
    )
    memory_indicator = Memory(
        foreground=colors[6],
        background=colors[0],
        font=cfg.get("font", FONT),
        fontsize=cfg.get("font_size", FONT_SIZE),
    )
    hdd_indicator = HDDGraph(
        foreground=colors[6],
        background=colors[0],
    )
    volume_control = Volume(
        cardid="1",
        foreground=colors[6],
        background=colors[0],
        font=cfg.get("font", FONT),
        fontsize=cfg.get("font_size", FONT_SIZE),
    )
    network_indicator = Net(
        foreground=colors[6],
        background=colors[0],
        font=cfg.get("font", FONT),
        fontsize=cfg.get("font_size", FONT_SIZE),
    )
    # TODO: Only add this if this is a laptop, control through config.
    battery_indicator = Battery(
        foreground=colors[6],
        background=colors[0],
        font=cfg.get("font", FONT),
        fontsize=cfg.get("font_size", FONT_SIZE),
    )
    quick_exit = QuickExit(
        foreground=colors[6],
        background=colors[0],
        font=cfg.get("font", FONT),
        fontsize=cfg.get("font_size", FONT_SIZE),
    )
    default_size = 24
    default_top_bar = Bar(
        [
            TextBox(
                text="Battery [",
                foreground=colors[6],
                background=colors[0],
                font=cfg.get("font", FONT),
                fontsize=12,
            ),
            battery_indicator,
            TextBox(
                text="]",
                foreground=colors[6],
                background=colors[0],
                font=cfg.get("font", FONT),
                fontsize=cfg.get("font_size", FONT_SIZE),
            ),
            quick_exit,
            get_sep(cfg),
            Spacer(length=STRETCH, foreground=colors[2], background=colors[0]),
            cpu_indicator,
            get_sep(cfg),
            memory_indicator,
            get_sep(cfg),
            TextBox(
                text="HDD:",
                foreground=colors[6],
                background=colors[0],
                font=cfg.get("font", FONT),
                fontsize=cfg.get("font_size", FONT_SIZE),
            ),
            hdd_indicator,
            get_sep(cfg),
            system_tray,
            TextBox(
                text="Net:",
                foreground=colors[6],
                background=colors[0],
                font=cfg.get("font", FONT),
                fontsize=cfg.get("font_size", FONT_SIZE),
            ),
            network_indicator,
            get_sep(cfg),
            TextBox(
                text="Vol:",
                foreground=colors[6],
                background=colors[0],
                font=cfg.get("font", FONT),
                fontsize=cfg.get("font_size", FONT_SIZE),
            ),
            volume_control,
            get_sep(cfg),
            capslock_numlock_indicator,
            Sep(linewidth=0, padding=5, foreground=colors[2], background=colors[0]),
        ],
        default_size,
    )
    return default_top_bar


def get_bottom_bar(cfg: dict):
    """Builds the bottom bar"""
    current_layout = CurrentLayout(
        font=cfg.get("font", FONT),
        fontsize=cfg.get("font_size", FONT_SIZE),
        foreground=colors[6],
        background=colors[0],
    )
    group_box = GroupBox(
        font=cfg.get("font", FONT),
        fontsize=12,
        margin_x=5,
        margin_y=3,
        padding_y=5,
        padding_x=5,
        borderwidth=3,
        active=colors[2],
        inactive=colors[9],
        rounded=False,
        highlight_color=colors[1],
        highlight_method="line",
        this_current_screen_border=colors[3],
        this_screen_border=colors[4],
        other_current_screen_border=colors[6],
        other_screen_border=colors[4],
        foreground=colors[2],
        background=colors[0],
        use_mouse_wheel=False,
    )

    window_name = WindowName(
        font=cfg.get("font", FONT),
        fontsize=cfg.get("font_size", FONT_SIZE),
        foreground=colors[3],
        background=colors[0],
        padding_x=10,
        margin_x=10,
    )
    clock_widget = Clock(
        foreground=colors[8],
        background=colors[0],
        format="%A, %B %d - %H:%M",
        font=cfg.get("font", FONT),
        fontsize=cfg.get("font_size", FONT_SIZE),
    )

    default_size = 24

    default_bottom_bar = Bar(
        [
            Sep(linewidth=0, padding=5, foreground=colors[2], background=colors[0]),
            current_layout,
            get_sep(cfg),
            group_box,
            get_sep(cfg),
            window_name,
            get_sep(cfg),
            clock_widget,
        ],
        default_size,
    )
    return default_bottom_bar


def get_sep(cfg: dict):
    return TextBox(
        text="|",
        font=cfg.get("font", FONT),
        background=colors[0],
        foreground=colors[10],
        padding=2,
        fontsize=cfg.get("font_size", FONT_SIZE),
    )
