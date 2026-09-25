.. _Guided tutorial simulated assets:

Step-by-step tutorial: Simulated assets
=======================================


This document contains a step-by-step guide to building a SMIA agent and deploying it alongside the entire platform. An Assets Simulator is provided as part of the ecosystem infrastructure, enabling the evaluation of both the agent’s and the platform’s performance. It offers detailed steps to follow, as well as source code for specific parts, to successfully reproduce the development tutorial.

.. note::

    All resources for this tutorial are available in the official SMIA repository.

    .. button-link:: https://github.com/ekhurtado/SMIA/tree/main/examples/tutorials/SMIA_extension_simulated_assets
            :color: primary
            :outline:

            :octicon:`container;1em` Step-by-step tutorial GitHub resources

.. TODO HAY QUE AÑADIR LOS RECURSOS A GITHUB


Introduction
------------

Tutorial Description
~~~~~~~~~~~~~~~~~~~~

The tutorial consists of three phases. It starts by generating the necessary pre-configuration, such as the CSS-enriched AAS model for each SMIA instance. Next, the entire SMIA platform is deployed to evaluate all the instances associated with these CSS-enriched AAS models, thanks to the necessary infrastructure (in particular, SMIA Operator). Finally, it evaluates the autonomous interaction between SMIA instances by deploying and running a BPMN manufacturing plan executed by an SMIA PE agent. The three phases are illustrated in the following figure:

.. figure:: ../../_static/images/guides_images/SMIA_guided_tutorial_simAss_steps.jpg
   :alt: SMIA simulated assets guided tutorial steps

   **Figure**: SMIA simulated assets guided tutorial steps

The objective is to evaluate the CSS-enriched AAS models using simulated assets to test their performance. To do this, we will use the Assets Simulator, an infrastructure component of the SMIA ecosystem.

.. note::

    The guide for Asset Simulators is available at :octicon:`repo;1em` :ref:`SMIA ecosystem Assets Simulators`.


In this tutorial, we will use the HTTP-based simulator, which provides three types of assets, each with different capabilities:

The following figure shows the CSS-enriched AAS elements for the three types of assets provided by the HTTP Assets Simulator:

.. figure:: ../../_static/images/guides_images/SMIA_guided_tutorial_simAss_asset_info.jpg
   :alt: SMIA simulated assets guided tutorial assets info
   :name: SMIA simulated assets guided tutorial assets info

   **Figure**: SMIA simulated assets guided tutorial assets info


Tutorial Objective
~~~~~~~~~~~~~~~~~~

Upon completing this practice, you will have achieved the following:

1. **Model:** Create a CSS-enriched AAS model that defines the asset's capabilities and serves to enable the self-configuration of the SMIA agent. As part of this process, you will also learn how to define a valid asset interface.
2. **Individual validation:** Test and validate the operation of SMIA agents individually (the operation of each agent). The **SMIA Operator** agent will be used to make requests through an intuitive graphical interface (abstracting the underlying implementation using the I4.0 language).
3. **Collaborative validation:** Test and validate the operation of the SMIA agents as a set of asset representatives within the SMIA platform. The **SMIA PE** agent will be used to automate production plans as BPMN workflows and verify how the involved agents interact and collaborate.

Development Environment
~~~~~~~~~~~~~~~~~~~~~~~

Before starting the code development part of the tutorial, it is necessary to verify that all resources are ready:

1. **AASX Package Explorer:** Required for the development of the CSS-enriched AAS model. To achieve this, you can follow the `SMIA installation guide <https://smia.readthedocs.io/en/latest/smia_user_guide/installation_guide.html#aasx-package-explorer>`_.
2. **Docker Compose:** The deployment will be conducted using Docker Compose to obtain a self-contained environment with the entire SMIA platform. It can be downloaded from its `official website <https://docs.docker.com/compose/install/>`_.
3. **SMIA package:** If you want to develop extended code and create an extended agent. To achieve this, you can follow the `SMIA installation guide <https://smia.readthedocs.io/en/latest/smia_user_guide/installation_guide.html#smia-source-code>`_.
4. **Infrastructure:** The entire SMIA platform infrastructure will be deployed using Docker, so there is no need to install anything else. However, a web browser is required to access the graphical interfaces of the infrastructure components.


First Phase: generate the CSS-enriched AAS model
------------------------------------------------


In the first phase, we will generate the CSS-enriched AAS model that will allow the SMIA agent to self-configure and obtain all information related to the simulated asset it will represent. This same process can be applied to the three types of simulated assets. The steps to follow to generate the model from scratch are as follows:


1. Open the **``AASX Package Explorer``** tool and configure it for edit mode (``Workspace > Edit``).

