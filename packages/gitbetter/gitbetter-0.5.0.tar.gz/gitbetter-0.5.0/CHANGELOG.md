# Changelog

## 0.4.0 (2023-05-04)

#### New Features

* add status command


## v0.3.0 (2023-05-02)

#### Refactorings

* remove do_cmd as it's now covered by parent class's do_sys
#### Others

* build v0.3.0
* update changelog


## v0.2.0 (2023-05-02)

#### New Features

* override do_help to display unrecognized_command_behavior_status after standard help message
* add functionality to toggle unrecognized command behavior
* add default override to execute line as system command when unrecognized
* display current working directory in prompt
#### Fixes

* set requires-python to >=3.10
#### Refactorings

* remove cwd command
#### Docs

* update readme
#### Others

* build v0.2.0
* update changelog


## v0.1.1 (2023-04-30)

#### Fixes

* cast Pathier objects to strings in recurse_files()
#### Others

* build v0.1.1
* update changelog


## v0.1.0 (2023-04-30)

#### New Features

* add do_cmd() to excute shell commands without quitting gitbetter
* enclose 'message' in quotes if you forget them
#### Refactorings

* rename some functions
#### Docs

* update readme
* add future feature to list in readme
#### Others

* build v0.1.0
* update changelog


## v0.0.0 (2023-04-29)
