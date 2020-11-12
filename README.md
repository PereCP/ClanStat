# ClanStat

ClanStat is a Discord bot that uses Battlemetrics API info about Rust servers to check for online players. The bot messages are in Spanish.

# Purpose

This bot is meant to prevent offline raids from big clans in this game while being more useful than having 10 open Battlemetrics tabs of players on the browser.

# Commands

All commands start with the dollar ($) character by default.

- $init [ID] | Initializes the bot, requires a Battlemetrics server ID as parameter.
- $a | Forces an update and shows the new player list.
- $manual [ID] | Manually adds a player to the list, requires the player Battlemetrics ID as a parameter.
- $list | Lists current players and their status.
- $borrar [ID] | Removes a player from the list.
- $extraer | Extracts and displays the current configuration for future usage or backup.
- $leer [config] | Reads and applies configuration obtained from $extraer.

