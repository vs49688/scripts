#!/bin/sh -e
##
# Game launching script for CAPRICA.
# - Made for "custom games" on Steam with streaming
##

if [ $# -ne 1 ]; then
	echo "Usage: $0 <trl|trldebug|tra|tru|tr2013|eso|ds2|bl|ac1|nier|soaser|gw2>"
	exit 2
fi

export LANG=en_AU.UTF-8
export LANGUAGE=en_AU:en_GB:en

if [ $1 = "trl" ]; then
	export WINEPREFIX=${HOME}/.wine-trl
	cd ${HOME}/Games/Tomb\ Raider\ Legend
	exec wine trl.exe
elif [ $1 = "trldebug" ]; then
	export WINEPREFIX=${HOME}/.wine-trl
	cd ${HOME}/Games/Tomb\ Raider\ Legend
	exec wine tr7.exe
elif [ $1 = "tra" ]; then
	export WINEPREFIX=${HOME}/.wine-trl
	cd ${HOME}/Games/Tomb\ Raider\ Anniversary
	exec wine tra.exe
elif [ $1 = "tru" ]; then
	export WINEPREFIX=${HOME}/.wine-trl
	cd ${HOME}/Games/Tomb\ Raider\ Underworld
	exec wine tru.exe
elif [ $1 = "tr2013" ]; then
	export WINEPREFIX=${HOME}/.wine-tr2013
	cd ${HOME}/Games/Tomb\ Raider\ GOTY
	exec wine TombRaider.exe
elif [ $1 = "eso" ]; then
	export WINEPREFIX=${HOME}/.wine-eso
	exec wine ${HOME}/Games/Zenimax\ Online/Launcher/Bethesda.net_Launcher.exe
elif [ $1 = "ds2" ]; then
	export WINEPREFIX=${HOME}/.wine-ds2
	exec wine ${HOME}/Games/Dark\ Souls\ 2\ -\ Scholar\ of\ the\ First\ Sin/DarkSoulsII.exe
elif [ $1 = "bl" ]; then
	export WINEPREFIX=${HOME}/.wine-wow
	wine reg ADD HKCU\\Software\\Wine\\DllOverrides /t REG_SZ /f /v "ucrtbase" /d "native,builtin"
	wine reg ADD HKCU\\Software\\Wine\\DllOverrides /t REG_SZ /f /v "api-ms-win-crt-private-l1-1-0" /d "native,builtin"
	# Command for OW
	# xmodmap -e "keycode 37 = Control_R"
	exec wine ${HOME}/Games/Battle.net/Battle.net.exe
elif [ $1 = "ac1" ]; then
	export WINEPREFIX=${HOME}/Games/AssassinsCreed/wine
	cd ${HOME}/Games/AssassinsCreed
	exec wine ${HOME}/Games/AssassinsCreed/AssassinsCreed_Dx10.exe
elif [ $1 = "nier" ]; then
	export WINEPREFIX=${HOME}/Games/NierAutomata/wine
	cd ${HOME}/Games/NierAutomata
	exec wine ${HOME}/Games/NierAutomata/NieRAutomata.exe
elif [ $1 = "soaser" ]; then
	export WINEPREFIX=${HOME}/Games/SoaSE
	cd ${HOME}/Games/SoaSE
	exec wine "${HOME}/Games/SoaSE/Sins of a Solar Empire Rebellion.exe"
elif [ $1 = "gw2" ]; then
	export WINEPREFIX=${HOME}/Games/GuildWars2/wine
	cd ${HOME}/Games/GuildWars2/
	exec wine ${HOME}/Games/GuildWars2/Guild\ Wars\ 2/Gw2-64.exe
fi
