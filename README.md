# Kuiper

A terminal-based dating application for UTD students, built with the `curses` API.

## Installation

Unfamiliar with terminal stuff? Here's what you need to start using Kuiper:

1. [Install Python](https://www.python.org/downloads/release/python-379/)
2. Open up your terminal or command line
3. Type in `python3 -m pip install kuiper`. You may receive some nasty output, that's alright. Mac users might need to install XCode tools
4. Now you're ready to use Kuiper! Just type `kuiper` into your command line, and the TUI should boot.

## Usage
```bash
$ kuiper                       # Start the TUI
$ kuiper -c USERNAME PASSWORD  # Login with credentials
$ kuiper -d                    # Print configs
$ kuiper -i                    # Initialize the database
$ kuiper -h                    # View the help menu
$ kuiper -l new_configs.yaml   # Update server configs
$ kuiper --local_server        # Connect to localhost server
$ kuiper -q                    # Suppress server output
$ kuiper -s                    # Start server
```

Menu navigation is controlled by the up and down arrow keys.

When filling out a form field, the string in the bottom-right corner is the current buffer. 
Hit "Enter" to save the form field.

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
| org_name | "UTD" | The organization name to be displayed at login and registration |
| server_email_username/password | None/None | The login information for the email the server will use to send email verification codes |
| server_email_smtp_addr/port | "smtp.gmail.com"/465 | The SMTP address/port used to send emails |
| text_editor | "vim" | The text editor called via the `subprocess` module to write posts and comments |


## Inspiration
[UTD Bruh Moments IG Post](https://www.instagram.com/p/CRCJhEmpbI0/)

[Original Reddit Post](https://www.reddit.com/r/utdallas/comments/od9roi/how_easy_is_it_to_find_men_above_the_age_of_23_at/)
