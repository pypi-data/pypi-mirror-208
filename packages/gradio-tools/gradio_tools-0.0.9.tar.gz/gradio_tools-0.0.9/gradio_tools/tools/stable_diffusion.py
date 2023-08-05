from __future__ import annotations

from typing import TYPE_CHECKING, List

from gradio_client.client import Job

from gradio_tools.tools.gradio_tool import GradioTool

if TYPE_CHECKING:
    import gradio as gr


class StableDiffusionTool(GradioTool):
    """Tool for calling stable diffusion from llm"""

    def __init__(
        self,
        name="StableDiffusion",
        description=(
            "An image generator. Use this to generate images based on "
            "text input. Input should be a description of what the image should "
            "look like. The output will be a path to an image file."
        ),
        src="gradio-client-demos/text-to-image",
        hf_token=None,
        duplicate=False,
    ) -> None:
        super().__init__(name, description, src, hf_token, duplicate)

    def create_job(self, query: str) -> Job:
        return self.client.submit(query, api_name="/predict")

    def postprocess(self, output: str) -> str:
        return output

    def _block_input(self, gr) -> List["gr.components.Component"]:
        return [gr.Textbox()]

    def _block_output(self, gr) -> List["gr.components.Component"]:
        return [gr.Image()]
