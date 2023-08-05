<p align="center">
  <img src="http://logos.u2d.ai/msaFileWorker_logo.png?raw=true" alt="msaFileWorker">
</p>

------
<p align="center">
    <em>msaFileWorker - file management library</em>
  <a href="https://pypi.org/project/msaFileWorker" target="_blank">
      <img src="https://img.shields.io/pypi/v/msaFileWorker?color=%2334D058&label=pypi%20package" alt="Package version">
  </a>
  <a href="https://pypi.org/project/msaFileWorker" target="_blank">
      <img src="https://img.shields.io/pypi/pyversions/msaFileWorker.svg?color=%2334D058" alt="Supported Python versions">
  </a>
</p>

------

**Documentation**: <a href="https://msaFileWorker.u2d.ai/" target="_blank">Documentation (https://msaFileWorker.u2d.ai/)</a>

------
## License Agreement

- `msaFileWorker`Based on `MIT` open source and free to use, it is free for commercial use, but please show/list the copyright information about msaFileWorker somewhere.


## How to create the documentation

We use mkdocs and mkdocsstring. The code reference and nav entry get's created virtually by the triggered python script /docs/gen_ref_pages.py while ``mkdocs`` ``serve`` or ``build`` is executed.

### Requirements Install for the PDF creation option:
PDF Export is using mainly weasyprint, if you get some errors here plsease check there documentation. Installation is part of the msaFileWorker, so this should be fine.

We can now test and view our documentation using:

    mkdocs serve

Build static Site:

    mkdocs build


## Build and Publish

Build:

    python setup.py sdist

Publish to pypi:

    twine upload dist/*
