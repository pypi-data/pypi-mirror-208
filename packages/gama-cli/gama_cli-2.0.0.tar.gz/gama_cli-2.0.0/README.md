# GAMA CLI

![GAMA CLI](./docs/gama_cli.png)

Publicly available on [PyPi](https://pypi.org/project/gama-cli/) for convenience but if you don't work at Greenroom Robotics, you probably don't want to use this.

## Install

* For development:
  * `pip install -e ./libs/gama_config`
  * `pip install -e ./tools/gama_cli`
* For production: `pip install gama-cli`
* You may also need to `export PATH=$PATH:~/.local/bin` if you don't have `~/.local/bin` in your path
* Install autocomplete:
  * bash: `echo 'eval "$(_GAMA_CLI_COMPLETE=bash_source gama_cli)"' >> ~/.bashrc`
  * zsh: `echo 'eval "$(_GAMA_CLI_COMPLETE=zsh_source gama_cli)"' >> ~/.zshrc` (this is much nicer)

## Usage

* `gama_cli --help` to get help with the CLI

### Groundstation

Installing a GAMA on a groundstation is as simple as this:

* `mkdir ~/gama && cd ~/gama`
* `gama_cli authenticate` to authenticate with the GAMA package registry
* `gama_cli gs configure` to configure GAMA on a groundstation
* `gama_cli gs install` to install GAMA on a groundstation
* `gama_cli gs up` to start GAMA on a groundstation
* `gama_cli gs down` to stop GAMA on a groundstation

### Vessel

Installing a GAMA on a vessel is as simple as this:

* `mkdir ~/gama && cd ~/gama`
* `gama_cli authenticate` to authenticate with the GAMA package registry
* `gama_cli vessel configure` to configure GAMA on a vessel
* `gama_cli vessel install` to install GAMA on a vessel
* `gama_cli vessel up` to start GAMA on a vessel
* `gama_cli vessel down` to stop GAMA on a vessel

## Dev mode

GAMA CLI can be ran in dev mode. This will happen if it is installed with `pip install -e ./tools/gama_cli` or if the environment variable `GAMA_CLI_DEV_MODE` is set to `true`.