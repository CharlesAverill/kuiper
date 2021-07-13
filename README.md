# Kuiper

A terminal-based dating application for UTD students, built with the `curses` api

## Usage
```bash
$ pip install kuiper              # Install
$ kuiper                          # Start the TUI
$ kuiper -c USERNAME PASSWORD     # Login with credentials
$ kuiper -i                       # Initialize the database
$ kuiper -h                       # View the help menu
$ kuiper -l config_updates.yaml   # Update server configs
$ kuiper -q                       # Suppress server output
$ kuiper -s                       # Start kuiper server
```

## Main Server

The main Kuiper server is publicly hosted at `35.172.42.184:8000`

If you overwrite your `access_host` or `port` configs and wish to connect to the main server again, 
use the `-l` option to update your configs

## Inspiration
[UTD Bruh Moments IG Post](https://www.instagram.com/p/CRCJhEmpbI0/)

[Original Reddit Post](https://www.reddit.com/r/utdallas/comments/od9roi/how_easy_is_it_to_find_men_above_the_age_of_23_at/)
