#!/bin/sh
##
# Source in ~/.profile to handle switching from MATE<->i3
#
# In TWILYSPARKLE (Dell XPS 15 9550)
# - Enable natural and horizontal scrolling
# - Main Display is eDP-1
# - Configure the external monitor (if connected)
# - Touchpad ID is 06CB:7A13
#
# In DEMORGOGON:
# - Fix the monitor arrangement
##

if [ "$(hostname)" = "DEMORGOGON" ]; then
	# Fix the workstation's monitors
	xrandr --output DP-4 --right-of DP-0
	xrandr --output DP-7 --right-of DP-4
	xrandr --output DP-4 --primary
elif [ "$(hostname)" = "TWILYSPARKLE" ]; then
	xrandr --output eDP-1 --primary --mode 3840x2160

	# If the external's connected, set it up
	if [ ! -z "$(xrandr | grep 'HDMI-1 connected')" ]; then
		xrandr --output HDMI-1 --mode 1920x1080 --scale-from 3840x2160 --panning 3840x2160+3840+0 --right-of eDP-1
	fi

	TOUCHPAD_ID=$(xinput list | sed -nr 's/^.+06CB:7A13.+id=([0-9]+).+$/\1/p')
	if [ ! -z $TOUCHPAD_ID ]; then
		# Enable "natural" scrolling
		PROP_ID=$(xinput list-props $TOUCHPAD_ID | sed -nr 's/^.+libinput\sNatural\sScrolling\sEnabled\s\(([0-9]+)\):.+$/\1/p')
		if [ ! -z $PROP_ID ]; then
			xinput set-prop $TOUCHPAD_ID $PROP_ID 1
		fi

		# Enable horizontal scrolling
		PROP_ID=$(xinput list-props $TOUCHPAD_ID | sed -nr 's/^.+libinput\sHorizontal\sScroll\sEnabled\s\(([0-9]+)\):.+$/\1/p')
		if [ ! -z $PROP_ID ]; then
			xinput set-prop $TOUCHPAD_ID $PROP_ID 1
		fi
		unset PROP_ID
	fi
	unset TOUCHPAD_ID
fi

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

export GTK_THEME=Arc-Dark

