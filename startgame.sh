#!/bin/sh -e
##
# Game launching script for CAPRICA.
# - Made for "custom games" on Steam with streaming
##

if [ $# -ne 1 ]; then
	echo "Usage: $0 <trl|trldebug|tra|tru|tr2013|eso|lol|ds2|me1|ark|bl|ac1|nier>"
	exit 2
fi

#xmessage -print -buttons trl,trldebug,tra,tru,tr2013,eso,lol,ds2,me1,ark "Select a game"

if [ $1 = "trl" ]; then
	export WINEPREFIX=${HOME}/.wine-trl
	cd /media/Data2/Games/Tomb\ Raider\ Legend
	exec wine trl.exe
elif [ $1 = "trldebug" ]; then
	export WINEPREFIX=${HOME}/.wine-trl
	cd /media/Data2/Games/Tomb\ Raider\ Legend
	exec wine tr7.exe
elif [ $1 = "tra" ]; then
	export WINEPREFIX=${HOME}/.wine-trl
	cd /media/Data2/Games/Tomb\ Raider\ Anniversary
	exec wine tra.exe
elif [ $1 = "tru" ]; then
	export WINEPREFIX=${HOME}/.wine-trl
	cd /media/Data2/Games/Tomb\ Raider\ Underworld
	exec wine tru.exe
elif [ $1 = "tr2013" ]; then
	export WINEPREFIX=${HOME}/.wine-tr2013
	cd /media/Data2/Games/Tomb\ Raider\ GOTY
	exec wine TombRaider.exe
elif [ $1 = "eso" ]; then
	export WINEPREFIX=${HOME}/.wine-eso
	exec wine /media/Data2/Games/Zenimax\ Online/Launcher/Bethesda.net_Launcher.exe
elif [ $1 = "lol" ]; then
	export WINEPREFIX=${HOME}/.wine-lol
	exec wine /media/Data2/Games/League\ of\ Legends/LeagueClient.exe
elif [ $1 = "ds2" ]; then
	export WINEPREFIX=${HOME}/.wine-ds2
	exec wine /media/Data2/Games/Dark\ Souls\ 2\ -\ Scholar\ of\ the\ First\ Sin/DarkSoulsII.exe
elif [ $1 = "me1" ]; then
	export WINEPREFIX=/media/Data2/wine/masseffect
	exec wine /media/Data2/wine/masseffect/drive_c/Games/Mass\ Effect/Binaries/MassEffect.exe
elif [ $1 = "ark" ]; then
	xrandr --output DP-0 --primary
	set +e
	trap 'xrandr --output DVI-I-1 --primary' TERM INT ABRT
	/media/Data2/Games/SteamLibrary/steamapps/common/ARK/ShooterGame/Binaries/Linux/ShooterGame
	xrandr --output DVI-I-1 --primary
	set -e
elif [ $1 = "bl" ]; then
	export WINEPREFIX=${HOME}/.wine-wow
	wine reg ADD HKCU\\Software\\Wine\\DllOverrides /t REG_SZ /f /v "ucrtbase" /d "native,builtin"
	wine reg ADD HKCU\\Software\\Wine\\DllOverrides /t REG_SZ /f /v "api-ms-win-crt-private-l1-1-0" /d "native,builtin"
	# Command for OW
	# xmodmap -e "keycode 37 = Control_R"
	exec wine ${HOME}/Games/Battle.net/Battle.net.exe
elif [ $1 = "ac1" ]; then
	export WINEPREFIX=/media/Data2/Games/AssassinsCreed/wine
	cd /media/Data2/Games/AssassinsCreed
	exec wine /media/Data2/Games/AssassinsCreed/AssassinsCreed_Dx10.exe
elif [ $1 = "crysis" ]; then
	export WINEPREFIX=/media/Data2/Games/Crysis/wine
	cd /media/Data2/Games/Crysis/Bin64
	exec wine /media/Data2/Games/Crysis/Bin64/Crysis.exe
elif [ $1 = "nier" ]; then
	export LANG=en_AU.UTF-8
	export LANGUAGE=en_AU:en_GB:en
	export WINEPREFIX=/media/Data2/Games/NierAutomata/wine
	cd /media/Data2/Games/NierAutomata
	exec wine /media/Data2/Games/NierAutomata/NieRAutomata.exe
fi
