from dataclasses import dataclass, field


class Builder:
    """A builder class that creates instances of a given dataclass model and sets values
    for its non-private fields through dynamically created setter methods.
    """

    def __init__(self, model) -> None:
        self.model = dataclass(model)
        self.instance = None

    def __call__(self):
        """Creates an instance of the dataclass model and sets its non-private fields using
        dynamically created setter methods.

        Returns:
            The created instance of the dataclass model.
        """
        self.instance = self.model()
        self.add_setters()
        self.instance.setup()
        return self.instance

    def add_setters(self) -> None:
        """Adds setter methods to the instance of the dataclass model for each of its
        non-private fields.
        """
        keys = [
            {"name": field.name, "type": field.type}
            for field in self.model.__dataclass_fields__.values()
            if field.name[0] != "_"
        ]

        for key in keys:
            name: str = key["name"].replace("_", " ").title().replace(" ", "")
            setattr(self.instance, f"set{name}", self.func(key))

    def func(self, key):
        """Returns a setter function for a given field.

        Parameters:
            key: The name and type of the field.

        Returns:
            A setter function that sets the value of the field in the instance of the dataclass model and returns the instance.
        """

        def ex(value):
            setattr(self.instance, key["name"], value)
            return self.instance

        return ex
