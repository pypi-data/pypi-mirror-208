# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['ms2ml',
 'ms2ml.data',
 'ms2ml.data.adapters',
 'ms2ml.data.parsing',
 'ms2ml.metrics',
 'ms2ml.unimod',
 'ms2ml.utils']

package_data = \
{'': ['*']}

install_requires = \
['appdirs>=1.4.4,<2.0.0',
 'importlib-metadata>=6.0.0,<7.0.0',
 'lark>=1.1.2,<2.0.0',
 'loguru>=0.6.0,<0.7.0',
 'lxml>=4.9.1,<5.0.0',
 'numpy>=1.23.2,<2.0.0',
 'pandas>=2.0.1,<3.0.0',
 'psims>=1.2.3,<2.0.0',
 'pyteomics>=4.5.5,<5.0.0',
 'tomli-w>=1.0.0,<2.0.0',
 'tomli>=2.0.1,<3.0.0',
 'tqdm>=4.64.1,<5.0.0',
 'uniplot>=0.9.2,<0.10.0']

extras_require = \
{':python_version >= "3.8" and python_version < "3.11"': ['pandas-stubs>=1.5.3.230227,<2.0.0.0']}

setup_kwargs = {
    'name': 'ms2ml',
    'version': '0.0.39',
    'description': 'Provides an intermediate layer between mass spec data and ML applications, such as encoding.',
    'long_description': '![Pypi version](https://img.shields.io/pypi/v/ms2ml?style=flat-square)\n![Pypi Downloads](https://img.shields.io/pypi/dm/ms2ml?style=flat-square)\n![Github Activity](https://img.shields.io/github/last-commit/jspaezp/ms2ml?style=flat-square)\n![Python versions](https://img.shields.io/pypi/pyversions/ms2ml?style=flat-square)\n![GitHub Actions](https://img.shields.io/github/workflow/status/jspaezp/ms2ml/CI%20Testing/release?style=flat-square)\n![License](https://img.shields.io/pypi/l/ms2ml?style=flat-square)\n\n![](./docs/assets/ms2ml_logo.png)\n\n# ms2ml\n\nDocumentation site: https://jspaezp.github.io/ms2ml/main/\n\nGitHub: https://github.com/jspaezp/ms2ml\n\n**This package is in early development, I am actively taking ideas and requests**\n\nThe idea of this package is to have an intermeiate layer between the pyteomics package and ML applications.\n\nSince ML applications do not take MS data as input directly, it is necessary to convert/encode it. This package is meant to handle that aspect.\n\nThis project is meant to be opinionated but not arbitrary. By that I mean that it should attempt to enforce the "better way" of doing things (not give flexibility to do everything every way) but all design decisions are open to discussion (ideally though github).\n\n## Installation\n\n```shell\npip install ms2ml\n```\n\n## Usage\n\n```python\nfrom ms2ml.config import Config\nfrom ms2ml.data.adapters import MSPAdapter\n\n# From proteometools\nmy_file = "FTMS_HCD_20_annotated_2019-11-12.msp"\n\ndef post_hook(spec):\n    return {\n        "aa": spec.precursor_peptide.aa_to_onehot(),\n        "mods": spec.precursor_peptide.mod_to_vector(),\n    }\n\nmy_adapter = MSPAdapter(file=my_file, config=Config(), out_hook=post_hook)\nbundled = my_adapter.bundle(my_adapter.parse())\nprint({k: f"{type(v): of shape: {v.shape}}" for k, v in bundled.items()})\n# {\'aa\': "<class \'numpy.ndarray\'>: of shape: (N, 42, 29)",\n#  \'mods\': "<class \'numpy.ndarray\'>: of shape: (N, 42)"}\n```\n\n## Core parts\n\n(subject to change...)\n\n1. Parsers for external data are in ./ms2ml/data/parsing\n    1. Parsers should only be able to read data and return a base python representation, dict/list etc.\n1. Adapters are located in ./ms2ml/adapters, they should build on parsers (usually) but yield ms2ml representation objects (Spectrum, Peptide, AnnotatedSpectrum, LCMSSpectrum).\n    1. Behavior can be modified/extended using hooks.\n1. ms2ml representation objects have methods that converts them into tensor representations (Peptide.aa_to_onehot for instance)\n1. As much configuration as possible should be stored in the config.Config class.\n    1. It should contain information on the project and the way everything is getting encoded, so hypothetically one could just pass a config to a different data source adapter and get compatible results.\n    1. What position of the onehot is alanine?\n        1. look at the config\n    1. WHat order are our ions encoded in?\n        1. Look at the config.\n\n## Core design\n\n1. Unified configuration\n    - All configuration should be explicit or immediately visible upon request\n1. Consistent API\n    - It should feel similar to process the data inernally regardless of the input.\n1. Flexible output\n    - Every research need is different, therefore requesting different data from the API should be straightforward.\n1. Extensibility.\n    - It should be easy to adapt workflows to new and unexpected input data types.\n    - This is achieved with the addition of hooks that allow an additional slim layer of compatibility\n1. Abstract the loops away\n    - I do not like writting boilerplate code, neither should you. Ideally you will not need to write loops when using the user-facing API\n    - Therefore I try my best to abstract all the `[f(spec) for spec in file]` within reason.\n1. Fail loudly\n    - It is already hard to debug ML models, lets make it easier by having **sensical** error messages and checks. They should also contain suggestions to fix the bug. Explicit is better than implicit. Errors are better than bugs.\n1. Api documentation.\n    - Documentation is critical, if it is not documented, It will be deleted (because nobody will use it ...)\n    - Within reason, all external api should be documented, typed, in-code commented, have a docstring, check that it renders well using mkdocs and an example.\n    - All classes should have a static `_sample` static method that gives a sample of that object, and its docstring shoudl include an example on how to generate it.\n\n## Target audience\n\nPeople who want to train ML models from peptide/proteomics data instead of figuring out ways to encode their tensors and write parsers.\n\n```mermaid\n%%{init: {\'theme\': \'base\', \'themeVariables\': { \'primaryBorderColor\': \'#666666\', \'primaryColor\': \'#ffffff\', \'edgeLabelBackground\':\'#ffffff\', \'tertiaryColor\': \'#666666\'}}}%%\nflowchart TB\n    raw["Raw Data: .raw"]\n    mzml["Converted Data: .mzML"]\n    pepxml["Searched Data: .pep.xml"]\n    pout["FDR controlled Data: .pep.xml .pout"]\n    speclib["Spectral library: .ms2 .blib .sptxt .msp"]\n    tensor["Encoded Spectra: np.array torch.tensor"]\n    tensorcache["Tensor Cache: .hdf5 .csv .feather"]\n    mlmodel["ML model: torch.nn.Module tf.keras.nn"]\n    randomscript["Self-implemented script .py .R"]\n\n    msconvert[MSConvert]\n    searchengine[Search Engine: comet,msfragger...]\n    fdrvalidator[FDR validator: peptideprophet, Percolator, Mokapot]\n    speclibbuilder[Spectral Library Builder]\n\n    ms2ml[MS2ML]\n\n    raw --> msconvert\n    msconvert --> mzml\n    raw --> searchengine\n    searchengine --> pepxml\n    mzml --> searchengine\n    pepxml --> fdrvalidator\n    fdrvalidator --> pout\n    pout --> speclibbuilder\n    speclibbuilder --> speclib\n    pout --> randomscript\n    randomscript --> tensor\n    speclib --> randomscript\n    tensor --> mlmodel\n    tensor --> tensorcache\n    tensorcache --> mlmodel\n    tensorcache --> randomscript\n    randomscript --> mlmodel\n\n    speclib --> ms2ml\n    ms2ml --> mlmodel\n\n    linkStyle 10,11,12,13,14,15,16 stroke:#db7093,stroke-width:5px;\n    linkStyle 17,18 stroke:#008000,stroke-width:5px;\n\n    style msconvert stroke:#00ffff,stroke-width:4px\n    style searchengine stroke:#00ffff,stroke-width:4px\n    style fdrvalidator stroke:#00ffff,stroke-width:4px\n    style speclibbuilder stroke:#00ffff,stroke-width:4px\n\n    style raw fill:#cccccc,stroke-width:2px\n    style mzml fill:#cccccc,stroke-width:2px\n    style pepxml fill:#cccccc,stroke-width:2px\n    style pout fill:#cccccc,stroke-width:2px\n    style speclib fill:#cccccc,stroke-width:2px\n\n    style ms2ml fill:#ee82ee,stroke:#b882ee,stroke-width:4px\n\n```\n\n## Peptide sequence notation\n\nWhen possible I will attempt to allow \'Proforma\' based sequence annotations.\n\nCheck:\n\n- https://pyteomics.readthedocs.io/en/latest/api/proforma.html\n- http://psidev.info/sites/default/files/2020-12/ProForma_v2_draft12_0.pdf\n- https://www.psidev.info/proforma\n\n# TODO\n\n- [ ] Config\n    - [ ] Handle variable modifications\n- [ ] *Documentation, Documentation, Documentation*\n    - [ ] Helper Annotation classes\n\n# Similar projects:\n\n- https://matchms.readthedocs.io/en/latest/:\n    - Matchms is an open-access Python package to import, process, clean,\n      and compare mass spectrometry data (MS/MS). It allows to implement\n      and run an easy-to-follow, easy-to-reproduce workflow from raw mass\n      spectra to pre- and post-processed spectral data.\n    - Tailored for small molecule data\n\n- https://gitlab.com/roettgerlab/ms2ai:\n    - MS2AI from Tobias Rehfeldt (who is also part of the ProteomicsML project)\n    - Uses maxquant to for a full PRIDE to ml workflow.\n\n- https://github.com/wilhelm-lab/dlomix\n    - DLOmix from Mathias Wilhelm’s group\n    - Tensorflow centric implementatino of ml models for proteomcs\n\n- https://github.com/wfondrie/depthcharge\n    - Depthcharge is a deep learning toolkit for building state-of-the-art\n      models to analyze mass spectra generated from peptides other and molecules.\n    - It seems to focus on the model generation, rather than proving flexibility\n      in encoding.\n\n- https://github.com/bittremieux/spectrum_utils\n    - spectrum_utils is a Python package for efficient mass spectrometry\n      data processing and visualization.\n    - Many of the spectrum processing aspects are similar but there\n      is no focus in parsing or exporting encoding.\n\n# Contribution\n\nRight not this is a proof of concept package, I would be happy to make it something more stable if there is interest.\nFeel free to open an issue and we can discuss what you need out of it!! (and decide who can implement it)\n',
    'author': 'J. Sebastian Paez',
    'author_email': 'jspaezp@users.noreply.github.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://jspaezp.github.io/ms2ml/main',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>3.8,<3.12',
}


setup(**setup_kwargs)
