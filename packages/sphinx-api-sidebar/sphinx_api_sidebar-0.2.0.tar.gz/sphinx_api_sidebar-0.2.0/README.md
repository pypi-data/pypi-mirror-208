# Sphinx API Sidebar

A Sphinx extension for displaying any generated static API documentation in a sidebar.

## Overview

This Sphinx extension allows you to include and display static API documentation (e.g., `JavaDoc`, `Doxygen`) in the sidebar of your Sphinx documentation. It updates the `html_context` with the API documentation paths, which can then be used to render the API documentation sidebar template.

This extension serves as an immediate workaround to make Sphinx consume API docs in HTML format from various languages without building additional deeply integrated extensions for each type of API docs.

## Installation

To install the `sphinx-api-sidebar` extension, you can use pip:

```sh
pip install sphinx-api-sidebar
```

## Usage
1. To enable the sphinx-api-sidebar extension in your Sphinx documentation project, add it to the extensions list in your conf.py file:

```python
extensions = [
    'sphinx_api_sidebar',
    # Other extensions...
]
```

2. To use a custom command to generate your API documentation or specify different directories, you can set the `api_docs_generators` configuration value in your conf.py file:

```python
api_docs_generators = [
  {
    'command': '<your_api_docs_build_command_1>',
    'outputs': [
            {
                'name': '<generated_api_doc_name_1>',
                'path': '<path_to_generated_api_doc_1>' # path should be relative to the docs directory
            },
            {
                'name': '<generated_api_doc_name_2>',
                'path': '<path_to_generated_api_doc_2>'
            },
            # ...
        ]
  },
  {
    'command': '<your_custom_build_command_2>',
    'outputs': [
            {
                'name': '<generated_api_doc_name_3>',
                'path': '<path_to_generated_api_doc_3>'
            },
            # ...
        ]
  },
  # more groups of generated api docs
]
```

Replace `<your_custom_build_command_*>`, `<generated_api_doc_name_*>`, and `<path_to_generated_api_doc_*>` with the appropriate values for your project.

3. Update your `conf.py` file to include the `api_docs_sidebar.html` template in the html_sidebars configuration:

```python
html_sidebars = {
    '**': [
        # ... other sidebars ...
        'sidebar/api_docs_sidebar.html',
    ]
}
```
