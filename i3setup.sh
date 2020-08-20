#!/bin/sh
##
# Source in ~/.profile to handle switching from MATE<->i3
#
# In MORNINGSTAR (Dell XPS 15 9550)
# - Enable natural and horizontal scrolling
# - Main Display is eDP-1 on intel, eDP-1-1 on nvidia
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
		--output DP-3 --mode 1920x1080 \
		--output HDMI-0 --primary --mode 1920x1080 --right-of DP-3 \
		--output DVI-I-1 --mode 1920x1080 --right-of HDMI-0
elif [ "$(hostname)" = "DEMOGORGON" ]; then
	# Fix the workstation's monitors
	xrandr \
		--output DP-6 --mode 2560x1440 --scale-from 3840x2160 --panning 3840x2160+0+0 \
		--output DP-4 --mode 3840x2160 --pos 3840x0 --scale 1x1 --primary \
		--output DP-0 --mode 3840x2160 --pos 7680x0 --scale 1x1
elif [ "$(hostname)" = "MORNINGSTAR" ]; then

	if [ "$(prime-select query)" = "nvidia" ]; then
		MAIN_DISPLAY="eDP-1-1"
		EXT_DISPLAY="HDMI-1-1"
	else
		MAIN_DISPLAY="eDP-1"
		EXT_DISPLAY="HDMI-1"
	fi

	#xrandr --output ${MAIN_DISPLAY} --primary --mode 3840x2160
	#if [ ! -z "$(xrandr | grep "${EXT_DISPLAY} connected")" ]; then
	#	xrandr --output ${EXT_DISPLAY} --mode 1920x1080 --scale-from 3840x2160 --panning 3840x2160+3840+0 --right-of ${MAIN_DISPLAY}
	#fi

	# Drop to 1080p so the system's actually usable.
	xrandr --output ${MAIN_DISPLAY} --primary --mode 1920x1080
	if [ ! -z "$(xrandr | grep "${EXT_DISPLAY} connected")" ]; then
		xrandr --output ${EXT_DISPLAY} --mode 1920x1080 --right-of ${MAIN_DISPLAY} --scale 1x1
	fi

	unset MAIN_DISPLAY
	unset EXT_DISPLAY

	TOUCHPAD_ID=$(xinput list --id-only 'DLL06E4:01 06CB:7A13 Touchpad')
	if [ ! -z ${TOUCHPAD_ID} ]; then
		xinput set-prop ${TOUCHPAD_ID} 'libinput Natural Scrolling Enabled' 1
		xinput set-prop ${TOUCHPAD_ID} 'libinput Horizontal Scroll Enabled' 1
		xinput set-prop ${TOUCHPAD_ID} 'libinput Tapping Enabled'           1
	fi
	unset TOUCHPAD_ID
fi

RESOLUTION=$(xrandr -q | sed -nr 's/^.+primary\s+([0-9]+x[0-9]+).+$/\1/p')

if [ "${XDG_CURRENT_DESKTOP}" = "MATE"  -o "${XDG_CURRENT_DESKTOP}" = "mate" ]; then
	unset GDK_SCALE
	xrandr --dpi 96

	if [ "${RESOLUTION}" = "3840x2160" ]; then
		export QT_SCALE_FACTOR=2
		dconf write /org/mate/desktop/interface/window-scaling-factor 2
		dconf write /org/gnome/desktop/interface/scaling-factor 2
	else
		export QT_SCALE_FACTOR=1
		dconf write /org/mate/desktop/interface/window-scaling-factor 1
		dconf write /org/gnome/desktop/interface/scaling-factor 1
	fi

	# Remap Alt-to-move
	dconf write /org/gnome/desktop/wm/preferences/mouse-button-modifier "'<Control><Alt><Space>'"
	dconf write /org/mate/marco/general/mouse-button-modifier "'<Control><Alt><Space>'"
	dconf write /org/mate/settings-daemon/plugins/media-keys/home "'<Mod4>e'"
	dconf write /org/mate/marco/global-keybindings/run-command-terminal "'<Primary><Alt>t'"


	# Kill automount
	dconf write /org/mate/desktop/media-handling/automount-open false
	dconf write /org/mate/desktop/media-handling/automount false

    # Fix themes
	dconf write /org/mate/marco/general/theme                    "'Arc-Dark'"
	dconf write /org/mate/desktop/interface/gtk-theme            "'Arc-Dark'"
	dconf write /org/mate/desktop/interface/icon-theme           "'Papirus-Dark'"
	dconf write /org/mate/desktop/peripherals/mouse/cursor-theme "'mate-black'"

	# Configure Keyboard Layouts
	dconf write /org/mate/desktop/peripherals/keyboard/kbd/layouts "['us', 'ru']"
	dconf write /org/mate/desktop/peripherals/keyboard/kbd/options "['grp\tgrp:alt_caps_toggle', 'terminate\tterminate:ctrl_alt_bksp']"

	# Disable software compositing, picom's handling it
	dconf write /org/mate/marco/general/compositing-manager false

	# Fix touchpad on the laptops
	if [ "$(hostname)" = "MORNINGSTAR" -o "$(hostname)" = "BAST" ]; then
		dconf write /org/mate/desktop/peripherals/touchpad/horizontal-two-finger-scrolling true
		dconf write /org/mate/desktop/peripherals/touchpad/natural-scroll true
		dconf write /org/mate/desktop/peripherals/touchpad/tap-to-click true
	fi

elif [ "${XDG_CURRENT_DESKTOP}" = "i3" ]; then
	if [ "${RESOLUTION}" = "3840x2160" ]; then
		export GDK_SCALE=2
		export QT_SCALE_FACTOR=2
		xrandr --dpi 235
		dconf write /org/mate/desktop/interface/window-scaling-factor 2
		dconf write /org/gnome/desktop/interface/scaling-factor 2
	else
		unset GDK_SCALE
		unset QT_SCALE_FACTOR
		xrandr --dpi 96
		dconf write /org/mate/desktop/interface/window-scaling-factor 1
		dconf write /org/gnome/desktop/interface/scaling-factor 1
	fi
fi

unset RESOLUTION
