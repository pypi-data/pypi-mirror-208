from pyntcli.ui import ui_thread

def unexpected_error():
    ui_thread.print(ui_thread.PrinterText("An Unexpected Error Occurred",style=ui_thread.PrinterText.WARNING) \
                        .with_line("") \
                            .with_line("Please tell us about it in our community channel and we will help you figure it out:",style=ui_thread.PrinterText.HEADER) \
                                .with_line("https://join.slack.com/t/pynt-community/shared_invite/zt-1mvacojz5-WNjbH4HN8iksmKpCLTxOiQ",style=ui_thread.PrinterText.HEADER))