from llama.program.function import Function
from llama.program.util.type_to_dict import value_to_dict


class Program:
    """Internal representation of a program that can be executed by the Llama
    large language model engine.

    Each program has a unique name (within your account).

    """

    def __init__(self, builder, name):
        self.builder = builder
        self.name = name
        self.main = Function(program=self, name="main")
        self.functions = {"main": self.main}
        self.examples = []

    def add_data(self, examples):
        if isinstance(examples, list):
            self.examples.extend(examples)
        else:
            # singleton
            self.examples.append(examples)

    def add_metric(self, metric):
        self.add_operation(metric)

    def to_dict(self):
        examples = []
        for example in self.examples:
            if isinstance(example, list):
                # Related information in a list together
                examples_i = []
                for example_i in example:
                    examples_i.append(value_to_dict(example_i))
                examples.append(examples_i)
            else:
                # Singleton type
                examples.append(value_to_dict(example))
        dict_object = {
            "name": self.name,
            "functions": {
                name: function.to_dict() for name, function in self.functions.items()
            },
            "examples": examples,
        }
        return dict_object
