# Self-configurable Manufacturing Industrial Agents: SMIA 

[![Python versions](https://img.shields.io/pypi/pyversions/smia.svg)](https://pypi.org/project/smia/) [![Docker badge](https://img.shields.io/docker/pulls/ekhurtado/smia.svg)](https://hub.docker.com/r/ekhurtado/smia/) ![GitHub release (latest SemVer)](https://img.shields.io/github/v/release/ekhurtado/SMIA?sort=semver) [![Codacy Badge](https://app.codacy.com/project/badge/Grade/e87506fff1bb4a438c20e11bb7295f51)](https://app.codacy.com/gh/ekhurtado/SMIA/dashboard?utm_source=gh&utm_medium=referral&utm_content=&utm_campaign=Badge_grade) [![Documentation Status](https://readthedocs.org/projects/smia/badge/?version=latest)](https://smia.readthedocs.io/en/latest/)


![SMIA Logo](https://raw.githubusercontent.com/ekhurtado/SMIA/refs/heads/main/images/SMIA_logo_positive.png "SMIA main logo")

[//]: # (The logo image need to be obtained externally)

[//]: # (//Dependiendo del modo de GitHub oscuro o claro se añade una imagen u otra&#41;)

The Self-configurable Manufacturing Industrial Agents (SMIA) is a proposal for the implementation of the concept of the I4.0 Component from the Reference Architectural Model Industrie 4.0 (RAMI 4.0) as an AAS-compliant agent-based Digital Twin (DT). The features of the SMIA approach include:

- free & open-source
- AAS-compliant: standardized approach
- Ontology-based
- easily customizable and configurable
- self-configuration at software startup
- easy to usage
- containerized solution

The development of the SMIA approach is addressed by Ekaitz Hurtado as part of a PhD thesis in the Control and Systems Integration research group at the University of the Basque Country (UPV/EHU).

> 💡 **TIP:**
> For more details on Self-configurable Manufacturing Industrial Agents (SMIA) see the [📄 **full documentation**](https://smia.readthedocs.io/en/latest/).

## Usage

> ❗ **IMPORTANT:**
> The project is currently under active development, 
> so new features and bug fixes will be introduced continuously.
> Therefore, although SMIA is not yet an industry-ready implementation,
> validations of the approach with different use cases will be conducted during its development.
 
Multiple ways of running SMIA software are available. The associated GitHub repository shows how to run the base SMIA software.

In this case, how to use the SMIA Python package is shown.

### Installation

The SMIA approach can be easily installed using [pip](https://pip.pypa.io/en/stable/):

```
pip install smia
```
[//]: # (TODO actualizar con el nombre cuando se publique)

### Available facilities

The SMIA approach offers different facilities for its use:

- ``smia.launchers``: some launchers to run the base SMIA software.
  - ``smia.launchers.smia_cli_starter.py``: launcher to run the SMIA software by passing the AAS model as CLI argument.
  - ``smia.launchers.smia_starter.py``: launcher to run the SMIA software by passing the AAS model through Python code.
  - ``smia.launchers.smia_docker_starter.py``: launcher to run the SMIA software as Docker container by passing the AAS model as environmental variable.
- ``smia.agents``: the Agent classes available to be instantiated and used.
  - ``smia.agents.SMIAAgent``: the generic SMIA agent.
  - ``smia.agents.ExtensibleSMIAAgent``: the extensible SMIA agent offering all extension methods.
- ``smia.assetconnection``: tools related to connection with assets.
  - ``smia.assetconnection.HTTPAssetConnection``: tools related to connection with assets through HTTP communication protocol.

The other modules are available for import when, for example, developing an extension to SMIA.

[//]: # (TODO actualizar con los que se presenten)

#### Extensibility

SMIA extensibility is provided through the special agent ``ExtensibleSMIAAgent``. It provides some methods to extend the base SMIA and add own code:

- ``add_new_agent_capability(behaviour_class)``: this method adds a new agent capability to SMIA to increase its intelligence and autonomy. The new capability is  added as a SPADE behavior instance.
- ``add_new_agent_service(service_id, service_method)``: this method adds a new agent service to SMIA to increase its intelligence and autonomy. The new service is added as a Python method that will be called when the service is requested.
- ``add_new_asset_connection(aas_interface_id_short, asset_connection_class)``: this method adds a new asset connection to SMIA. The new connection is added by the instance class inherited from the official SMIA generic class ``AssetConnection`` and the associated AAS interface element.

### Examples

Create and run an ``SMIAAgent``:
```python
import smia
from smia.agents.smia_agent import SMIAAgent

smia.load_aas_model('<path to the AASX package containing the AAS model>')
my_agent = SMIAAgent()

smia.run(my_agent)
```

#### Extensibility examples

Create an ``ExtensibleSMIAAgent``:
```python
import smia
from smia.agents.extensible_smia_agent import ExtensibleSMIAAgent

smia.load_aas_model('<path to the AASX package containing the AAS model>')
my_agent = ExtensibleSMIAAgent()
```

Add new ``Agent Capability`` to ``ExtensibleSMIAAgent``:
```python
import spade
from smia.agents.extensible_smia_agent import ExtensibleSMIAAgent  # Import from the SMIA package

new_capability = spade.behaviour
my_extensible_agent.add_new_agent_capability(new_capability)
```

Add new ``Agent Service`` to ``ExtensibleSMIAAgent``:

```python
from smia.agents.extensible_smia_agent import ExtensibleSMIAAgent  # Import from the SMIA package

my_extensible_agent.add_new_agent_service(new_service_id, new_service_method)
```

Add new ``Asset Connection`` to ``ExtensibleSMIAAgent``:

```python
from smia.agents.extensible_smia_agent import ExtensibleSMIAAgent  # Import from the SMIA package

my_extensible_agent.add_new_asset_connection(aas_interface_id_short, asset_connection_class)
```

Complete example of an Extensible SMIA agent:

```python
import smia
import asyncio
from spade.behaviour import CyclicBehaviour
from smia.agents.extensible_smia_agent import ExtensibleSMIAAgent  # Import from the SMIA package
from my_asset_connections import MyAssetConnection

class MyBehaviour(CyclicBehaviour):
    async def on_start(self):
        print("MyBehaviour started")
        self.iteration = 0

    async def run(self):
        print("MyBehaviour is in iteration {}.".format(self.iteration))
        self.iteration += 1
        await asyncio.sleep(2)

def new_service_method():
    print("This is a new service to be added to SMIA.")
    
def main():
    my_extensible_agent = ExtensibleSMIAAgent()
    smia.load_aas_model('<path to the AAS model>')
    
    my_behav = MyBehaviour()
    my_extensible_agent.add_new_agent_capability(my_behav)
    
    my_extensible_agent.add_new_agent_service('new_service_id', new_service_method)
    
    new_asset_connection = MyAssetConnection()
    my_extensible_agent.add_new_asset_connection('new_connection_idshort', new_asset_connection)
    
    smia.run(my_extensible_agent)

if __name__ == '__main__':
    main()
```

## Dependencies

The SMIA software requires the following Python packages to be installed to run correctly. These dependencies are listed in ``pyproject.toml`` so that they are automatically obtained when installing with ``pip``:

- ``spade`` (MIT license)
- ``basyx-python-sdk`` (MIT license)
- ``owlready2`` (GNU LGPL licence v3)

[//]: # (TODO actualizar con los que sean)

## License

GNU General Public License v3.0. See `LICENSE` for more information.
