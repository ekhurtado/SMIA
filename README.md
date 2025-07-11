# Self-configurable Manufacturing Industrial Agents: SMIA 

[![Docker badge](https://img.shields.io/docker/pulls/ekhurtado/smia.svg)](https://hub.docker.com/r/ekhurtado/smia/) ![GitHub release (latest SemVer)](https://img.shields.io/github/v/release/ekhurtado/SMIA?sort=semver) [![Codacy Badge](https://app.codacy.com/project/badge/Grade/e87506fff1bb4a438c20e11bb7295f51)](https://app.codacy.com/gh/ekhurtado/SMIA/dashboard?utm_source=gh&utm_medium=referral&utm_content=&utm_campaign=Badge_grade) [![Documentation Status](https://readthedocs.org/projects/smia/badge/?version=latest)](https://smia.readthedocs.io/en/latest/)

![I4.0 SMIA Logo Light](images/SMIA_logo_positive.png/#gh-light-mode-only "SMIA logo")
![I4.0 SMIA Logo Dark](images/SMIA_logo_negative.png/#gh-dark-mode-only "SMIA logo")

[//]: # (//Dependiendo del modo de GitHub oscuro o claro se añade una imagen u otra&#41;)

The Self-configurable Manufacturing Industrial Agents (SMIA) is a proposal for the implementation of the concept of the I4.0 Component from the Reference Architectural Model Industrie 4.0 (RAMI 4.0) as an AAS-compliant agent-based Digital Twin (DT). The features of the SMIA approach include:

- free & open-source
- AAS-compliant: standardized approach
- Ontology-based
- easily customizable and extendable
- self-configuration at software startup
- easy to start-up
- containerized solution

The development of the SMIA approach is addressed by Ekaitz Hurtado as part of a PhD thesis in the Control and Systems Integration research group at the University of the Basque Country (UPV/EHU). 

> [!TIP]
> For more details on Self-configurable Manufacturing Industrial Agents see the [:blue_book: **full documentation**](https://smia.readthedocs.io/en/latest/).

## Project structure

The repository of the SMIA project is structured as follows:

- [additional_tools](https://github.com/ekhurtado/SMIA/tree/main/additional_tools): additional tools developed related to the SMIA.
  - [aas_ontology_reader](https://github.com/ekhurtado/SMIA/tree/main/additional_tools/aas_ontology_reader): this tool contains the source code of a reader capable of analyzing an AAS model based on a given OWL ontology.
  - [aasx_package_explorer_resources](https://github.com/ekhurtado/SMIA/tree/main/additional_tools/aasx_package_explorer_resources): this tool contains the JSON files to extend the AASX Package Explorer software with the Capability-Skill-Service (CSS) model.
  - [capability_skill_ontology](https://github.com/ekhurtado/SMIA/tree/main/additional_tools/capability_skill_ontology): this tool contains the ontology for the Capability-Skill-Service (CSS) model in an OWL file. It also provides some ExtendedClasses implemented in Python.
  - [gui_agent](https://github.com/ekhurtado/SMIA/tree/main/additional_tools/gui_agent): this tool provides a SPADE agent with an easy-to-use graphical interface. This agent provides several useful functionalities for SMIA usage and execution.
- [examples](https://github.com/ekhurtado/SMIA/tree/main/examples): some examples to facilitate the use of the solution.
  - [docker_compose_deployment](https://github.com/ekhurtado/SMIA/tree/main/examples/docker_compose_deployment): required files to easily deploy SMIA using the Docker Compose tool.
  - [smia_extended](https://github.com/ekhurtado/SMIA/tree/main/examples/smia_extended): an example of files related to a SMIA extension case.
  - [tutorials](https://github.com/ekhurtado/SMIA/tree/main/examples/tutorials): all the resources shown in the SMIA tutorials.
- [src](https://github.com/ekhurtado/SMIA/tree/main/src): the entire source code of the SMIA software.
  - [smia](https://github.com/ekhurtado/SMIA/tree/main/src/smia): the main Python package for the entire source code of the SMIA.

## Usage

> [!IMPORTANT]
> The project is currently under active development, 
> so new features and bug fixes will be introduced continuously.
> Therefore, although SMIA is not yet an industry-ready implementation,
> validations of the approach with different use cases will be conducted during its development.
 
Multiple ways of running SMIA software are available. 

### Download source code

The source code inside the ``src`` folder can be downloaded, and there are two launchers to run the software easily. If the folder where the launchers are located is accessed, it is possible to run SMIA using the following command:

```bash
python3 smia_cli_starter.py --model "<path to AASX package>"
```

> [!TIP]
> The launcher ``smia_starter.py`` specifies the AAS model manually, so the code must be modified. Just change the line that specifies the path to the AASX package that contains the AAS model. Then it can be executed:
>```bash
>python3 smia_starter.py
>```

### Install as pip package

The SMIA approach is also available as Python package in PyPI. It can be easily installed using [pip](https://pip.pypa.io/en/stable/):

```bash
pip install smia
```

> [!NOTE]
> The PyPI project is available at <https://pypi.org/project/smia/>.

The PyPI SMIA package contains all the source code and there are determined the necessary dependencies, so they can be automatically installed by pip, so it can run SMIA directly by:

```bash
python3 -m smia.launchers.smia_cli_starter --model "<path to AASX package>"
```

[//]: # (TODO actualizar con el nombre cuando se publique)

### Run as Docker container

The SMIA approach is also available as Docker image in DockerHub. To run SMIA software the AAS model should be passed as environmental variable:

```bash
docker run -e model=<path to AASX package> gcis-upv-ehu/smia:latest-alpine
```
[//]: # (TODO actualizar con el nombre cuando se publique)

> [!NOTE]
> The SMIA Docker Hub repository is available at <https://hub.docker.com/r/ekhurtado/smia>.

## Discussions

> [!NOTE]
> [Discussions](https://github.com/ekhurtado/SMIA/discussions) page has been set as available to share announcements, create conversations, answer questions, and more.

## Dependencies

The SMIA software, as it has been built following an Open Source Software Engineering approach, integrates some mature Python packages.

| Package name                                                   | Version | License             | Has it been modified |
|----------------------------------------------------------------|---------|---------------------|----------------------|
| [spade](https://pypi.org/project/spade/)                       | 3.3.3   | MIT                 | No                   |
| [basyx-python-sdk](https://pypi.org/project/basyx-python-sdk/) | 1.2.0   | MIT                 | No                   |
| [owlready2](https://pypi.org/project/owlready2/)               | 0.47    | GNU LGPL licence v3 | No                   |

## License

GNU General Public License v3.0. See `LICENSE` for more information.