2. Create a new AAS within the environment and define its *idShort*. Also, add an identifier for the asset in *globalAssetId*, which will be used later to identify it as a simulated asset. It can be generated automatically, but it is recommended to add an identifier that represents the asset type (e.g., “assetID/humanWorker001”).

3. Add the ontological identifiers of the CSS model in the form of ``ConceptDescriptions``.

    3.1. Add the submodel with the ontological identifiers of the CSS model: ``Workspace > Create ... > New submodel from plugin > AasxPluginGenericForms | GCIS/SubmodelWithCapabilitySkillOntology``.

    3.2. From the submodel, generate the ConceptDescriptions with ontological identifiers of the CSS model: button ``Create <- SMEs (all)``. Within *ConceptDescriptions*, all elements will have been generated. The submodel can now be deleted (button ``Delete``), as well as its ConceptDescription (*SubmodelWithCapabilitySkillOntology*) so that it does not produce errors later (since it generates it with an empty id).

    .. note::
       As of v2025-03-25, ConceptDescriptions are generated via the ``SMEs (all)`` functionality, but this is not capable of generating all information from the plugin for the CSS model. If you do not wish to fill in all the remaining information (e.g., *shortName* of each concept), it is possible to obtain it from the base resource for the development of the CSS-enriched AAS model. To do this, you can open a new window of the ``AASX Package Explorer`` tool, open the file ``CSS_AAS_model_base.aasx`` offered in this tutorial's folder, select and copy all ConceptDescriptions using the ``Copy`` button, and ``Paste into`` in our AAS.

4. Add the submodel for defining the SMIA software: ``Workspace > Create ... > New submodel from plugin > AasxPluginGenericForms | Nameplate for Software in Manufacturing (IDTA) V1.0``.

    4.1. Delete the SubmodelElement ``SoftwareNameplateType`` and modify the ``SoftwareNameplateInstance``: remove all occurrences of *{0:00}*.

    4.2. Specify the agent identifier in ``SoftwareNameplateInstance/InstanceName[value]`` (the same one that will later be defined in the JID in the code, although in this case without the XMPP server, i.e., only the identifier before "@"), and the agent version in ``SoftwareNameplateInstance/InstalledVersion[value]`` (e.g., "1.0.0"). In addition to these mandatory data, the others are optional. You can add any data you wish to define the SMIA software in more depth (installed modules, OS on which it is deployed, etc.).

    .. note::
       If you do not want to modify the submodel, you can obtain a valid submodel with the following process: open a new window of the ``AASX Package Explorer`` tool, open the file ``CSS_AAS_model_base.aasx`` offered in this tutorial's folder, copy the "SoftwareNameplate" submodel using the ``Copy`` button, and in our AAS, ``Paste into``.


