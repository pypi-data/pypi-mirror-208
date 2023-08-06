import subprocess
import re

def about():
    """Provide a simple description of the package."""
    msg = f"""
# ===== ou-tm351-jl-extensions =====

The `ou_tm351_jl_extensions` package is an "empty" package that installs Python package requirements 
for the Open University module TM351 — Data Management and Analysis. [http://www.open.ac.uk/courses/modules/tm351].

To test the installation, run:

import ou_tm351_jl_extensions as ou
ou.check_install()
    """
    print(msg)

CHECK_EXTENSIONS = [
    'jupyterlab_ou_brand_extension',
    'jupyterlab_empinken_extension',
    'jupyterlab-skip-traceback',
    'jupyterlab-jupytext',
    'jupyterlab-stickyland',
    'jupyterlab_cell_status_extension',
    'jupyterlab-myst',
    '@ijmbarr/jupyterlab_spellchecker',
    '@jupyter-server/resource-usage',
    '@jupyterlab/geojson-extension',
    '@jupyterlab/git',
    '@hadim/jupyter-archive',
    'THIS-SHOULD-FAIL'
    ]

def check_jupyterlab_extensions_installed(extension_names):
    """
    Check if a JupyterLab extension is installed
    """
    #https://stackoverflow.com/a/38662876/454773
    def escape_ansi(line):
        ansi_escape = re.compile(r'(?:\x1B[@-_]|[\x80-\x9F])[0-?]*[ -/]*[@-~]')
        return ansi_escape.sub('', line)

    results = {}
    
    try:
        result = subprocess.check_output(['jupyter', 'labextension', 'list'], stderr=subprocess.STDOUT)
        result = escape_ansi(result.decode('utf-8'))
        _extensions = [e.strip() for e in result.split('\n') if e.startswith("        ")]
        extensions = {}
        for _ext in _extensions:
            _ext = _ext.split()
            extensions[_ext[0]] = {"installed": True,
                               "version": _ext[1],
                               _ext[2]: _ext[3]
            }
        for ext in extension_names:
            if ext not in extensions:
                results[ext] =  {"installed": False}
            else:
                results[ext] = extensions[ext]
        return results
    except subprocess.CalledProcessError as e:
        print(e.output)
        return False
    
def check_install():
    """Report whether required JupyterLab extensions are installed and enabled."""
    print("Checking extensions are installed...\n\n")
    results = check_jupyterlab_extensions_installed(CHECK_EXTENSIONS)
    for ext in results:
        print(f"{ext}: {results[ext]}")
