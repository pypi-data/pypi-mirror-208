"""
This model takes input and returns an output multiplied by 2.
"""


def entrypoint(tag, system):
    class Model:
        def multiply_by_two(self, data, t):
            v = data.get("input1")
            output = {f"{tag}_output1": v * 2}
            return output

    return Model()
