#!/bin/sh
##
# Source in ~/.profile to handle switching from MATE<->i3
#
# In MORNINGSTAR (Dell XPS 15 9550)
# - Enable natural and horizontal scrolling
# - Main Display is eDP-1
# - Configure the external monitor (if connected)
# - Touchpad ID is 06CB:7A13
#
# In DEMOGORGON:
# - Fix the monitor arrangement
#
# In CAPRICA:
# - Fix the monitor arrangement
##

if [ "$(hostname)" = "CAPRICA" ]; then
	xrandr \
		--output DVI-I-1 --primary --mode 1920x1080 --right-of DP-0 \
		--output HDMI-0 --mode 1920x1080 --right-of DVI-I-1
elif [ "$(hostname)" = "DEMOGORGON" ]; then
	# Fix the workstation's monitors
	xrandr \
		--output DP-7 --mode 1920x1080 --scale-from 3840x2160 --panning 3840x2160+0+0 \
		--output DP-4 --mode 3840x2160 --pos 3840x0 --scale 1x1 --primary \
		--output DP-0 --mode 3840x2160 --pos 7680x0 --scale 1x1
elif [ "$(hostname)" = "MORNINGSTAR" ]; then
	# xrandr --output eDP-1 --primary --mode 3840x2160
	# if [ ! -z "$(xrandr | grep 'HDMI-1 connected')" ]; then
	# 	xrandr --output HDMI-1 --mode 1920x1080 --scale-from 3840x2160 --panning 3840x2160+3840+0 --right-of eDP-1
	# fi

	# Drop to 1080p so the system's actually usable.
	xrandr --output eDP-1 --primary --mode 1920x1080
	if [ ! -z "$(xrandr | grep 'HDMI-1 connected')" ]; then
		xrandr --output HDMI-1 --mode 1920x1080 --right-of eDP-1
	fi

	TOUCHPAD_ID=$(xinput list --id-only 'DLL06E4:01 06CB:7A13 Touchpad')
	if [ ! -z ${TOUCHPAD_ID} ]; then
		xinput set-prop ${TOUCHPAD_ID} 'libinput Natural Scrolling Enabled' 1
		xinput set-prop ${TOUCHPAD_ID} 'libinput Horizontal Scroll Enabled' 1
	fi
	unset TOUCHPAD_ID
fi

RESOLUTION=$(xrandr -q | sed -nr 's/^.+primary\s+([0-9]+x[0-9]+).+$/\1/p')

if [ "${XDG_CURRENT_DESKTOP}" = "MATE" ]; then
	unset GDK_SCALE
	xrandr --dpi 96
	gsettings set org.gnome.desktop.interface scaling-factor 1

	if [ "${RESOLUTION}" = "3840x2160" ]; then
		export QT_SCALE_FACTOR=2
		dconf write /org/mate/desktop/interface/window-scaling-factor 2
	else
		export QT_SCALE_FACTOR=1
		dconf write /org/mate/desktop/interface/window-scaling-factor 1
	fi
elif [ "${XDG_CURRENT_DESKTOP}" = "i3" ]; then
	if [ "${RESOLUTION}" = "3840x2160" ]; then
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

