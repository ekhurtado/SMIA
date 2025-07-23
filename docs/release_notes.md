# Release Notes

(Release Notes)=

## v0.3.0

This release of Self-configurable Manufacturing Industrial Agents (SMIA) comes with a significant upgrade of the solution in terms of flexible manufacturing automation using the SMIA approach. Version 0.2.x of SMIA focused on asset integration, and version 0.3.x will focus on autonomy and flexible manufacturing (where the interaction of multiple SMIA instances and the need for new infrastructure arise).

This specific release introduces new components within the SMIA ecosystem that enable flexible manufacturing automation. These new components are:
- ``SMIA KB``: This is an infrastructure component for a Knowledge Base (KB). It is an OWL ontology instance management database based on the CSS model. This infrastructure provides HTTP access following the OpenAPI standard specification.
- ``SMIA ISM``: This is a "special" SMIA agent in charge of managing all the infrastructure services that may be requested by SMIA instances. In other words, it offers the possibility of receiving requests for infrastructure services via FIPA-ACL, executing them and returning the response. In the validated case study it is used for the interaction between the ACL environment (SMIA instances) and HTTP-OpenAPI (SMIA KB and AAS Repository).
- ``SMIA PE``: This is a "special" SMIA agent able to collect a flexible production plan serialized in BPMN and carry it out by performing the necessary interactions with the other SMIA instances or with the infrastructure services (through the SMIA ISM).
- ``SMIA HI``: This is an extension of SMIA agent that provides a human interface (HI) so that a human can be an additional production asset. It is capable of submitting CSS requests and picking up completed ones via web GUI.

> SMIA: All Python files structured in Python modules.
> - It includes the launcher files to run the software in the ``launchers`` module: _smia_cli_starter.py_, _smia_starter.py_ and _smia_docker_starter.py_.

### Features

- All the code of the newly developed components has been added
  - SMIA KB, SMIA ISM, SMIA PE, SMIA HI.
  - Their developments have been done in individual branches, which have been integrated into the main at the end of their development.
  - All of them have been added inside the ``additional_tools`` folder.
- The SMIA plugin code for the Camunda Modeler software has been added.
  - This plugin is able to collect the CSS ontology information from the SMIA KB and present it to the user during the design of the BPMN flow (which will represent the flexible production plan).
- Added option to set the AAS ID (instead of the path to the AAS model file)
  - Added option as CLI, environment variable (Docker) and via code (``smia.load_aas_id``).
  - If the ID is set, and not the model file, the AAS model is obtained through an infrastructure service to SMIA ISM (it will obtain the whole AAS model from the AAS Repository)
- Added more precision in saved timestamps for SMIA performance evaluation (new method ``get_current_timestamp_microsecs`` in GeneralUtils)
- Added code to generate JSON objects from ontology instances for CSS elements. Added also the method to use this JSONs to register all the CSS elements extracted in the self-configuration in the SMIA KB

### Major Changes

- The additional software within the SMIA ecosystem has been divided into two folders
  - ``additional_resources``: several additional static resources will be grouped here, such as the CSS-SMIA ontology OWL file, visual resources, etc.
  - ``additional_tools``: several software programs developed within the SMIA ecosystem will be grouped here: SMIA KB, ISM, PE, HI, Camunda plugin...
- The versions of some SMIA dependencies have been upgraded (regarding SPADE, other versions have had to be adapted for the software to function correctly)
  - SPADE from v3.3.3 to v4.0.3
  - Basyx-python-sdk to v1.2.1
  - Owlready2 to v0.48
- Added explanation in SMIA RTD ``Extension guide`` on how to correctly add agent services that are defined inside Python classes (need to be added with the "self" included in the executable method)
- Added adaptation of complex parameters in ``get_adapted_service_parameters`` for services_utils

### Fixed errors