5. Add the submodel for defining the interface of the simulated asset that the SMIA agent will represent: ``Workspace > Create ... > New submodel from plugin > AasxPluginGenericForms | AssetInterfacesDescription (IDTA) V1.0``. Completely define the *SubmodelElementCollection* corresponding to the protocols supported by the asset.

    5.1. In this tutorial, we'll be using the HTTP-based Assets Simulator, so you can edit the HTTP *SubmodelElementCollection* ("InterfaceTemplateForHTTP") and rename it, for example, to ``SimulatedAssetHTTPInterface``.

    5.2. To test and validate the interface, the *EndpointMetadata/base* element will be modified with the the endpoint of the asset on the server representing the Assets Simulator. To this end, the URI will be constructed as *http://<serverIP>:<serverPort>/api/v1/<assetID>*. Since we will later deploy all components using Docker, the container name can be used; therefore, a valid endpoint using the asset ID from the previous example would be: ``http://smia-assets-simulator-http:5000/api/v1/asset/assetID/humanWorker001``.

    5.3. To test and validate asset properties, they will be added to *InteractionMetadata/properties/*. For each asset property, its *SubmodelElementCollection* must be added and specified.

    First, define its *idShort*, which is the asset’s property. The Assets Simulator provides general information about each asset via ``status``. Depending on the asset type, this includes ``battery`` (production and mobile robots) or ``stamina`` (humans). Next, define the value of its data point in *forms/href/* (for example, ``/status``).

    If you want to extract a specific piece of data from all the information returned by the asset, you can specify it in *dataQuery*. In this tutorial, the Assets Simulator returns a JSON object containing all the asset’s information from the ``/status`` data point. If you want to extract a specific piece of data, add the field where the data is located (``$.stamina`` or ``$.battery``) to *dataQuery*. This way, you can choose to retrieve all the information for further processing ("status"), or you can configure SMIA to automatically extract specific data (“stamina” or “battery”).

    5.4. To test and validate asset services, they will be added to *InteractionMetadata/actions/*. For each asset property, its *SubmodelElementCollection* must be added and specified.

    First, its *idShort* will be defined, which corresponds to the asset’s service. The Assets Simulator provides actions for each asset type and recovery/charging service (``recover/charge``). All of these are shown in the figure above (:ref:`SMIA simulated assets guided tutorial assets info`). It is also necessary to define the value of its data point in *forms/href/* using the format */action/<actionID>* (for example, ``/action/transport`` for the transport action for humans and mobile assets). In this case, it is a POST request, so it is necessary to ensure that the “Content-Type” is defined in *forms/htv_headers/*.

    .. dropdown:: :octicon:`table;1em;sd-text-primary` Simulated assets actions mappings

        The following table shows the relationship between the available actions of simulated assets and the corresponding datapoints (*/action/<actionID>* within Assets Simulator server).

        +------------------+------------------+------------------+
        | Asset type       | Action           | Datapoint        |
        +==================+==================+==================+
        | Production Asset | Welding          | ``/weld``        |
        |                  +------------------+------------------+
        |                  | Drilling         | ``/drill``       |
        |                  +------------------+------------------+
        |                  | Pick & Place     | ``/pick_place``  |
        +------------------+------------------+------------------+
        | Mobile Asset     | Transportation   | ``/transport``   |
        |                  +------------------+------------------+
        |                  | Patrol           | ``/patrol``      |
        |                  +------------------+------------------+
        |                  | RADAR Scan       | ``/scan``        |
        +------------------+------------------+------------------+
        | Human Asset      | Transportation   | ``/transport``   |
        |                  +------------------+------------------+
        |                  | Assembly         | ``/assemble``    |
        |                  +------------------+------------------+
        |                  | QA Inspection    | ``/inspect``     |
        |                  +------------------+------------------+
        |                  | Maintenance      | ``/maintain``    |
        +------------------+------------------+------------------+

        .. tip::
            All actions allow specifying a ``duration`` as a parameter within the body of the HTTP request, but it is not necessary to specify it within the AID submodel (it is specified at the Skill CSS level and is automatically handled by SMIA).

    .. note::
       The submodel must be completely defined so that it does not produce errors during the SMIA startup. If you wish to modify a valid submodel, you can open a new window of the ``AASX Package Explorer`` tool, open the file ``CSS_AAS_model_base.aasx`` offered in this tutorial's folder, copy the "AssetInterfacesDescription" submodel using the ``Copy`` button, and in our AAS, ``Paste into``.


6. Define the submodels with the asset information. To do this, create the submodels in the AAS via ``Create new Submodel of kind Instance``. For this tutorial, we will define two submodels to distinguish the CSS-enriched elements of the asset (functional information) and the ontological relations between them: ``CSSElements`` and ``CSSInfo``.

    6.1. Define the submodel ``CSSElements``, adding the following SubmodelElementCollections (specified by the idShort): *Capabilities*, *Skills*,, and *Constraints*. Within each collection, SubmodelElements will be added so that they can be semantically enriched later. Within *Capabilities*, the asset’s capabilities will be added using Capability elements, with their *idShort* set to the corresponding capability (e.g., for human assets, ``Assembly`` or ``Recovering``), while within *Skills*, Operations will be added with the associated skills for those capabilities (e.g., for human assets, ``Assemble`` or ``Recover``).

    All actions except "Recover" have a possible input SkillParameter to determine the duration of the action. This can be defined using a Property with the idShort *duration*. Finally, within *Constraints*, you can add the only currently possible limitation using a Range with the idShort *PayloadWeight*, with a type “xs:float” and values (e.g., min: 0.0 and max: 5.0).

    6.2. Define the submodel ``CSSInfo``, adding the following RelationshipElements to link the CSS elements. Capabilities, Skills, Skill Parameters, Capability Constraints, and Skill Interfaces must be linked correctly. You can use any naming convention you wish for the idShort, but descriptive names are recommended, such as *RelCapSkill<>* to link capabilities and skills, *RelSkillSkillInterface<>* to link skills and their interfaces, and *RelCapConstraint<>* to link capabilities and their constraints. To link elements, add them to the ``first`` and ``second`` parameters  (use the ``Add existing`` button to select the elements).

7. Semantically enrich the SubmodelElements with the ontological concepts of the CSS model. To do this, in each created element, add the corresponding ``semanticID``.

    7.1. In each SubmodelElement to be enriched, create an empty semanticID (``Create w/ default!``), then ``Add existing`` and select the identifiers corresponding to each element from the ConceptDescriptions (e.g., "http://www.w3id.org/upv-ehu/gcis/css-smia#AssetCapability" for asset capabilities).

    7.2. In each RelationshipElement defined for each ontological relationship, add its semanticID following the procedure in step ``7.1``.

    7.3. Define the *Qualifiers* for capabilities, skills, and constraints. To do this, create an empty qualifier (``Create w/ default!``), then ``Add preset`` and select the associated qualifier from ``GCIS | CSS |``. For example, for capabilities, add the *hasLifecycle* qualifier with the value *ASSURANCE*; for skills, add *hasImplementationType* with the value *ASSURANCE*; or for skill parameters, add *hasType* with the value *INPUT*, among others.

