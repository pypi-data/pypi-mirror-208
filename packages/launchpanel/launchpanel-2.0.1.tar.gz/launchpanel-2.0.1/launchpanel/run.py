

# ------------------------------------------------------------------------------
if __name__ == '__main__':
    import launchpanel

    args, kwargs = launchpanel.utils.format_sys_argv()

    # -- Launch the panel window with the given arguments
    launchpanel.launch(
        *args,
        **kwargs
    )