- Ontology file loading bug fixed: before if the properties file was not set, it always looked for the ontology inside the AASX, now it looks for it in the SMIA Archive.
- Added ServerConnectionError handling during HTTP requests (connection with HTTP-based assets)
  - For cases, e.g., in which the server suddenly is disconnected
- Fixed an error obtaining the agent identifier from the agent JID with SPADE version >4.x.x (now the ``acl_smia_messages_utils.get_agent_id_from_jid`` method is used)
- Fixed some circular imports error when creating SMIA documentation with Sphinx (for ReadTheDocs)

## v0.2.4

This release of Self-Configurable Manufacturing Industrial Agents (SMIA) comes with an upgrade of the solution in terms of interaction between different SMIA instances.

> SMIA: All Python files structured in Python modules.
> - It includes the launcher files to run the software in the ``launchers`` module: _smia_cli_starter.py_, _smia_starter.py_ and _smia_docker_starter.py_.

### Features

- A class for AAS services information (``aas_services_info``) has been added.
- The possible interactions between SMIA instances have been analyzed and a new ACL message structure for the SMIA approach has been proposed.
  - This proposal will be used for all SMIA instances.
  - The proposal is based on FIPA-ACL, integrating the FIPA performatives and proposing ontologies based on the different AAS services defined in the Functional View of AAS.
- JSON schemas have been added within SMIA for the new structures of ACL messages.
  - These schemas will be used to both validate incoming messages and create new ones to be sent.
  - Added a method to check ACL-SMIA messages with the new JSONSchemas in ``inter_aas_interactions_utils``.
  - Added util code to interactions between SMIA instances: create message from received ones, create message body using JSONSchemas...
- Improved JSONSchema for AAS ModelReferences. Now it can be defined in object (as defined in the AAS meta-model) or in String (e.g., as copied from the AASX Package Explorer).
- Added code into ``HTTPAssetConnection`` to send POST requests with the service data in the body, serialized by the specified content type.
- Added method to register the SMIA instance itself in the SMIA KB using by requesting an AAS infrastructure service.
- Improved distributed negotiation algorithm in FIPA-CNP management of SMIA (situations whit negotiation value tie).
A seeded randomization process is now performed to manage the tie and obtain a random winner (the same for all instances managing the same specific tie).

### Major Changes

- Changed ``inter_aas_interactions_utils`` to ``inter_smia_interactions_utils``
- The additional resource ``GUI Agent`` has been improved by adding the new structure for ACL message for interactions between SMIA instances
- Added possibility to determine the affected element in ServiceRequestExecutionErrors
- Modified all the ACL receiving methods and behaviours (ACLHandling, Negotiation…) with the new structure of ACL-SMIA message and the new approach to handle the interactions (depending on the ontology, its associated behaviour is added)
- Modified the handling of AAS related services with the new approach and new ACL-SMIA message schemas: to handle asset-/agent-related services and AAS Services (discovery)
- Modified the handling of CSS related services with the new approach and new ACL-SMIA message schemas: received JSON validation, capability checking and capability execution
- Modified SMIA negotiation code (management of FIPA-CNP protocol) with the new structures of FIPA-SMIA-ACL messages
Added ``CapabilityChecking`` in the FIPA-CNP management. In case it failed, SMIA instance returns Refuse message and it will have -1.0 negotiation value to lose against all the participants

### Fixed errors

- Fixed a bug during the self-configuration of an AAS without agent capabilities
  - SMIA was trying to add non-existing elements
- Fixed an error in the method to serialize service input data into HTTP request body
- Fixed an error in HTTPAssetConnection by adding body content to the HTTP POST requests
- Fixed error during saving information in log files (now the ontology values are used to determine the log file for each type of service)
- Fixed error when receiving ACL message with non JSON body (e.g. in an Inform message)
- Modified ``simple_human_in_the_mesh`` and ``cooperative_transport_logistics`` use cases deployment files to set v0.2.2 of SMIA as base Docker image
  - To avoid errors due to future developments of the source code
