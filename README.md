# Discord Bot for League Stats

## What

It's a bot for Discord that scrapes the Riot API using [Cassiopeia](https://github.com/meraki-analytics/cassiopeia).
Data returned will always be from the last 24 hours of a user's match history.

## How

The default prefix is `&karg`, usable commands are:

- `games`: print number of games and hours played.
- `champ`: print pie chart showing recent champion pool.
- `raw`: print raw table of match history data.
