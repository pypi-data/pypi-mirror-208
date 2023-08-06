from dataclasses import dataclass
from bytez.tasks.language_modelling._models.hazyresearch_h3 import HazyresearchH3Model


@dataclass
class LanguageModellingModels:
    hazyresearch_h3 = HazyresearchH3Model().inference