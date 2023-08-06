import uuid

from .api_dto import ApiDto
from enum import Enum


class StepType(Enum):
    QUERY = 'query'
    SCRIPT = 'script'
    MODEL = 'model'


class PipelineStep(ApiDto):
    """
    Step of a pipeline.
    """

    def __init__(self,
                 step_id: uuid.UUID = None,
                 step_type: StepType = None,
                 config=None,
                 inputs=None,
                 outputs=None):

        if outputs is None:
            outputs = []
        if step_id is None:
            step_id = uuid.uuid4()
        self.step_id = step_id
        self.step_type = step_type
        self.config = config
        self.inputs = inputs
        self.outputs = outputs

    def from_json(self, obj):
        """
        load from JSON dictionary representation
        """
        if "id" in obj.keys():
            self.step_id = uuid.UUID(obj["id"])

        if "type" in obj.keys():
            if obj["type"] in ['query', 'script', 'model']:
                self.step_type = obj["type"]
            else:
                raise TypeError(f'unsupported step type {obj["type"]}')
        if "config" in obj.keys():
            self.config = obj['config']
        self.inputs = []
        if "inputs" in obj.keys():
            for step_input in obj["inputs"]:
                if isinstance(step_input, str):
                    self.inputs.append(step_input)
                else:
                    raise TypeError(f'unsupported input type {step_input.__class__.__name__}')

        self.outputs = []
        if "outputs" in obj.keys():
            for step_output in obj["outputs"]:
                if isinstance(step_output, str):
                    self.outputs.append(step_output)
                else:
                    raise TypeError(f'unsupported output type {step_output.__class__.__name__}')


class Pipeline(ApiDto):

    def __init__(self,
                 pipeline_id: uuid.UUID = None,
                 key: str = None,
                 variables: dict = None,
                 steps: [] = None):

        if pipeline_id is None:
            pipeline_id = uuid.uuid4()
        self.pipeline_id = pipeline_id
        self.key = key
        self.variables = variables
        if steps is not None:
            for step in steps:
                if not isinstance(step, PipelineStep):
                    raise TypeError(f'step expected PipelineStep but received {step.__class__.__name__}')
            self.steps = steps
        else:
            self.steps = []

    def check_path(self) -> bool:
        """
        validate that steps create a valid path.
        return true if path is valid, otherwise raise errors
        """
        steps_to_follow = self._initial_steps()
        if len(steps_to_follow) == 0:
            raise ValueError('path does not contains any initial steps producing outputs')

        followed = []  # all steps already followed
        produced = []  # all outputs already produced

        while len(steps_to_follow) > 0:
            for step in steps_to_follow:
                self._follow_step(step, followed, produced)
            steps_to_follow = []
            if len(followed) < len(self.steps):
                steps_to_follow = self._next_steps(followed, produced)

        if len(followed) == len(self.steps):
            return True
        else:
            raise RuntimeError(f'missing {len(self.steps)-len(followed)} step(s) that could not be followed')

    def _follow_step(self,
                     step: PipelineStep,
                     followed: list,
                     produced: list):
        """
        simulate that step have been followed.

        """
        if step in followed:
            raise RuntimeError(f'path cannot pass two times through same step {step.step_id}')
        followed.append(step)
        for output in step.outputs:
            if output in produced:
                raise RuntimeError(f'output {output} is already produced.')
            produced.append(output)

    def _initial_steps(self):
        """
        find initials steps (no input at least one output).
        :return: initial steps.
        """
        initial_steps = []
        step: PipelineStep
        for step in self.steps:
            if len(step.inputs) == 0 and len(step.outputs) > 0:
                initial_steps.append(step)
        return initial_steps

    def _next_steps(self, followed, produced):
        """
        find all next steps that are ready to be executed
        """
        next_steps = []
        step: PipelineStep
        for step in self.steps:
            if all(s_input in produced for s_input in step.inputs) and step not in followed:
                next_steps.append(step)
        return next_steps

    def from_json(self, obj):
        """
        load from JSON dictionary representation
        """
        if "id" in obj.keys():
            self.pipeline_id = uuid.UUID(obj["id"])
        if "key" in obj.keys():
            self.key = str(obj['key'])
        if "variables" in obj.keys():
            self.variables = obj['variables']
        if "steps" in obj.keys():
            for obj_step in obj["steps"]:
                step = PipelineStep()
                step.from_json(obj_step)
                self.steps.append(step)



