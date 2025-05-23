Cooperative transport logistics
===============================

.. _Use case transport logistics:

This use case represents a robotic logistics production scenario, in which a plant operator will request efficient transports performed by robots. This page will detail the use case in relation to its development and implementation and the results obtained.

.. note::

    All the resources developed in the case study are available in the `SMIA repository on GitHub <https://github.com/ekhurtado/SMIA/tree/cooperative_transport_logistics/use_cases/cooperative_transport_logistics>`_. The use case was validated with SMIA version 0.2.2.

Description of the use case
---------------------------

The objective is to enable operators to manage logistics through efficient transports. The efficiency of the transport is achieved by considering that each robot is limited in relation to the weight of the load, so the operator must know which robots are capable of performing each transport, and can request them to send or pick up products. Since it is possible for several robots to meet the transport weight requirement, it is possible to decide how the transport will be performed: by selecting a specific robot or by launching a negotiation request among the contenders for the most suitable option to perform it.

The operator represents a worker who must be able to interact with the system in order to perform the transport requests, so a Graphical User Interface (GUI) is required to interact within the SMIA ecosystem. On the other hand, it should be noted that the experiments have been performed in a simulated scenario for the ROS Noetic distribution including Turtlebot 3 Waffle Pi robots. The following figure graphically represents the use case:

.. image:: ../_static/images/use_cases_images/SMIA_coop_trans_logis_graphical.jpg
  :align: center
  :width: 600
  :alt: Cooperative transport logistics graphical representation


Development of the use case
---------------------------

The assets identified in this case study are physical, but operator accessibility is achieved through a GUI, while ROS-based robots can be managed through HTTP-based asset integration. The SPADE development platform provides the ability to add customized, web-accessible GUIs to the agents. Using this functionality, an extension of SMIA has been developed that adds a new agent capability which is in charge of managing the GUI offered by SPADE. In this way the operator can interact within the SMIA ecosystem. For transport robots it is not necessary to extend SMIA, since SMIA base presents connection with active via HTTP. Both cases are graphically presented in the following figure:

.. image:: ../_static/images/use_cases_images/SMIA_coop_trans_logis_dev.jpg
  :align: center
  :width: 400
  :alt: Cooperative transport logistics development

Deployment of the use case
--------------------------

For this use case it has been decided to deploy SMIA using the Docker Compose method, as it offers the possibility of a self-contained deployment. This way, everything necessary is added in the ``docker-compose-yml`` file and the complete use case can be deployed with a simple command, as Docker Compose takes care of starting the containers and enabling communication between them.

.. dropdown:: ``docker-compose.yml`` file of the use case
    :octicon:`file-code;1em;sd-text-primary`

    .. code:: yaml

        services:

          smia-robot-1:
            image: ekhurtado/smia:latest-alpine
            container_name: smia-robot-1
            environment:
              - AAS_MODEL_NAME=SMIA_TransportRobot_article_1.aasx
              - AGENT_ID=transportrobot001@ejabberd
              - AGENT_PSSWD=gcis1234
            depends_on:
              xmpp-server:
                condition: service_healthy
            volumes:
              - ./aas:/smia_archive/config/aas

          smia-robot-2:
            image: ekhurtado/smia:latest-alpine
            container_name: smia-robot-2
            environment:
              - AAS_MODEL_NAME=SMIA_TransportRobot_article_2.aasx
              - AGENT_ID=transportrobot002@ejabberd
              - AGENT_PSSWD=gcis1234
            depends_on:
              xmpp-server:
                condition: service_healthy
            volumes:
              - ./aas:/smia_archive/config/aas

          smia-operator:
            image: ekhurtado/smia-use-cases:latest-operator
            container_name: smia-operator
            environment:
              - AAS_MODEL_NAME=SMIA_Operator_article.aasx
              - AGENT_ID=operator001@ejabberd
              - AGENT_PSSWD=gcis1234
            depends_on:
              xmpp-server:
                condition: service_healthy
            volumes:
              - ./aas:/smia_archive/config/aas
            ports:
              - 10000:10000

          xmpp-server:
            image: ghcr.io/processone/ejabberd
            container_name: ejabberd
            environment:
              - ERLANG_NODE_ARG=admin@ejabberd
              - ERLANG_COOKIE=dummycookie123
              - CTL_ON_CREATE=! register admin localhost asd
            ports:
              - "5222:5222"
              - "5269:5269"
              - "5280:5280"
              - "5443:5443"
            volumes:
              - ./xmpp_server/ejabberd.yml:/opt/ejabberd/conf/ejabberd.yml
            healthcheck:
              test: netstat -nl | grep -q 5222
              start_period: 5s
              interval: 5s
              timeout: 5s
              retries: 10

    .. note::

        Notice how the base image of the SMIA operator is different. This is because the operator is based on an extended SMIA, so a new Docker image has been generated.

