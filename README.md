# Kuiper

A terminal-based dating application for UTD students, built with the `curses` API.

## Usage
```bash
$ pip install kuiper           # Install
$ kuiper                       # Start the TUI
$ kuiper -c USERNAME PASSWORD  # Login with credentials
$ kuiper -i                    # Initialize the database
$ kuiper -h                    # View the help menu
$ kuiper -l new_configs.yaml   # Update server configs
$ kuiper -q                    # Suppress server output
$ kuiper -s                    # Start kuiper server
```

## Configs

The follow are the configuration options supported by Kuiper. 

To modify Kuiper's configs, create a `config.yaml` file with the keys and values you'd like to overwrite, 
and call `kuiper -l config.yaml`

| Config | Default Value | Description |
| --- | --- | --- |
| bind_host | "127.0.0.1" | The address on which the server will be hosted via `kuiper -s` |
| port | 8000 | The port on which the server will be hosted via `kuiper -s`
| access_host | "35.172.42.184" | The address to the server the client will ping. The defualt value is the static IP address of Kuiper's main server |
| db_path | "kuiper.db" | The path to the server's user and post database |
| required_email_suffix | "@utdallas.edu" | The email suffix required during registration. For no requirement, set to `""` |
| text_editor | "vim" | The text editor called via the `subprocess` module to write posts and comments |


## Inspiration
[UTD Bruh Moments IG Post](https://www.instagram.com/p/CRCJhEmpbI0/)

[Original Reddit Post](https://www.reddit.com/r/utdallas/comments/od9roi/how_easy_is_it_to_find_men_above_the_age_of_23_at/)
