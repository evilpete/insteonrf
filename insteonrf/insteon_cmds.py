
bc_ext_cmd_list = {
    0x00  : { "label" : "Reserved" }, 
    "label" : "Reserved",
}
bc_sd_cmd_list = {
    0x01 : { "label" : "Set Button Press Responder" }, #  cmd2 = 0xFF
    0x02 : { "label" : "Set Button Press Controller" }, #  cmd2 = 0xFF
    0x03 : { "label" : "Test Powerline Phase" ,
                "subcmd" : {
                    0x00 : "Test Powerline Phase A",
                    0x01 : "Test Powerline Phase A",
                }
            },
    0x02 : { "label" : "Heartbeat Button Press Controller" }, #  cmd2 = Battery Level 0x00 -> 0xff

    0x11 : { "label" : "On Recall" },
    0x12 : { "label" : "Alias 2 High" },
    0x13 : { "label" : "Alias 1 Low" },
    0x14 : { "label" : "Alias 2 Low" },
    0x15 : { "label" : "Alias 3 High" },
    0x16 : { "label" : "Alias 3 Low" },
    0x17 : { "label" : "Alias 4 High" },
    0x18 : { "label" : "Alias 4 Low" },
    0x25 : { "label" : "Alias 5 High" },

    0x27 : { "label" : "Device Status Changed" }, #  cmd2 = 0xFF
    0x49 : { "label" : "SALad Debug Report" }, #  cmd2 = 0xFF
    "label" : "Broadcast Std Command",
}

sd_cmd_list = {
    0x01 : { "label" : "Assign to Group" }, #  cmd2 = group number
    0x02 : { "label" : "Delete from Group" }, #  cmd2 = group number
    0x03 : { "label" : "Product Data Request" }, #  returns extended message. cmd2 = 0 for data request, 1 for FX username, 2 for text string
    0x09 : { "label" : "Enter Link Mode" }, #  cmd2 = group number
    0x0A : { "label" : "Enter Unlink Mode" }, #  cmd2 = group number
    0x0D : { "label" : "Get Insteon Engine Version" }, #  cmd2 = returns 0x00 for i1 or 0x01 for i2
    0x0F : { "label" : "Ping" },
    0x10 : { "label" : "ID Request" }, #  Older devices may go into linking mode, newer ones not. Identifies self with set-button-pressed broadcast.
    0x11 : { "label" : "On" },
    0x12 : { "label" : "Fast On" },
    0x13 : { "label" : "Off" },
    0x14 : { "label" : "Fast Off" },
    0x15 : { "label" : "Bright One Step" }, #  32 steps from on to off
    0x16 : { "label" : "Dim One Step" },
    0x17 : { "label" : "Start Manual Change", #  bright/dim until Stop Manual Change received. cmd2 = 1 for bright, 0 for dim
                "subcmd" : {
                    0x00 : "Dim",
                    0x01 : "Bright",
                }
            },
    0x18 : { "label" : "Stop Manual Change" },
    0x19 : { "label" : "Status Request"},
    0x1F : { "label" : "Get Operating Flags" },
    0x20 : { "label" : "Set Operating Flags",
                "subcmd" : {
                    0x00 : "Program Lock On",
                    0x01 : "Program Lock Off",
                    0x02 : "LED Enabled",
                    0x03 : "LED Off",
                    0x04 : "Beeper Enabled",
                    0x05 : "Beeper Off",

                    0x06 : "Stay Awake On",
                    0x07 : "Stay Awake Off",

                    0x08 : "Listen Only On",
                    0x09 : "Listen Only Off",

                    0x0A : "No I'm Alive On",
                    0x0B : "No I'm Alive Off",

                    0x05 : "Set ALL-Link Command Alias Extended Data",
                }
            },

    0x21 : { "label" : "Light Instant Change" },
    0x22 : { "label" : "Light Manually Turned Off" },
    0x23 : { "label" : "Light Manually Turned On" },
    0x25 : { "label" : "Remote Set Button Tap", #  command2 = number of taps (1 or 2)
                "subcmd" : {
                    0x01 : "1 Tap",
                    0x02 : "2 Tap",
                    }
                },
    0x27 : { "label" : "Light Set Status" },
    0x28 : { "label" : "Set MSB for Peek/Poke" },
    0x29 : { "label" : "Poke EE" },
    0x2B : { "label" : "Peek" },
    0x2E : { "label" : "Light On at Rate" }, #  cmd2 - bits 0-3 = 2xRamp Rate +1, Bits 4-7 = On Level + 0x0F
    0x2F : { "label" : "Light Off at Rate" }, #  cmd2 - as above but ramp rate = 0 regardless of value sent
    0x30 : { "label" : "Beep"}, 
    0x45 : { "label" : "Output ON (EZIO)" }, #  cmd2 = output #
    0x46 : { "label" : "Output OFF (EZIO)" }, #  cmd2 = output #
    0x48 : { "label" : "Write Output Port (EZIO)" }, #  cmd2 = value
    0x49 : { "label" : "Read Output Port (EZIO)" },
    0x4A : { "label" : "Get Sensor Value (EZIO)" },
    0x4B : { "label" : "Set Sensor 1 OFF->ON Alarm" },
    0x4C : { "label" : "Set Sensor 1 ON->OFF Alarm" },
    0x4D : { "label" : "Write Configuration Port (EZIO)" },
    0x4E : { "label" : "Read Configuration Port (EZIO)" },
    0x4F : { "label" : "EZIO Control (EZIO)" },
    0x80 : { "label" : "Reserved" },
    0x81 : { "label" : "Assign to Companion Group" },
    "label" : "Std Command",
}


