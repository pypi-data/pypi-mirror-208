import logging

from numerous.image_tools.app import run_job
from numerous.image_tools.job import NumerousSimulationJob

logger = logging.getLogger("multiply-by-two")

#  Creates the MultiplyByTwoJob inheriting the NumerousSimulationJob, which uses the standard work-flow of reading data,
#  stepping the model by calculating new states, outputs, and the next time step, and saves these outputs to numerous.


class MultiplyByTwoJob(NumerousSimulationJob):
    def __init__(self):
        super(MultiplyByTwoJob, self).__init__()

    def initialize_simulation_system(self):
        self.numerous_name = "example"
        # Set align_outputs_to_next_timestep to False, when outputs are to be aligned to the current timestep in the
        # step() method
        self.align_outputs_to_next_timestep = False

    """
    The step method is called each time the inputs have been read, and must return the next timestep and the outputs,
    which is a dictionary formatted as {tag1: value1, tag2: value2...}
    """

    def step(self, t: float, dt: float) -> tuple[float, dict]:
        component = self.system.components[
            self.numerous_name
        ]  # Get the component named 'example' from the frontend
        inputs = (
            component.inputs
        )  # This dict contains the inputs to the named component
        model = (
            component.model
        )  # This allows the user to access the user instantiated python model class
        outputs = model.multiply_by_two(inputs, t)  # a dict with outputs
        # we can add more outputs.. for example output resumed True if job is resumed
        outputs.update({"resumed": len(self.system.states) > 0})
        # Finally return the next timestep (t+dt) and the outputs. The outputs are timestamped with the current
        # timestep (t), because of the 'align_outputs_to_next_timestep = False' set above.
        return t + dt, outputs

    # you can save states, by defining the serialize_states. This way you can resume a stateful model.
    def serialize_states(self, t: float) -> bool:
        return True


def run_example():
    run_job(
        numerous_job=MultiplyByTwoJob(),
        appname="multiply-by-two",
        model_folder="numerous.image_tools.example_models",
    )


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    run_example()
