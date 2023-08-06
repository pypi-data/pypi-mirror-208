import os
import shutil
import subprocess
from pathlib import Path

from sphinx.util import logging

logger = logging.getLogger(__name__)

TEMPLATE_CONTENT = """{% if api_docs %}
    <h3>{{ _('API Documentation') }}</h3>
    <ul style="list-style-type: none;">
    {%- for item in api_docs %}
        <li style="margin-bottom: 10px;"><a href="{{ pathto('_static/api-docs/{}'.format(item), 1) }}">{{ item }}</a></li>
    {%- endfor %}
    </ul>
{% endif %}
"""


def write_template_file(app):
    templates_dir = os.path.join(app.srcdir, "_templates/sidebar")
    template_path = os.path.isfile(os.path.join(templates_dir, "api_docs_sidebar.html"))

    # create the directory if it doesn't exist
    os.makedirs(templates_dir, exist_ok=True)

    # if the template file already exists, don't write it again
    if template_path:
        return

    # else write the template content to api_docs_sidebar.html
    with open(os.path.join(templates_dir, "api_docs_sidebar.html"), "w") as f:
        f.write(TEMPLATE_CONTENT)


def update_html_context(config, api_docs=[]):
    # update html_context with api_docs
    config.html_context.update({"api_docs": api_docs})


def generate_api_sidebar(app, config):
    # write the template file
    write_template_file(app)

    # get the path to the _static/api-docs directory
    api_docs_dir = os.path.join(app.srcdir, "_static/api-docs")

    # delete the directory if it exists
    if os.path.exists(api_docs_dir):
        shutil.rmtree(api_docs_dir)

    api_docs = []

    # iterate through the list of dictionaries and run the customized command
    for api_docs_generator in config.api_docs_generators:
        # get the build command from conf.py and run it
        command = api_docs_generator["command"]

        subprocess.run([f"{command}"], text=True, shell=True, capture_output=True)

        # iterate through the list of dictionaries and copy the generated API docs to the static/api-docs directory
        for output in api_docs_generator["outputs"]:
            api_doc_name = output["name"]

            output_path = os.path.join(app.srcdir, output["path"])# the input path should be relative to app.srcdir

            shutil.copytree(output_path, os.path.join(api_docs_dir, api_doc_name))

            api_docs.append(api_doc_name)

    # update html_context with api_docs
    update_html_context(config, api_docs)


def setup(app):

    app.add_config_value("api_docs_generators", [], "env")

    app.connect("config-inited", generate_api_sidebar)
