from typing import List
from llama.program.util.run_ai import query_run_program

from llama.types.base_specification import BaseSpecification
from llama.program.util.run_ai import query_submit_program_to_batch
from llama.program.util.run_ai import query_check_llama_program_status
from llama.program.util.run_ai import query_get_llama_program_result
from llama.program.util.run_ai import query_cancel_llama_program
from llama.program.util.run_ai import query_submit_finetune_job


class Value(object):
    def __init__(self, type, data=None):
        self._type = type
        self._data = data
        self._function = None
        self._index = None

    def _get_field(self, name):
        if self._data is None:
            raise Exception("Value Access Error: must compute value before acessing")

        return self._data._get_attribute_raw(name)

    def __str__(self):
        if self._data is None:
            raise Exception("Value Access Error: must compute value before acessing")

        return str(self._data)

    def __int__(self):
        if self._data is None:
            raise Exception("Value Access Error: must compute value before acessing")

        return int(self._data)

    def __float__(self):
        if self._data is None:
            raise Exception("Value Access Error: must compute value before acessing")

        return float(self._data)

    def __gt__(self, other):
        if self._data is None:
            raise Exception("Value Access Error: must compute value before acessing")

        if isinstance(other, Value):
            other = other._get_data()

        return self._data > other

    def _get_data(self):
        if self._data is None:
            raise Exception("Value Access Error: must compute value before acessing")

        return self._data

    def __repr__(self):
        return str(self)

    def _compute_value(self):
        # check in the builper value cache
        if self._index in self._function.program.builder.value_cache:
            returned_value = self._function.program.builder.value_cache[self._index][
                "data"
            ]
        else:
            params = {
                "program": self._function.program.to_dict(),
                "requested_values": [self._index],
            }
            response = query_run_program(params)

            response.raise_for_status()

            # update the cache
            self._function.program.builder.value_cache.update(response.json())

            returned_value = response.json()[str(self._index)]["data"]

        if issubclass(self._type, BaseSpecification):
            self._data = self._type.parse_obj(returned_value)
        else:
            self._data = self._type(returned_value)

    def __getattribute__(self, name):
        if name.find("_") == 0:
            return super().__getattribute__(name)

        return self._function.program.builder.get_field(self, name)

    def _get_attribute_raw(self, name):
        return super().__getattribute__(name)


def gen_queue_batch(values: List[Value]):
    # Assume that all values have the same program
    program = values[0]._function.program.to_dict()
    params = {
        "program": program,
        "requested_values": [v._index for v in values],
    }
    response = query_submit_program_to_batch(params)
    response.raise_for_status()
    return response.json()


def gen_submit_training_job(model_name, data, input_type, output_type):
    params = {
        "model_name": model_name,
        "dataset": data,
        "input_type": input_type,
        "output_type": output_type,
    }
    response = query_submit_finetune_job(params)
    response.raise_for_status()
    return response.json()


def gen_check_job_status(job_id: str):
    # Assume that all values have the same program
    params = {
        "job_id": job_id,
    }
    response = query_check_llama_program_status(params)
    response.raise_for_status()
    return response.json()


def gen_job_results(job_id: str, output_type):
    # Assume that all values have the same program
    params = {
        "job_id": job_id,
    }
    response = query_get_llama_program_result(params)
    response.raise_for_status()
    response = response.json()
    if "Error" in response:
        return response
    outputs = []
    for key, val in response.items():
        data = val["data"]
        for d in data:
            obj = output_type.parse_obj(d)
            outputs.append(obj)
    if len(outputs) == 1:
        return outputs[0]
    return outputs


def gen_cancel_job(job_id: str):
    # Assume that all values have the same program
    params = {
        "job_id": job_id,
    }
    response = query_cancel_llama_program(params)
    response.raise_for_status()
    return response.json()


def gen_multiple_values(values: List[Value]):
    # Assume that all values have the same program
    program = values[0]._function.program.to_dict()
    params = {
        "program": program,
        "requested_values": [v._index for v in values],
    }
    response = query_run_program(params)
    response.raise_for_status()
    for i, v in enumerate(values):
        index = v._index
        response_val = response.json()[str(index)]
        if isinstance(response_val["data"], list):
            v._data = []
            for d in response_val["data"]:
                v._data.append(v._type.parse_obj(d))
        else:
            v._data = v._type.parse_obj(response_val["data"])
    # Update cache once
    values[0]._function.program.builder.value_cache.update(response.json())
    return [value._data for value in values]


def gen_value(value: Value):
    value._compute_value()
    return value._data
