class WizardStep:

    def __init__(self, step_id, order: int):
        self.step_id = step_id
        self.order = order


class WizardFunction:

    def __init__(self, title, function, is_beta=False, restricted_domain=None):
        self.title = title
        self.function = function
        self.restricted_domain = restricted_domain
        self.is_beta = is_beta
        self.steps = []

    def append_step(self, step: WizardStep):
        self.steps.append(step)
