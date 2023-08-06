def exclusive_select(button, button_group):
    for bt in button_group.buttons():
        if bt is not button:
            bt.setChecked(False)