.. dropdown:: :octicon:`table;1em;sd-text-primary` Simulated assets CSS information

    The following table shows the CSS information of simulated assets, required for their the CSS-enriched AAS model.

    +------------------+---------------------+--------------------+-----------------------------+-------------------+------------------------------------------------+
    | Asset Type       | Capability          | Capability Type    | Skill                       | Skill Parameter   | Constraint                                     |
    +==================+=====================+====================+=============================+===================+================================================+
    | Production Asset | Welding             | Asset Capability   | Weld                        | duration          | \-                                             |
    |                  +---------------------+--------------------+-----------------------------+-------------------+------------------------------------------------+
    |                  | Drilling            | Asset Capability   | Drill                       | duration          | \-                                             |
    |                  +---------------------+--------------------+-----------------------------+-------------------+------------------------------------------------+
    |                  | PickingAndPlacing   | Asset Capability   | PickAndPlace                | duration          | PayloadWeight (*IR1 [0-5 kg] / IR2 [0-10 kg]*) |
    |                  +---------------------+--------------------+-----------------------------+-------------------+------------------------------------------------+
    |                  | Charging            | Asset Capability   | Charge                      | \-                | \-                                             |
    |                  +---------------------+--------------------+-----------------------------+-------------------+------------------------------------------------+
    |                  | Negotiation         | Agent Capability   | NegotiationBasedOnBattery   | NegotiationWinner | \-                                             |
    +------------------+---------------------+--------------------+-----------------------------+-------------------+------------------------------------------------+
    | Mobile Asset     | Transportation      | Asset Capability   | Transport                   | duration          | PayloadWeight (*MR1 [0-5 kg] / MR2 [0-10 kg]*) |
    |                  +---------------------+--------------------+-----------------------------+-------------------+------------------------------------------------+
    |                  | Patrolling          | Asset Capability   | Patrol                      | duration          | \-                                             |
    |                  +---------------------+--------------------+-----------------------------+-------------------+------------------------------------------------+
    |                  | Scanning            | Asset Capability   | Scan                        | duration          | \-                                             |
    |                  +---------------------+--------------------+-----------------------------+-------------------+------------------------------------------------+
    |                  | Charging            | Asset Capability   | Charge                      | \-                | \-                                             |
    |                  +---------------------+--------------------+-----------------------------+-------------------+------------------------------------------------+
    |                  | Negotiation         | Agent Capability   | NegotiationBasedOnBattery   | NegotiationWinner | \-                                             |
    +------------------+---------------------+--------------------+-----------------------------+-------------------+------------------------------------------------+
    | Human Asset      | Transportation      | Asset Capability   | Transport                   | duration          | PayloadWeight (*[0-15 kg]*)                    |
    |                  +---------------------+--------------------+-----------------------------+-------------------+------------------------------------------------+
    |                  | Assembly            | Asset Capability   | Assemble                    | duration          | \-                                             |
    |                  +---------------------+--------------------+-----------------------------+-------------------+------------------------------------------------+
    |                  | Inspection          | Asset Capability   | Inspect                     | duration          | \-                                             |
    |                  +---------------------+--------------------+-----------------------------+-------------------+------------------------------------------------+
    |                  | Maintenance         | Asset Capability   | Maintain                    | duration          | \-                                             |
    |                  +---------------------+--------------------+-----------------------------+-------------------+------------------------------------------------+
    |                  | Recovering          | Asset Capability   | Recover                     | \-                | \-                                             |
    |                  +---------------------+--------------------+-----------------------------+-------------------+------------------------------------------------+
    |                  | Negotiation         | Agent Capability   | NegotiationBasedOnStamina   | NegotiationWinner | \-                                             |
    +------------------+---------------------+--------------------+-----------------------------+-------------------+------------------------------------------------+

8. Save the AASX file with the complete definition of the valid CSS-enriched AAS model. To do this, use the menu: ``File > Save as ...``, select the folder where the CSS-enriched AAS model will be saved and specify the name for the AASX file.



.. TODO repasarlo y seguir con esta parte


Second Phase: validate the SMIA agents manually
-----------------------------------------------

.. TODO



Third Phase: validate the SMIA agents via SMIA PE
-------------------------------------------------

.. TODO



.. note::

    This tutorial is currently in development and will be available soon!

.. TODO ELIMINARLO CUANDO SE ACABE
