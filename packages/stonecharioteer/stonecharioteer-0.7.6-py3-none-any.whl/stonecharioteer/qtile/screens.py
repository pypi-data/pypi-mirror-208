"""This module configures the monitors depending on how many displays there
are.
"""
from libqtile.config import Screen
from stonecharioteer.qtile.panels import get_top_bar, get_bottom_bar
from stonecharioteer.utils.displays import get_display_info


def configure_screens(cfg: dict):
    """This function configures the screens based on how many active
    monitors there are currently."""
    displays = get_display_info()

    screens = []
    default_screen = Screen(
        top=get_top_bar(cfg),
        bottom=get_bottom_bar(cfg),
    )
    if len(displays) == 1:
        # If there is only 1 display, it should contain the default screen.
        screens = [default_screen]
    elif len(displays) == 2:
        # if there are 2 displays and one of them is the eDP, the default screen
        # should be the one that isn't the eDP (laptop screen)
        used_default_screen = False
        for display in displays:
            if display["name"] == "eDP":
                screen = Screen(bottom=get_bottom_bar(cfg))
                screens.append(screen)
            else:
                # account for the fact that both screens could be external screens.
                # In that case, the first identified screen will be the default
                # screen.
                # TODO: Need to figure out a way to get this data from a TOML.
                # Perhaps I can set some screen priority.
                # TODO: Figure out how I can get a screen's model/name and then
                # use that to my advantage.
                if not used_default_screen:
                    screens.append(default_screen)
                    used_default_screen = True
                else:
                    screen = Screen(bottom=get_bottom_bar(cfg))
                    screens.append(screen)
    else:
        # There are more than 2 screens.
        used_default_screen = False

        for display in displays:
            display_name = display["name"]
            if "DisplayPort" in display_name and not used_default_screen:
                screens.append(default_screen)
                used_default_screen = True
            else:
                screen = Screen(bottom=get_bottom_bar(cfg))
                screens.append(screen)
        # if the default screen wasn't used anywhere (not quite possible, but who knows?)
        # set the last identified screen to the default screen.
        if not used_default_screen:
            screens[-1] = default_screen
    return screens
