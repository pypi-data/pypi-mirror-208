from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import Response, JSONResponse, HTMLResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
import functools
import io
import yaml
import uvicorn
from pydantic import BaseModel
from gradio_tools import StableDiffusionTool
import pathlib
import urllib.parse
import json


tool = StableDiffusionTool(src='gradio-client-demos/stable-diffusion', hf_token=None)

plugin_json = { 'api': { 'is_user_authenticated': False,
           'type': 'openapi',
           'url': '<<insert-url-here>>/openapi.yaml'},
  'auth': {'authorization_type': 'bearer', 'type': 'user_http'},
  'contact_email': 'freddy@freddy.edu',
  'description_for_human': 'StableDiffusion: a plugin based for the gradio '
                           'space hosted on '
                           'gradio-client-demos/stable-diffusion',
  'description_for_model': 'An image generator. Use this to generate images '
                           'based on text input. Input should be a description '
                           'of what the image should look like. The output '
                           'will be a path to an image file.If the output is '
                           'the string QUEUE_FULL you should try this action '
                           "again and never stop until you don't see this "
                           'message.',
  'legal_info_url': '<<insert-url-here>>',
  'logo_url': '<<insert-url-here>>/favicon.ico',
  'name_for_human': 'StableDiffusion',
  'name_for_model': 'StableDiffusion',
  'schema_version': 'v1'}

class PostBody(BaseModel):
    query: str

app = FastAPI()


def get_url(request: Request):
    port = f":{request.url.port}" if request.url.port else ""
    return f"{request.url.scheme}://{request.url.hostname}{port}"

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def landing_page():
    return HTMLResponse(
        """
        <p>Just a bot to sync data from diffusers gallery please go to
    <a href="https://huggingface.co/spaces/huggingface-projects/diffusers-gallery" target="_blank" rel="noopener noreferrer">https://huggingface.co/spaces/huggingface-projects/diffusers-gallery</a>
    </p>""")


@app.get('/openapi.yaml', include_in_schema=False)
@functools.lru_cache()
def read_openapi_yaml() -> Response:
    openapi_json= app.openapi()
    yaml_s = io.StringIO()
    yaml.dump(openapi_json, yaml_s)
    return Response(yaml_s.getvalue(), media_type='text/yaml')


@app.get("/.well-known/ai-plugin.json")
@functools.lru_cache()
def ai_plugin(request: Request) -> JSONResponse:
    plugin = json.loads(json.dumps(plugin_json).replace("<<insert-url-here>>", get_url(request)))
    return JSONResponse(plugin)


@app.post("/predict")
def predict(body: PostBody, request: Request) -> JSONResponse:
    output = tool.run(body.query)
    if isinstance(output, str) and pathlib.Path(output).is_file():
        output = urllib.parse.urljoin(get_url(request), f"file={output}")
    return JSONResponse({"output": output})


@app.head("/file={path_or_url:path}")
@app.get("/file={path_or_url:path}")
async def file(path_or_url: str):

    path = pathlib.Path(path_or_url)

    if path.is_absolute():
        abs_path = path
    else:
        abs_path = path.resolve()

    if not abs_path.exists():
        raise HTTPException(404, "File not found")
    if abs_path.is_dir():
        raise HTTPException(403)
    return FileResponse(abs_path, headers={"Accept-Ranges": "bytes"})

uvicorn.run(app, host="0.0.0.0", port=7860)