- Fixed README files regarding the links to SMIA ReadTheDocs project
- Fixed error executing agent services defined both as asynchronous and as static methods
- Fixed a problem in capability checking (constraints were checked although the capability did not have them)

## v0.2.3

This release of Self-Configurable Manufacturing Industrial Agents (SMIA) comes with an upgrade of the solution in terms of validation and accesibility. 

> SMIA: All Python files structured in Python modules.
> - It includes the launcher files to run the software in the ``launchers`` module: _smia_cli_starter.py_, _smia_starter.py_ and _smia_docker_starter.py_.

### Features

- All relevant tests have been conducted with the first case study (SMIA operator and transport robots within the “Cooperative transport logistics” case).
- The tutorials for SMIA (AAS development, SMIA extension and deployment of the “Cooperative transport logistics” case study) have been completed.
- CSS-SMIA ontology has been published in w3id: now using the IRIs in the browser you can access the SMIA GitHub.
- Improved RTD glossary:
  - Added more terms.
  - Improved explanations of each term.
- Added SMIA approach PDF and demo video as additional resource.
- Created branches for additional infrastructure services development: SMIA KB (``smia_kb_development``) and Camunda plugin (``camunda_plugin_development``).

### Major Changes

- Renamed ``additional_tools`` folder to ``additional_resources``.
- Renamed additional resources folder ``capability_skill_ontology`` to ``css_smia_ontology``.
- Changed I4.0 SMIA to SMIA:
  - Both on GitHub and on ReadTheDocs.
  - Updated all files that contain the old name (PyPI configuration files, READMEs…).
- Modified SMIA banner style. 
- Upgraded “basyx-python-sdk” dependency to its latest version (1.2.0).

### Fixed errors
- Fixed bugs during testing of CSS-based AAS development tutorial
- Removed old Kubernetes test files (YAML deployment files in “examples” folder)
- Removed tests with CSS-SMIA ontology from “additional_resources/css_smia_ontology/tests” folder
- Removed code from old SMIA approach: folder with the different AAS Cores
- Removed ``deploy`` folder: contained deployment files of the old SMIA approach
- Modified README file to improve the important message in the “Usage” section mentioning the validations being conducted with the use cases.

## v0.2.2

This release of Self-Configurable Manufacturing Industrial Agent (SMIA) comes with an upgrade of the solution. Similar to the other releases, it is available with the  source code in a ZIP file. Content of ``SMIA.source.code.zip`` file:

> SMIA: All Python files structured in Python modules.
> - It includes the launcher files to run the software in the ``launchers`` module: _smia_cli_starter.py_, _smia_starter.py_ and _smia_docker_starter.py_.

### Features

- SMIA now is available as pip package in PyPI and TestPyPI 
  - In the previous version the package was generated and uploaded manually 
  - In this version it is automatically created with GitHub Actions and uploaded to both PyPI and TestPyPI. 
- The first use case for SMIA with the new approach (from ``v0.2.0``) has been started its development 
  - An SMIA operator has been developed taking advantage of the SMIA extension methods. 
    - The related resources (code for the new capability, HTMLs for the operator dashboard) have been developed. 
  - Some SMIAs for transport robot assets have been deployed. 
  - The required AASs for the different types of assets (operator and transport robot) have been developed.  
  - First tests with transport requests and negotiations in case of multiple robot options have been performed. 
- The SMIA ReadTheDocs documentation project has been improved 
  - New guides developed such as SMIA Extension  
- A new SMIA launcher for SMIA deployments based on Docker containers (``smia_docker_starter.py``)

### Major Changes 

- The SMIA ReadTheDocs documentation project file have been improved 
  - Improved guides such as start-up SMIA 
  - The glossary has been considerably improved by adding multiple terms useful for understanding the SMIA approach 
- Removed all old code related to the AAS Manager-Core approach (prior to ``v0.2.0``) 
  - Removed unused objects like interaction_id, all related methods only used in the old approach... 
