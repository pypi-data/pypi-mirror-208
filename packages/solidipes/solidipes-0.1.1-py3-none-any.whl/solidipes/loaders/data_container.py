def wrap_errors(func):
    def foo(self, *args, **kwargs):
        try:
            return func(self, *args, **kwargs)
        except Exception as e:
            self.errors.append(str(e))

    return foo


################################################################


class DataContainer:
    """Container class for other structured data containers"""

    def __init__(self, initial_data={}):
        self.name = ""
        #: Dictionnary of other DataContainer or arbitrary objects.
        #: Set entry to "None" to mark as loadable.
        self._data_collection = initial_data.copy()
        #: Default viewer for this file. Optionally override this in
        #: subclasses.
        self.default_viewer = None

        #: stores the error messages during loading
        self.errors = []

    def valid_loading(self):
        if self.errors:
            return False
        return True

    def copy(self):
        """Returns a shallow copy without the need to read from disk again"""
        cls = self.__class__
        new = cls.__new__(cls)
        new.__dict__.update(self.__dict__)
        new._data_collection = self._data_collection.copy()
        return new

    @property
    def data_info(self):
        """Returns a multi-line string with information about data keys"""
        info_list = []

        for key, data in self._data_collection.items():
            if data is None:
                info_list.append(f"{key}: Not loaded")
            else:
                info_list.append(f"{key}: {type(self._data_collection[key])}")

        return "\n".join(info_list)

    @property
    def data(self):
        """Load all data if necessary and return it

        Accessing this property for the first time will load the data.
        If self.__loaded_data has only one entry, returns it directly.

        Override the _load_data method in subclasses to define how data is
        loaded or built using other data containers.
        """
        self.load_all()

        # Return data
        if len(self._data_collection) == 1:
            return list(self._data_collection.values())[0]
        else:
            return self._data_collection

    def _load_data(self, key):
        """Load data or build sub-data dictionary and return it

        Override this method in subclasses to define how data is loaded or
        built.
        """
        return None

    @wrap_errors
    def load_all(self):
        """Load all data"""
        # Find keys that have a None value and load them
        for key in self._data_collection:
            if self._data_collection[key] is None:
                # Trigger loading of data
                self.get(key)

    def add(self, key, data=None):
        """Add an arbitrary object to the data collection"""
        self._data_collection[key] = data

    def get(self, key):
        """Get a data object by key, loading it if necessary"""
        try:
            data = self._data_collection[key]
        except KeyError as e:
            raise KeyError(str(e) + "\n" + f"for {type(self)}, " + f"possible keys are {self._data_collection.keys()}")
            raise e

        # Load data
        if data is None:
            data = self._load_data(key)
            if data is None:
                raise Exception(f'Data "{key}" could not be loaded')
            self._data_collection[key] = data

        return data

    def remove(self, key):
        """Remove a data object from the data collection"""
        del self._data_collection[key]

    def has(self, key):
        """Check if data is available in this container"""
        return key in self._data_collection

    def __getattr__(self, name):
        """Get a data object by key, loading it if necessary

        Only works if the name is not already an attribute of this class.
        """
        return self.get(name)

    def view(self, **kwargs):
        """View the file using the default viewer"""

        if self.default_viewer is None:
            raise Exception("This File cannot be viewed directly. Use get_data to get a Dataobject.")
        viewer = self.default_viewer(self, **kwargs)
        return viewer

    def __str__(self):
        return self.__class__.__name__
