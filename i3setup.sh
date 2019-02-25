#!/bin/sh
##
# Source in ~/.profile to handle switching from MATE<->i3
#
# In TWILYSPARKLE (Dell XPS 15 9550)
# - Enable "Natural Scrolling" if using i3.
# - Main Display is eDP-1
# - Touchpad ID is 06CB:7A13
#
# In ZANE-DEVPC:
# - Fix the monitor arrangement
##

RESOLUTION=$(xrandr -q | sed -nr 's/^.+primary\s+([0-9]+x[0-9]+).+$/\1/p')

if [ "$XDG_CURRENT_DESKTOP" = "MATE" ]; then
	unset GDK_SCALE
	xrandr --dpi 96
	gsettings set org.gnome.desktop.interface scaling-factor 1

	if [ "$RESOLUTION" = "3840x2160" ]; then
		export QT_SCALE_FACTOR=2
		dconf write /org/mate/desktop/interface/window-scaling-factor 2
	else
		export QT_SCALE_FACTOR=1
		dconf write /org/mate/desktop/interface/window-scaling-factor 1
	fi
elif [ "$XDG_CURRENT_DESKTOP" = "i3" ]; then
	# Enable "natural" scrolling
	TOUCHPAD_ID=$(xinput list | sed -nr 's/^.+06CB:7A13.+id=([0-9]+).+$/\1/p')
	if [ ! -z $TOUCHPAD_ID ]; then
		NS_ID=$(xinput list-props $TOUCHPAD_ID | sed -nr 's/^.+libinput\sNatural\sScrolling\sEnabled\s\(([0-9]+)\):.+$/\1/p')
		xinput set-prop $TOUCHPAD_ID $NS_ID 1
		unset NS_ID
	fi
	unset TOUCHPAD_ID

	if [ "$RESOLUTION" = "3840x2160" ]; then
		export GDK_SCALE=2
		export QT_SCALE_FACTOR=2
		xrandr --dpi 235
		gsettings set org.gnome.desktop.interface scaling-factor 2
		dconf write /org/mate/desktop/interface/window-scaling-factor 2
	else
		unset GDK_SCALE
		unset QT_SCALE_FACTOR
		xrandr --dpi 96
		gsettings set org.gnome.desktop.interface scaling-factor 0
		dconf write /org/mate/desktop/interface/window-scaling-factor 0
	fi
fi

unset RESOLUTION

# Fix workstation's monitors
if [ "$(hostname)" = "ZANE-DEVPC" ]; then
	xrandr --output DP-4 --right-of DP-0
	xrandr --output DP-7 --right-of DP-4
	xrandr --output DP-4 --primary
fi

export GTK_THEME=Arc-Dark

