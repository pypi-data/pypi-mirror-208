# DEPRECATED - OVOS PHAL CONFIGURATION PROVIDER


This repository is no longer maintained by OpenVoiceOS, use https://github.com/OpenVoiceOS/ovos-gui-plugin-shell-companion instead

___________________________


The Configuration Provider plugin provides an interface to generate GUI compatible configuration sections for mycroft advanced configuration

# Requirements
- This plugin has not external requirements

# Install
`pip install ovos-PHAL-plugin-configuration-provider`

# Event Details:

##### List / Display Groups

Event for listing available groups in the GUI list interface

``` python
    # type: request
    # ovos.phal.configuration.provider.list.groups
```

##### Get Settings For Groups

Get GUI compatible configuration display for specific group

``` python
    # type: request
    # ovos.phal.configuration.provider.get
```

##### Set Settings For Groups

Set Core compatible configuration for specific group

``` python
    # type: request
    # ovos.phal.configuration.provider.set
```