- The README for PyPI has been improved:  
  - Added some examples  
  - Added explanations of the modules  
  - Added explanations of the extension methods  

### Fixed errors

- Added OWL ontology file for the CSS model in Docker SMIA images in case the user does not add it in AASX (AAS model associated to SMIA).  
- Fixed problem with displaying AAS model analysis results with no parsed CSS model elements. 
- Fixed bugs with tests with invalid AAS models. 
- Fixed bugs with invalid ontology tests. 
- Fixed an error when SubmodelService with ExternalReference is requested. 

## v0.2.1

This release of I4.0 Self-Configurable Manufacturing Industrial Agent comes with an upgrade of the new approach added in version 0.2.0 of the solution. Similar to the other releases, it is available with the  source code in a ZIP file. Content of ``SMIA.source.code.zip`` file:

> SMIA: All Python files structured in Python modules.
> - It includes two launcher files to run the software in the ``launchers`` module: _smia_cli_starter.py_ and _smia_starter.py_.

### Features

- Information about the software during runtime is now stored in the Archive.  
  - The log has been structured to store different types of information (status of executions and errors).  
  - The status of completed requests for services and capabilities is also stored. 
    - Information about errors occurred during requests is also stored with the type of the error. 
- There are new ways to run the software  
  - PyPI package to install SMIA and run it directly (accessible on TestPyPI) 
  - Docker container with SMIA installed to run it passing only the AAS model as environment variable. 
    - Los Dockerfiles con los que se han generado están disponibles en la carpeta ``docker`` 
    - Two types of images are provided: a lightweight image based on Python Alpine (``smia/alpine-*``) and a full image based on generic Python (``smia/full-*``).   
  - Docker Compose for efficient deployment with all required infrastructure 
    - Comes with an XMPP server that can be used to communicate with different SMIAs  
- Now it is possible to extend the software through extension methods that allow you to add your own code to the SMIA base.  
  - It is offered through a new agent called ``ExtensibleSMIAAgent``.  
  - It is accessible through the PyPI package or by downloading the source code.  
- New guides have been added to the associated ReadTheDocs documentation platform to help developers and users get integrated into the SMIA ecosystem  
  - A SMIA start-up guide has been developed. 

### Major Changes 

- The code of the negotiation capability has been modified with the new approach (the one added in version ``v0.2.0``). 
  - Negotiation is now an agent capability and is managed as such. 
- The open source project has been completed with the remaining files such as contributing, release notes, about the project, code of conduct or templates for issues. 
  - Both on GitHub and on ReadTheDocs 
- Progress has been made in the removal of old code related to the AAS Manager-Core approach (prior to version ``v0.2.0``). 	

### Fixed errors

- Changed library for HTTPAssetConnection from ``requests`` to ``aiohttp``. 
  - Requests is a library for synchronous program, so it was blocking all software waiting for server response. 
  - With aiohttp now software is able to perform other tasks while waiting for HTTP server response (e.g. pick up other ACL requests) 
- Fixed a bug in the ``load_aas_model`` method of the smia package: it did not use the file passed, now it copies the file into the archive to use it as AAS model 
  - Did not allow to start correctly the code 
- Fixed problem with ``capability_skill_module`` module during Sphinx documentation generation due to ontology Python object 
  - A condition has been added to fix the problem during Sphinx generation. 
- Fixed problem with inheritance of SMIA extended classes from Basyx AAS classes


## v0.2.0

This release of I4.0 Self-Configurable Manufacturing Industrial Agent comes with a new approach for the solution. That is the reason why the software has been upgraded to version 0.2.x. Similar to the other releases, it is available with the  source code in a ZIP file. Content of ``SMIA.source.code.zip`` file:

> SMIA: All Python files structured in Python modules.
> - It includes two launcher files to run the software in the ``launchers`` module: _smia_cli_starter.py_ and _smia_starter.py_.

### Features

