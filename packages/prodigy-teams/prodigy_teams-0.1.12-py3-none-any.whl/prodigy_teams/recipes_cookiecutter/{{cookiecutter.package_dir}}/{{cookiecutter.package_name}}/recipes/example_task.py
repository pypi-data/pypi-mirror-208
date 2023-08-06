from typing import Literal

from prodigy.types import RecipeSettingsType
from prodigy_teams_recipes_sdk import Dataset, IntProps, props, task_recipe


@task_recipe(
    title="Example Task",
    description="Annotate 'hello world'",
    field_props={
        "dataset": props.dataset_choice,
        "n_examples": IntProps(title="Number of examples to generate", min=1),
    },
)
def example_task(
    *, dataset: Dataset[Literal["text"]], n_examples: int = 100
) -> RecipeSettingsType:
    stream = ({"text": f"hello world {i}"} for i in range(n_examples))
    return {
        "dataset": dataset.name if isinstance(dataset, Dataset) else dataset,
        "stream": stream,
        "view_id": "text",
    }
