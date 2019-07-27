# pyjvcpj

A python API for network control of a JVC projector as per http://support.jvc.com/consumer/support/documents/DILAremoteControlGuide.pdf

Supports the JVC N5/7/9 range only

# Config

Run the app and then edit the generated config file (in $HOME/.pyjvcpj/pyjvcpj.yaml)
 
make sure to see an IP address to your PJ
macros of multiple commands can be defined in config

# API

Exposes an API over HTTP via

GET /api/1/info
GET /api/1/pj/:command
PUT /api/1/pj/

Get info to show all the supported commands
Get pj/:command to issue a read only command to get a response from some particular command
Put a json payload to pj to issue a command, expected payload is a list of commands e.g.

    ["Power.PowerState.Standby"]
    
will put the PJ into standby. This equates to jvccommands.Command.Power with an argument of type PowerState with a value of Standby

alternatively

    ["ColorTemperatureGainBlue.Numeric.100"]
    
equates to jvccommands.Command.ColorTemperatueGainBlue with an argument of type Numeric and a value of 100

This information is supplied via the info endpoint as it equates to command_name.value_type.value