- New additional tools:
  - A reader capable of parsing an AAS model based on a given OWL ontology.
  - The JSON files to extend the AASX Package Explorer software with the Capability-Skill-Service (CSS) model.
  - The ontology for the Capability-Skill-Service (CSS) model in an OWL file. Some ExtendedClasses implemented in Python are also provided.
  - A SPADE agent with an easy-to-use graphical interface. This agent provides several useful functionalities for SMIA usage and execution.
- SMIA can be run with several launchers offered with the source code.
  - smia_cli_starter.py: SMIA can be run with a simple configuration by setting the AAS model with "-m" or "--model" attribute and the SPADE configuration with "-c" or "--config"
  - smia_starter.py: provides some methods to load the AAS model or the SPADE configuration file by passing the path.
- This new approach focuses on the integration of the Capablity-Skill-Service (CSS) model, implemented as an OWL ontology.
- SMIA now self-configures using an AAS model based on an OWL ontology that represents the CSS model.
  - It can create ontology instances with the CSS model information added in the AAS model.
  - So now the structure of the AAS model is not constrained, only the CSS model concepts need to be added using semantic identifiers.
- SMIA can handle two types of interactions:
  - Service requests, with new kinds such as submodel services.with new kinds such as submodel services.
  - Capability requests, related to the CSS model.
- SMIA now integrates assets with communication protocol utility logic within its source code.
  - An abstract "AssetConnection" class has been defined, with some general methods to extend it with the necessary communication protocols.
  - Asset integration for HTTP has been developed in this version.


### Major Changes 

- The name of the approach has changed from "I4.0 Standardized Microservice-based Industrial Agent" to "I4.0 Self-Configurable Manufacturing Industrial Agent". The acronym of SMIA is retained.
- The AAS Core disappears. The logic for asset integration and connection has been added in the AAS Manager.
  - Now the asset connection is defined within SMIA by extending a common abstract class.
- With the removal of AAS Core, the Intra AAS interactions through Kafka have also disappeared.
- The AAS Manager as a concept disappears. In the new approach, the software is AAS-compliant, so there is now only SMIA as software solution.
  - The approach is also based on the CSS model implemented as an OWL ontology.
- The software can now entirely self-configure by using only a valid AASX Package.
  - The structure of the AAS model within the AASX is now unconstrained, only the required CSS model semantic identifiers need to be added.
- The management of FIPA-ACL request messages has been changed, as there are now two types: service requests (i.e. submodel service) and capability requests (i.e. execute a capability through a specific skill and skill interface).

### Fixed errors

- Fixed Sphinx code autodocumentation with some modules.
- Fixed errors during the execution of the software with the development of exception to manage them.
  - AAS model reading errors, asset connection errors…

## v0.1.3

Fourth release of I4.0 Standardized Microservice-based Industrial Agent (I4.0 SMIA) with the source code in a ZIP file. Content of ZIP file:

### AAS Source code

> AAS Manager: All Python files structured in Python modules, including the main file to start the agent (`aas_manager.py`).
> AAS Cores: The source code of the three AAS Cores developed for this release: Numerical AAS Core (developed in Java, so the JAR file (`Numerical_AAS_Core.jar`) is provided), OPC UA AAS Core (Python modules, including the `main.py`) and ROS AAS Core (Python modules, including the `main.py`).

### Features

- New additional tools:  
  - A reader capable of transforming an AAS definition in XML (following the RAMI 4.0 meta-model) into structured Python objects. 
  - A reader capable of reading AASX files and getting the submodels fromt the AAS definition. 
- The AAS Manager and the AAS Core can be run individually, as the interaction between them has been changed to be done through Kafka. 
- The AAS Manager can handle service request from the AAS Core. 
- The AAS Manager can handle negotiation requests. 
  - The AASs can participate in negotiation with different criteria using a distributed algorithm. 
