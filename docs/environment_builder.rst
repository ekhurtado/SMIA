SMIA Environment Builder
========================

.. _SMIA Environment Builder:

The SMIA Environment Builder is a tool provided for automating SMIA deployment environments.

.. note::

    **How does the SMIA Environment Builder work?**

    A deployment or working environment will be generated based on your answers to the following questions, which aim to determine your specific case. Component configurations will change throughout the process, depending on the options you choose. At the end, you will be able to download and deploy your SMIA environment as a ZIP file. The builder supports three scenarios:

    - **Local Development**: Local working scenario for testing and development on your local machine.
    - **Docker Compose**: Scenario for containerized deployment on a single host.
    - **Kubernetes**: Scenario for distributed and scalable deployments in containerized cluster.

Getting Started
---------------

Use the wizard builder below to configure your SMIA environment. The tool will guide you through:

1. **Infrastructure Setup**: Choose your deployment environment and configure the infrastructure components, both external (XMPP Server, AAS Server) and SMIA-specific (SMIA-I KB, SMIA ISM).
2. **SMIA Instances**: Select which SMIA instances to include and add required information to enable their self-configuration.
3. **Asset Management**: Configure manufacturing plans and production assets as SMIA instances.
4. **Review & Generate**: Review your configuration and download the deployment package.

Environment Builder
-------------------

.. raw:: html

   <div id="smia-builder-root">
       <div style="padding: 2rem; text-align: center; border: 1px dashed #ccc;">
           Loading Environment Builder... <br>
           <small>(If this takes too long, check if JavaScript is enabled)</small>
       </div>
   </div>

   <noscript>
       <div class="admonition warning">
           <p class="admonition-title">JavaScript Required</p>
           <p>This tool requires JavaScript to generate configuration files.</p>
       </div>
   </noscript>

.. note::

   The SMIA Environment Builder generates all necessary configuration files for your deployment.

   - For local development environment, you'll receive Python files along with valid templates and SMIA archive with required OWL ontology file.
   - For Docker Compose deployments, you'll receive a ``docker-compose.yml`` file along with configuration files.
   - For Kubernetes deployments, you'll receive YAML files ready to be applied to your cluster.

What's Included
---------------

Depending on your configuration, the generated package may include:

* **Environment**: Complete environment containing all required files (Python, Docker Compose, Kubernetes YAML files...).
* **Configuration Files**: Pre-configured settings for Ejabberd, AAS Server, etc.
* **README**: Deployment instructions and service documentation.
* **Directory Structure**: Organized folders for models, configs, and data.

Next Steps
----------

After downloading your configuration:

1. **Extract the ZIP file** to your desired location
2. **Review the README.md** for specific deployment instructions
3. **Place your AAS models** in the designated directory (if applicable)
4. **Deploy the environment** using the provided commands in ``README.md``.