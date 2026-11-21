AlteringCave_MapScripts::
	map_script MAP_SCRIPT_ON_TRANSITION, AlteringCave_OnTransition
	.byte 0

AlteringCave_OnTransition:
	setflag FLAG_LANDMARK_ALTERING_CAVE
	addvar VAR_ALTERING_CAVE_WILD_SET, 1
	goto_if_lt VAR_ALTERING_CAVE_WILD_SET, 9, AlteringCave_Ready
	setvar VAR_ALTERING_CAVE_WILD_SET, 0
AlteringCave_Ready:
	end

