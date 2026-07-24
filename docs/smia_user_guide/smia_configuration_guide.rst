SMIA Configuration Guide
========================

.. _SMIA Configuration Guide:

This guide is focused on the configuration of  :term:`SMIA` software. The configuration changes minimally depending on the deployment technology.

Properties file configuration
-----------------------------

This file will be used to define the entire SMIA configuration. For example, in order to run the SMIA software correctly, it is necessary to specify certain information about the infrastructure. The properties file is divided into several sections to clarify the configuration.

===============  ===============
     Section         Details
===============  ===============
    DT               Information about the software
    AAS              Information about the AAS model
    ONTOLOGY         Information about the CSS ontology
===============  ===============

The attributes of each section will be detailed in the following subsections.

Properties file: DT section
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. centered:: Configuration of DT section.

=============================  ===============  ===================================================================================================================================================================
          Attribute                 Type                                                                      Details
=============================  ===============  ===================================================================================================================================================================
``dt.version``                    Optional       Version of the software configuration.
``dt.agentID``                    Mandatory      Identifier of the SPADE agent within SMIA to connect with XMPP server.
``dt.password``                   Mandatory      Password of the SPADE agent within SMIA to connect with XMPP server.
``dt.xmpp-server``                Mandatory      XMPP server domain required infrastructure for SPADE agent within SMIA.
``dt.smia-i-kb-registration``     Optional       Activates the registration of the SMIA agent in the SMIA-I KB along with all its CSS information (boolean ``True`` or ``False``). If set to ``True``, the agent self-registers when both SMIA-I KB and SMIA ISM are available within the platform.
=============================  ===============  ===================================================================================================================================================================

Properties file: AAS section
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. centered:: Configuration of AAS section.

=============================  ===============  ====================================================================================================================================================================
          Attribute                 Type                                                                      Details
=============================  ===============  ====================================================================================================================================================================
``aas.meta-model.version``        Optional       Version of the AAS meta-model.
``aas.model.serialization``       Optional       Serialization format of the AAS meta-model ("AASX", "XML" or "JSON").
``aas.model.folder``              Optional*      Path of the folder where the AAS model can be accessed.
``aas.model.file``                Optional*      File name of the AAS model.
``aas.id``                        Optional*      Identifier of the AAS. If a CSS-enriched AAS model (AASX file) has not been associated upon starting SMIA, setting ``aas.id`` allows the agent to automatically retrieve its CSS-enriched AAS model from the AAS Repository if both AAS Repository and SMIA ISM are available within the platform.
=============================  ===============  ====================================================================================================================================================================

.. important::
    *\*: If the AAS model is not specified at the start of the SMIA software, it must be defined either through ``aas.model.folder`` and ``aas.model.file`` or fetched automatically from the repository using ``aas.id`` when the AAS Repository and SMIA ISM are available.*

Properties file: ONTOLOGY section
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. centered:: Configuration of ONTOLOGY section.

=========================  ===============  ==================================================================================
        Attribute               Type                                              Details
=========================  ===============  ==================================================================================
``ontology.folder``           Optional*         Path of the folder where the ontology OWL file can be accessed.
``ontology.file``             Optional*         File name of the OWL ontology.
``ontology.inside-aasx``      Optional          Boolean indicating if the ontology file is located inside the AASX package.
=========================  ===============  ==================================================================================

.. important::
    *\*: If the ontology has not been added within the AASX package at start-up of the SMIA software, it is mandatory to specify the ontology file.*

.. dropdown:: Example of ``smia-initialization.properties`` configuration file
    :octicon:`file-code;1em;sd-text-primary`

    The following snippet shows a complete example of the ``smia-initialization.properties`` configuration file including all sections:

    .. code-block:: ini

        [DT]
        dt.version = #
        dt.agentid = smia_agent_1@ejabberd
        dt.password = gcis1234
        dt.xmpp-server = localhost
        dt.web-ui = True
        dt.smia-i-kb-registration = True

        [AAS]
        aas.meta-model.version = 3.0
        aas.model.serialization = .aasx
        aas.model.folder = aas/
        aas.model.file = SMIA_test_64_sm.aasx
        aas.id = #

        [ONTOLOGY]
        ontology.folder = #
        ontology.file = #
        ontology.inside-aasx = True

AAS model configuration
-----------------------

The AAS model can be defined following the :octicon:`repo;1em` :ref:`AAS Development Guide`. If it is decided to use AASX as the serialisation format, both the ontology file and the properties file can be added to the package.

.. TODO falta la guia de como añadir los ficheros dentro del AASX