SMIA Operator dashboard
~~~~~~~~~~~~~~~~~~~~~~~

During the development of the SMIA Operator extension, a dashboard was designed to facilitate the discovery of available SMIAs and the user's use of transport requests to those SMIAs.

The developed dashboard is presented in the following figure. It is divided into different sections, related to the different phases of its use. Each one is detailed below:

* ``External SMIAs loader`` section: this section offers the possibility to discover the SMIAs available within the deployment environment and to show in a clear way the information extracted from their analysis. Since it is necessary to know the functionalities of the assets in relation to the CSS model, for each SMIA identified its associated AAS model is analyzed, obtaining all its CSS elements.
* ``Available capabilities and skills`` section: this section shows by means of a table all the information related to the CSS model obtained from the analysis of the available SMIAs, but without distinguishing from which of them it has been obtained. The table is organized in identified capabilities and offers the possibility to select one of them.
* ``SMIA candidates`` section: this section shows the SMIA candidates for the selection made (i.e. if a constraint has been determined, the list shows only the SMIAs that meet the constraint).

.. image:: ../_static/images/use_cases_images/SMIA_coop_trans_logis_dashboard.jpg
  :align: center
  :width: 700
  :alt: Cooperative transport logistics operator dashboard

El proceso a seguir para el uso correcto del dashboard es el siguiente:

The process to follow for the correct use of the dashboard is as follows:

#. When accessing the page for the first time, only the top section will have content, as the SMIAs have not yet been loaded. Since the use case has been deployed with Docker Compose, you can click directly on :bdg-success:`LOAD` and it will automatically identify and parse the SMIAs deployed next to the SMIA Operator.
     * * After clicking on the button, the GUI will be updated and all the information obtained will appear in the capabilities and skills table.
#. In the table of available capabilities and skills you can choose a capability to be requested by clicking on the :bdg-warning:`SELECT` button in the row of the desired capability.
    * After clicking on the button, if any extra data needs to be added, it will be requested. For example, if the capability has more than one skill, you will be asked if you want to select a specific one; or if there are capability constraints, you will have to determine their values.
#. Finally, in the candidate SMIA table, you can decide which SMIA (a specific one or several to negotiate) you want the capability to perform, and you can request it through the :bdg-primary:`REQUEST` button.
    * If the selected skill has input parameters, their values must be added in order to be able to request the capability.
#. When the capability has been requested, the necessary interactions with the selected SMIAs will be performed and, when the full request process is completed, their execution information will be displayed on a new page. This is shown in the following figure. As can be seen, it is divided into two sections: general information on the capability execution request and a timeline with information on each step performed by the SMIA Operator.

.. image:: ../_static/images/use_cases_images/SMIA_coop_trans_logis_dashboard_results.jpg
  :align: center
  :width: 400
  :alt: Cooperative transport logistics operator dashboard results

Use case results
----------------

During the development of the case study and the tests performed in its application, some results and conclusions have been obtained:

* Having a standard such as :term:`AAS` as a base, although it may be complex at first, offers a lot of advantages.
* The inclusion of an architectural style focused on flexible manufacturing such as the :term:`CSS model` offers simplicity in encapsulating asset functionality.
* A clear and simple dashboard is necessary to simplify the use of complex industry standards based solutions.
* It has been concluded that an efficient discovery system is necessary to know the available SMIAs and therefore the available assets. This is because a global knowledge of the system is necessary in solutions that require interactions between different components.

.. TODO PENSAR MAS RESULTADOS