- The AAS Core for physical assets has been improved: for ROS transport robots and a Warehouse managed by a PLC with OPC UA server. 
- First proactive AAS with logical asset to perform a production management application. 
  - The AAS Core defines the relation between the AASs of the I4.0 System in order to produce an industrial application. 
  - The first developed application has been in a use case of a transport process to store product to a warehouse using transport robots. 


### Major Changes 

- Changed GitHub repository name from "Component_I4.0" to "I4.0 SMIA".
- The interaction between the AAS Manager and the AAS Core is perform through Kafka. 

### Fixed errors

- Fixed ReadTheDocs project with the new name of the GitHub repository (I4.0 SMIA).
- Fixed AAS Manager managing some service requests with unsupported format.

## v0.1.2

Third release of I4.0 Standardized Microservice-based Industrial Agent (I4.0 SMIA) with the source code in a ZIP file. Content of ZIP file:

### AAS Source code

> AAS Manager: All Python files structured in Python modules, including the main file to start the agent (`aas_manager.py`).
> AAS Cores: The source code of the three AAS Cores developed for this release: Numerical AAS Core (developed in Java, so the JAR file (`Numerical_AAS_Core.jar`) is provided), OPC UA AAS Core (Python modules, including the `main.py`) and ROS AAS Core (Python modules, including the `main.py`).

### Features

- AAS Manager is a SPADE agent parameterized with physical or logical assets. 
- AAS Manager has a Finite State Machine (FSM) to add behaviours in each state of the agent. 
   - This FSM depends on the type of the asset. 
- AAS Manager is capable of managing FIPA-ACL requests for executing asset related services and for negotiating (for latter the algorithm is not yet integrated ). 
- AAS Manager and AAS Core are able to interact and synchronized between them. 
- Two new AAS Cores have been developed and added in this version 
   - An AAS Core to work with ROS: able to interact with ROS nodes and to communicate with physical robots. In the tested use case a simulation of a Turtlebot 3 has been used. 
   - An AAS Core to work with OPC UA: able to interact with a OPC Servers. It has been tested with a server running on a Siemens PLC that manages a warehouse simulated in Factory I/O. 

### Major Changes 

- The AAS Manager gets its ID form the associated configmap
   - Due to the deployment of multiple AASs 
- AAS Manager and AAS Core have FSMs to synchronize with each other. 

### Fixed errors

- AAS Manager can handle ACL messages using template with multiple options 
   - For example, to negotiation requests different performative can be used 
- AAS Manager and AAS Core initialization fixed: bugs with status JSON file 
- Fixed some links a content related to the documentation

## v0.1.1

Second release of I4.0 Standardized Manufacturing Component (I4.0 SMC) with the source code in a ZIP file. Content of ZIP file:

### AAS Source code

> AAS Manager: All Python files structured in Python modules, including the main file to start the agent (`aas_manager.py`).
> AAS Core: Example of AAS Core for for the numerical services functionality. Developed in Java, so the JAR file (`AAS_Core.jar`) is provided.

### Features

- AAS Manager is a SPADE agent.
- AAS Manager has a Finite State Machine (FSM) to add behaviours in each state of the agent.
- AAS Manager is able to initialize all required files to allow interaction with the AAS Core.
- AAS Manager is capable of managing FIPA-ACL requests.
- AAS Manager and AAS Core are able to interact between them.
- AAS Manager and AAS Core are synchronized at startup.
- AAS Manager can request services from AAS Core.
- AAS Core is able to offer services related to numbers.

## v0.1.0

First release of I4.0 Standardized Manufacturing Component (I4.0 SMC) with the source code in a ZIP file. Content of ZIP file:

### Source code

> AAS Manager: Python main file (`main.py`) and required files (inside `utilities` folder).
> AAS Core: Example of AAS Core for for the numerical services functionality. Developed in Java, so the JAR file (`AAS_Core.jar`) is provided.

### Features

- AAS Manager is capable of managing HTTP requests.
- AAS Manager and AAS Core are able to interact between them.
- AAS Manager can request services from AAS Core.
- AAS Core is able to offer services to work with numbers.

