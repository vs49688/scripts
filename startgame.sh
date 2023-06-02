#!/bin/sh -e
##
# Game launching script for CAPRICA.
# - Made for "custom games" on Steam with streaming
##

if [ $# -ne 1 ]; then
	echo "Usage: $0 <trl|trldebug|tra|tru|tr2013|eso|ds2|dsr|bl|ac1|nier|soaser|bpm|hls|hl2|hl2ep1|hl2ep2|sc1|nierr|me1|me2|mcc|hoi4>"
	exit 2
fi

export LANG=en_AU.UTF-8
export LANGUAGE=en_AU:en_GB:en

if [ $1 = "trl" ]; then
	export WINEPREFIX=${HOME}/Games/Tomb\ Raider\ Legend/wine
	cd ${HOME}/Games/Tomb\ Raider\ Legend
	exec wine trl.exe
elif [ $1 = "trldebug" ]; then
	export WINEPREFIX=${HOME}/Games/Tomb\ Raider\ Legend/wine
	cd ${HOME}/Games/Tomb\ Raider\ Legend
	exec wine tr7.exe
elif [ $1 = "tra" ]; then
	export WINEPREFIX=${HOME}/Games/Tomb\ Raider\ Legend/wine
	cd ${HOME}/Games/Tomb\ Raider\ Anniversary
	exec wine tra.exe
elif [ $1 = "tru" ]; then
	export WINEPREFIX=${HOME}/Games/Tomb\ Raider\ Legend/wine
	cd ${HOME}/Games/Tomb\ Raider\ Underworld
	exec wine tru.exe
elif [ $1 = "tr2013" ]; then
	export WINEPREFIX=${HOME}/Games/Tomb\ Raider\ GOTY/wine
	cd ${HOME}/Games/Tomb\ Raider\ GOTY
	exec wine TombRaider.exe
elif [ $1 = "eso" ]; then
	export WINEPREFIX=${HOME}/.wine-eso
	exec wine ${HOME}/Games/Zenimax\ Online/Launcher/Bethesda.net_Launcher.exe
elif [ $1 = "ds2" ]; then
	export WINEPREFIX=${HOME}/.wine-ds2
	exec wine ${HOME}/Games/Dark\ Souls\ 2\ -\ Scholar\ of\ the\ First\ Sin/DarkSoulsII.exe
elif [ $1 = "dsr" ]; then
	export WINEPREFIX=${HOME}/Games/DarkSoulsRemastered/wine
	cd ${HOME}/Games/DarkSoulsRemastered
	exec wine ${HOME}/Games/DarkSoulsRemastered/DarkSoulsRemastered.exe
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
elif [ $1 = "bpm" ]; then
	export WINEPREFIX=${HOME}/Games/BPM/wine
	cd ${HOME}/Games/BPM
	exec wine ${HOME}/Games/BPM/WindowsNoEditor/BPMGame.exe
elif [ $1 = "sc1" ]; then
	cd ${HOME}/Games/SplinterCell
	export WINEPREFIX=$PWD/wine
	sed -i \
		-e 's/^Resolution=.*$/Resolution=1920x1080/g' \
		-e 's/^DesiredFOV=.*$/DesiredFOV=85.0/g' \
		-e 's/DefaultFOV=.*$/DefaultFOV=85.0/g' \
		system/SplinterCellUser.ini
	exec wine system/SplinterCell.exe
elif [ $1 = "nierr" ]; then
	cd ${HOME}/Games/NierReplicant
	export WINEPREFIX=$PWD/wine
	exec wine NieR\ Replicant\ ver.1.22474487139.exe
elif [ $1 = "me1" ]; then
	cd /media/Data2/Games/MassEffect1LE
	export WINEPREFIX=$PWD/wine
	exec wine Game/ME1/Binaries/Win64/MassEffect1.exe -NoHomeDir -SeekFreeLoadingPCConsole -Subtitles 20 -OVERRIDELANGUAGE=INT
elif [ $1 = "me2" ]; then
	cd /media/Data2/Games/MassEffect1LE
	export WINEPREFIX=$PWD/wine
	exec wine Game/ME2/Binaries/Win64/MassEffect2.exe -NoHomeDir -SeekFreeLoadingPCConsole -Subtitles 20 -OVERRIDELANGUAGE=INT
elif [ $1 = "mcc" ]; then
	cd /media/Data2/Games/HaloMCC
	export WINEPREFIX=$PWD/wine
	exec wine mcclauncher.exe
elif [ $1 = "hoi4" ]; then
	cd /media/Data2/Games/HeartsOfIronIV
	export WINEPREFIX=$PWD/wine
	exec wine dowser.exe
fi

#elif [ $1 = "hls" ]; then
	#export WINEPREFIX=${HOME}/Games/HL/wine
#fi

#hls|hl2|hl2ep1|hl2ep2

case $1 in hl*)
	export WINEPREFIX=${HOME}/Games/HL/wine
	cd ${HOME}/Games/HL

	case $1 in
		hls)    bat='Launch Half-Life Source.bat';;
		hl2)    bat='Launch Half-Life 2.bat';;
		hl2ep1) bat='Launch Half-Life 2 - Episode 1.bat';;
		hl2ep2) bat='Launch Half-Life 2 - Episode 2.bat';;
	esac

	exec wine cmd /wait /c "${HOME}/Games/HL/${bat}"
esac