ext_cmd_list = {
    0x03 : { "label" : "Data Response",
                "subcmd" : {
                    0x00 : "Product Data Response",
                    0x01 : "FX Username Response",
                    0x02 : "Device Text String Response",
                    0x03 : "Set Device Text String",
                    0x04 : "Set ALL-Link Command Alias",
                    0x05 : "Set ALL-Link Command Alias Extended Data",
                }
            },

    0x2A : { "label" : "Block Data Transfer",
                "subcmd" : {
                    0x00 : "Transfer Failure",
                    0x01 : "Transfer Complete,",
                    0x02 : "Transfer Complete",
                    0x03 : "Transfer Complete",
                    0x04 : "Transfer Complete",
                    0x05 : "Transfer Complete",
                    0x06 : "Transfer Complete",
                    0x07 : "Transfer Complete",
                    0x08 : "Transfer Complete",
                    0x09 : "Transfer Complete",
                    0x0A : "Transfer Complete",
                    0x0B : "Transfer Complete",
                    0x0C : "Transfer Complete",
                    0x0D : "Transfer Continues",
                    0xFF : "Request Block Data Transfer",
                },
            },
    0x2E : { "label" : "Extended Set/Get" },
    0x2F : { "label" : "Read/Write ALL-Link Database (ALDB)" },
    0x30 : { "label" : "Trigger ALL-Link Command" },
    0x4B : { "label" : "I/O Set Sensor Normal" },
    0x4C : { "label" : "I/O Alarm Data Responce" },
    0xF0 : { "label" : "FX User-specific Command" },
    0xF1 : { "label" : "FX User-specific Command" },
    0xF2 : { "label" : "FX User-specific Command" },
    0xF3 : { "label" : "FX User-specific Command" },
    0xF4 : { "label" : "FX User-specific Command" },
    0xF5 : { "label" : "FX User-specific Command" },
    0xF6 : { "label" : "FX User-specific Command" },
    0xF7 : { "label" : "FX User-specific Command" },
    0xF8 : { "label" : "FX User-specific Command" },
    0xF9 : { "label" : "FX User-specific Command" },
    0xFA : { "label" : "FX User-specific Command" },
    0xFB : { "label" : "FX User-specific Command" },
    0xFC : { "label" : "FX User-specific Command" },
    0xFD : { "label" : "FX User-specific Command" },
    0xFE : { "label" : "FX User-specific Command" },
    0xFF : { "label" : "FX User-specific Command" },
    "label" : "Extended Command",
}
