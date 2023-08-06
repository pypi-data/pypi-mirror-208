from llama.program.program import Program
from llama.program.function import Function
from llama.program.util.config import edit_config
from llama.program.util.run_ai import (
    query_run_program,
    fuzzy_is_duplicate,
    query_run_embedding,
)

from llama.types.type import Type

from llama.program.operations.llama_operation import LlamaOperation
from llama.program.operations.batch_llama_operation import BatchLlamaOperation
from llama.program.operations.metric_operation import MetricOperation
from llama.program.operations.call_operation import CallOperation
from llama.program.operations.get_element_operation import GetElementOperation
from llama.program.operations.get_field_operation import GetFieldOperation
from llama.program.operations.return_operation import ReturnOperation
from llama.program.operations.feedback_operation import FeedbackOperation
from llama.program.value import gen_value as run
from llama.program.value import gen_multiple_values as run_all
from llama.program.value import gen_queue_batch, gen_check_job_status, gen_job_results
from llama.program.value import gen_cancel_job
from llama.program.value import gen_submit_training_job

import inspect


class Builder:
    """Build a program for execution by the Llama large language model engine."""

    def __init__(self, name, model_name=None, config={}):
        self.program = Program(self, name)
        self.current_function = self.program.main
        self.value_cache = {}
        self.model_name = model_name
        edit_config(config)

    def __call__(self, input, output_type, *args, **kwargs):
        if isinstance(input, list):
            values = self.add_model(input, output_type, *args, **kwargs)
            results = run_all(values)
            if isinstance(results[0], list):
                return [value for sublist in results for value in sublist]
            return results
        else:
            value = self.add_model(input, output_type, *args, **kwargs)
            return run(value)

    def add_model(self, input, output_type, *args, **kwargs):
        if isinstance(input, list):

            def partition(l, n):
                for i in range(0, len(l), n):
                    yield l[i : i + n]

            chunks = list(partition(input, 20))
            if self.model_name is not None:
                kwargs["model_name"] = self.model_name
            operations = []
            for chunk in chunks:
                new_operation = self.current_function.add_operation(
                    BatchLlamaOperation(chunk, output_type, *args, **kwargs)
                )
                operations.append(new_operation)
            return operations
        else:
            if self.model_name is not None:
                kwargs["model_name"] = self.model_name
            new_operation = self.current_function.add_operation(
                LlamaOperation(input, output_type, *args, **kwargs)
            )
            return new_operation

    def submit_job(self, input, output_type, *args, **kwargs):
        if isinstance(input, list):
            values = self.add_model(input, output_type, *args, **kwargs)
            results = gen_queue_batch(values)
            return results
        else:
            new_input = [input]
            values = self.add_model(new_input, output_type, *args, **kwargs)
            results = gen_queue_batch(values)
            return results

    def submit_training_job(self, input_type, output_type, data):
        results = gen_submit_training_job(
            self.model_name, data, input_type, output_type
        )
        return results

    def check_job_status(self, job_id):
        status = gen_check_job_status(job_id)
        return status

    def get_job_results(self, job_id, output_type):
        results = gen_job_results(job_id, output_type)
        return results

    def cancel_job(
        self,
        job_id,
    ):
        results = gen_cancel_job(job_id)
        return results

    def sample(self, input, output_type, n=1, max_similarity=0.99, *args, **kwargs):
        input_value = input
        if self.model_name is not None:
            kwargs["model_name"] = self.model_name
        new_operations = []
        cache_len = 5  # NOTE: should use actual cache length
        max_iter = cache_len
        temperature = 0.7  # NOTE: should use actual random temperature
        random = True
        attributes = [
            attribute
            for attribute, field in output_type.__fields__.items()
            if field.type_ == str
        ]
        attribute_embeddings = {attribute: [None, []] for attribute in attributes}
        for i in range(n):
            new_operation = None
            attribute_embeddings = {
                attribute: [None, embeddings[1]]
                for attribute, embeddings in attribute_embeddings.items()
            }
            j = 0
            while any(
                [
                    fuzzy_is_duplicate(
                        attribute_embedding,
                        attribute_reference_embeddings,
                        max_similarity,
                    )
                    for attribute_embedding, attribute_reference_embeddings in attribute_embeddings.values()
                ]
            ) or fuzzy_is_duplicate(
                list(attribute_embeddings.values())[0][0],
                [
                    attribute_embedding
                    for attribute_embedding, _ in list(attribute_embeddings.values())[
                        1:
                    ]
                ],
                max_similarity,
            ):
                if j == max_iter:
                    max_iter += cache_len
                    random = False
                    temperature += 0.1  # NOTE: this could be set differently
                new_operation = self.current_function.add_operation(
                    LlamaOperation(
                        input_value,
                        output_type,
                        random=random,
                        temperature=temperature,
                        *args,
                        **kwargs,
                    )
                )
                new_operation = run(new_operation)
                for attribute in attributes:
                    attribute_embeddings[attribute][0] = query_run_embedding(
                        getattr(new_operation, attribute)
                    )
                j += 1
            if j == max_iter:
                continue
            for (
                attribute_embedding,
                attribute_reference_embeddings,
            ) in attribute_embeddings.values():
                attribute_reference_embeddings.append(attribute_embedding)
            if not new_operation:
                new_operation = self.current_function.add_operation(
                    LlamaOperation(
                        input_value,
                        output_type,
                        random=random,
                        temperature=temperature,
                        *args,
                        **kwargs,
                    )
                )
                new_operation = run(new_operation)
            new_operations.append(new_operation)

        return new_operations

    def fit(self, examples=[]):
        self.add_data(examples)

    def add_data(self, data=[]):
        self.program.add_data(examples=data)

    def improve(
        self,
        on: str,
        to: str,
        good_examples=[],
        bad_examples=[],
        temperature=0.0,
        version="",
    ):
        new_operation = self.current_function.add_operation(
            FeedbackOperation(
                on=on,
                to=to,
                good_examples=good_examples,
                bad_examples=bad_examples,
                temperature=temperature,
                version=version,
            )
        )

        return new_operation

    def function(self, function):
        signature = inspect.signature(function)
        input_types = [value.annotation for value in signature.parameters.values()]

        main = self.current_function
        new_function = Function(
            program=self.program, name=function.__name__, input_arguments=input_types
        )
        self.program.functions[new_function.name] = new_function
        self.current_function = new_function
        output_value = function(*new_function.operations)
        self.current_function.add_operation(ReturnOperation(output_value))
        self.current_function = main

        return Lambda(self, new_function, output_value)

    def parallel(self, function):
        return self.function(function=function)

    def add_call(self, function, input_value, output_value):
        new_operation = self.current_function.add_operation(
            CallOperation(function, input_value, output_value)
        )

        result = new_operation

        if isinstance(output_value, tuple):
            result = []

            for index, value in enumerate(output_value):
                result.append(
                    self.current_function.add_operation(
                        GetElementOperation(new_operation, value.type, index)
                    )
                )

        return result

    def get_field(self, value, field_name):
        return self.current_function.add_operation(
            GetFieldOperation(
                value, value._type._get_field_type(field_name), field_name
            )
        )

    def add_metric(self, metric):
        new_operation = self.current_function.add_operation(
            MetricOperation(metric.input, metric.get_metric_type())
        )

        return new_operation

    def make_metric(
        self, input: Type, metric_type: type, fit: bool = True, higher_is_better=True
    ):
        new_operation = self.current_function.add_operation(
            MetricOperation(input, metric_type)
        )

        return new_operation

    def metrics(self):
        requested_values = [
            op._index for op in self.program.functions["main"].operations
        ]

        params = {
            "program": self.program.to_dict(),
            "requested_values": requested_values,
        }
        response = query_run_program(params)
        response.raise_for_status()

        data = [response[str(index)]["data"] for index in requested_values]

        return data


class Lambda:
    def __init__(self, builder: Builder, function: Function, output_value: Type):
        self.output_value = output_value
        self.builder = builder
        self.function = function

    def __call__(self, *args, **kwargs):
        input_value = self._get_input(*args, **kwargs)
        return self.builder.add_call(self.function, input_value, self.output_value)

    def _get_input(self, *args, **kwargs):
        # TODO: support more than one input LLM arg

        if len(args) > 0:
            return args[0]

        return next(iter(kwargs.values()))
