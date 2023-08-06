class DependencyError(RuntimeError):
    """ Dependency Error

        This is used when optional dependencies are required, but it may not be installed.
    """
    def __init__(self, *package_names: str):
        super().__init__()
        self.__package_names = package_names

    def __str__(self):
        install_cmd = ' '.join(['pip3', 'install', *self.__package_names])
        return f'Optional dependencies are now required at this point. Please run "{install_cmd}" to install them.'
