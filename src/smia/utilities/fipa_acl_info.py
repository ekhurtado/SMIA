class FIPAACLInfo:
    """
    This class contains the values related to FIPA-ACL standard.
    """

    # FIPA-ACL attribute values
    FIPA_ACL_PERFORMATIVE_ATTRIB = 'performative'
    FIPA_ACL_ONTOLOGY_ATTRIB = 'ontology'
    FIPA_ACL_PROTOCOL_ATTRIB = 'protocol'
    FIPA_ACL_ENCODING_ATTRIB = 'encoding'
    FIPA_ACL_LANGUAGE_ATTRIB = 'language'

    # Performative values
    FIPA_ACL_PERFORMATIVE_CFP = 'cfp'
    FIPA_ACL_PERFORMATIVE_INFORM = 'inform'
    FIPA_ACL_PERFORMATIVE_REQUEST = 'request'
    FIPA_ACL_PERFORMATIVE_PROPOSE = 'propose'
    FIPA_ACL_PERFORMATIVE_FAILURE = 'failure'
    FIPA_ACL_PERFORMATIVE_QUERY_IF = 'query-if'
    FIPA_ACL_PERFORMATIVE_QUERY_REF = 'query-ref'
    FIPA_ACL_PERFORMATIVE_REFUSE = 'refuse'
    FIPA_ACL_PERFORMATIVE_NOT_UNDERSTOOD = 'not-understood'

    # TODO borrar: Antiguos nombres (se han actualizado a los formatos definidos en FIPA (en minuscula))
    # FIPA_ACL_PERFORMATIVE_CFP = 'CallForProposal'
    # FIPA_ACL_PERFORMATIVE_INFORM = 'Inform'
    # FIPA_ACL_PERFORMATIVE_REQUEST = 'Request'
    # FIPA_ACL_PERFORMATIVE_PROPOSE = 'Propose'
    # FIPA_ACL_PERFORMATIVE_FAILURE = 'Failure'
    # FIPA_ACL_PERFORMATIVE_QUERY_IF = 'Query-If'
    # TODO add more if they are needed
    # TODO se han añadido estos pero todavia no se utilizan:
    FIPA_ACL_PERFORMATIVE_ACCEPT_PROPOSAL = 'AcceptProposal'
    FIPA_ACL_PERFORMATIVE_REJECT_PROPOSAL = 'RejectProposal'
    FIPA_ACL_PERFORMATIVE_AGREE = 'Agree'
    FIPA_ACL_PERFORMATIVE_CONFIRM = 'Confirm'
    FIPA_ACL_PERFORMATIVE_NOT_UNDERSTOOD = 'NotUnderstood'
    FIPA_ACL_PERFORMATIVE_REFUSE = 'Refuse'

    # Ontology values
    FIPA_ACL_ONTOLOGY_SVC_REQUEST = 'SvcRequest'
    FIPA_ACL_ONTOLOGY_SVC_RESPONSE = 'SvcResponse'
    FIPA_ACL_ONTOLOGY_CAPABILITY_REQUEST = 'CapabilityRequest'
    FIPA_ACL_ONTOLOGY_CAPABILITY_CHECKING = 'CapabilityChecking'
    FIPA_ACL_ONTOLOGY_CAPABILITY_RESPONSE = 'CapabilityResponse'
    FIPA_ACL_ONTOLOGY_SVC_NEGOTIATION = 'Negotiation'

    # Default values in SMIA approach for some attributes
    FIPA_ACL_DEFAULT_ENCODING = 'application/json'
    FIPA_ACL_DEFAULT_LANGUAGE = 'smia-language'

class ACLSMIAOntologyInfo:
    """
    This class contains the values related to ACL-SMIA ontology library information: the ontology classification
    established for the SMIA approach.
    """
    ACL_ONTOLOGY_ASSET_RELATED_SERVICE = 'asset-related-service'
    ACL_ONTOLOGY_AGENT_RELATED_SERVICE = 'agent-related-service'
    ACL_ONTOLOGY_AAS_SERVICE = 'aas-service'
    ACL_ONTOLOGY_AAS_INFRASTRUCTURE_SERVICE = 'aas-infrastructure-service'
    ACL_ONTOLOGY_CSS_SERVICE = 'css-service'

class ServiceTypes:
    """
    This class contains all service types defined in the Functional View of RAMI 4.0.
    """
    ASSET_RELATED_SERVICE = 'AssetRelatedService'
    AAS_INFRASTRUCTURE_SERVICE = 'AASInfrastructureService'
    AAS_SERVICE = 'AASservice'
    SUBMODEL_SERVICE = 'SubmodelService'
    CSS_RELATED_SERVICE = 'CSSRelatedService'   # TODO duda con este ya que contiene el concepto de service dentro, y no es lo mismo

class ACLSMIAJSONSchemas:
    """This class contains all the JSON schemas related to ACL messages sent between SMIA agents."""

    JSON_SCHEMA_AAS_MODEL_REFERENCE_old = {
        "type": "object",
        "properties": {
            "keys": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "type": {"type": "string"},
                        "value": {"type": "string"}
                    },
                    "required": ["type", "value"]
                }
            }
        },
        "required": ["keys"]
    }

    JSON_SCHEMA_SUBMODEL_SERVICE_REQUEST = {
        "type": "object",
        "properties": {
            "ModelReference": JSON_SCHEMA_AAS_MODEL_REFERENCE_old,
            "ExternalReference": {
                "type": "string"
            }
        },
        "oneOf": [
            {"required": ["ModelReference"]},
            {"required": ["ExternalReference"]}
        ]
    }

    JSON_SCHEMA_ASSET_SERVICE_REQUEST = {
        "type": "object",
        "properties": {
            "serviceParameterValues": {
                "type": "object",
                "additionalProperties": {"type": "string"}
            },
            "ModelReference": JSON_SCHEMA_AAS_MODEL_REFERENCE_old,
        },
        "required": ["ModelReference"]
    }

    JSON_SCHEMA_CAPABILITY_REQUEST = {
        "type": "object",
        "properties": {
            "capabilityName": {"type": "string"},
            "skillName": {"type": "string"},
            "skillParameterValues": {
              "type": "object",
              "additionalProperties": {
                "type": "string"
              }
            },
            "skillInterfaceName": {"type": "string"}
        },
        "required": ["capabilityName"]
    }

    # NEW SCHEMAS FOR SMIA: added in v0.2.4
    # -------------------------------------
    # -------------------------------------

    # Common schemas
    # --------------
    JSON_SCHEMA_AAS_MODEL_REFERENCE = {
        "oneOf": [
            {
                "type": "object",
                "properties": {
                    "keys": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "type": {"type": "string"},
                                "value": {"type": "string"}
                            },
                            "required": ["type", "value"]
                        }
                    }
                },
                "required": ["keys"]
            },
            {
                "type": "string",
                "pattern": "^(\\[[^\\[\\],]+,[^\\[\\],]+\\])+$",
                "description": "ModelReference format for strings: [type,value][type,value]..."
            }
        ]
    }

    JSON_SCHEMA_SMIA_INSTANCE_INFORMATION = {
        "type": "object",
        "properties": {
            "id": { "type": "string" },
            "asset": {
                "type": "object",
                "properties": {
                    "id": {"type": "string"},
                    "kind": {"type": "string"},
                    "type": {"type": "string"},
                }
            },
            "aasID": {"type": "string"},
            "status": {"type": "string"},
            "startedTimeStamp": {"type": "integer"},
            "smiaVersion": {"type": "string"},
        },
        "required": ["id", "asset", "aasID"],
    }
    # TODO pensar mas (ademas de añadir ModelReference mas adelante)

    # Asset-related services / agent-related services schemas
    # -------------------------------------------------------
    JSON_SCHEMA_ASSET_AGENT_RELATED_SERVICE = {
        "title": "AssetAgentRelatedServiceSchema",
        "type": "object",

        "properties": {
            "serviceRef": JSON_SCHEMA_AAS_MODEL_REFERENCE,
            "serviceParams": {
                "type": "object",
                "additionalProperties": {"type": "string"}
            }
        },
        "required": ["serviceRef"]
    }
    # TODO falta probarlos

    # AAS Services schemas
    # --------------------
    JSON_SCHEMA_AAS_SERVICE = {
        # "$schema": "http://json-schema.org/draft-07/schema#",
        "title": "AASServiceSchema",
        "type": "object",

        "properties": {
            "serviceID": {"type": "string"},
            "serviceType": {
                "type": "string",
                "enum": ["SubmodelRegistryService", "MetaInformationManagementService", "DiscoveryService"]  # TODO in the future think about adding more
            },
            "serviceParams": {}
        },
        "required": ["serviceID", "serviceType"],
        "allOf": [
            {
                "if": {
                    "properties": {"serviceID": {"const": "GetSubmodelElementByReference"}}
                },
                "then": {
                    "properties": {
                        "serviceParams": JSON_SCHEMA_AAS_MODEL_REFERENCE
                    }
                }
            },
            {
                "if": {
                    "properties": {
                        "serviceID": {
                            # TODO Think of more AAS services that simply require a string.
                            "enum": ["GetAASInformationByAssetID"]
                        }
                    }
                },
                "then": {
                    "properties": {
                        "serviceParams": {"type": "string"}
                    }
                }
            }
        ]
    }
    # TODO falta probarlos

    # AAS Infrastructure Services schemas
    # -----------------------------------
    JSON_SCHEMA_AAS_INFRASTRUCTURE_SERVICE = {
        # "$schema": "http://json-schema.org/draft-07/schema#",
        "title": "AASInfrastructureServiceSchema",
        "type": "object",

        "properties": {
            "serviceID": { "type": "string" },
            "serviceType": {
                "type": "string",
                "enum": ["RegistryService", "DiscoveryService"]   # TODO in the future think about adding more
            },
        "serviceParams": {}
        },
        "required": ["serviceID", "serviceType"],
        "allOf": [
            {
                "if": {
                    "properties": { "serviceID": { "const": "RegistrySMIAInstance" } }
                },
                "then": {
                    "properties": { "serviceParams": JSON_SCHEMA_SMIA_INSTANCE_INFORMATION }
                }
            },
            {
                "if": {
                    "properties": {
                        "serviceID": {
                            # TODO Think of more infrastructure services that simply require a string.
                            "enum": ["GetSMIAInstanceIDByAssetID", "GetAssetIDBySMIAInstanceID",
                                     "GetAllAssetIDByCapability"]
                        }
                    }
                },
                "then": {
                    "properties": {
                        "serviceParams": { "type": "string" }
                    }
                }
            }
        ]
    }
    # TODO falta probarlos

    # CSS Services schemas
    # --------------------
    JSON_SCHEMA_CSS_SERVICE = {
        "type": "object",
        "properties": {
            "capabilityIRI": {"type": "string"},
            "skillIRI": {"type": "string"},
            "constraints": {
                "type": "object",
                "additionalProperties": {"type": "string"}
            },
            "skillParams": {
                "type": "object",
                "additionalProperties": {"type": "string"}
            },
            "skillInterfaceIRI": {"type": "string"},

            # Optional parameters for SMIA instances negotiation within FIPA-CNP protocol
            "negCriterion": {"type": "string"},
            "negTargets": {
                "type": "array",
                "items": {"type": "string"}
            },
            "negValue": {
                "type": "number",   # It is a float number between 0 and 1
                "minimum": 0.0,
                "maximum": 1.0
            },
        },
        "required": ["capabilityIRI"]
    }
    # TODO falta probarlos


    # JSON schemas mapping to ACL-SMIA ontologies
    # -------------------------------------------
    JSON_SCHEMA_ACL_SMIA_ONTOLOGIES_MAP = {
        ACLSMIAOntologyInfo.ACL_ONTOLOGY_ASSET_RELATED_SERVICE: JSON_SCHEMA_ASSET_AGENT_RELATED_SERVICE,
        ACLSMIAOntologyInfo.ACL_ONTOLOGY_AGENT_RELATED_SERVICE: JSON_SCHEMA_ASSET_AGENT_RELATED_SERVICE,
        ACLSMIAOntologyInfo.ACL_ONTOLOGY_AAS_SERVICE: JSON_SCHEMA_AAS_SERVICE,
        ACLSMIAOntologyInfo.ACL_ONTOLOGY_AAS_INFRASTRUCTURE_SERVICE: JSON_SCHEMA_AAS_INFRASTRUCTURE_SERVICE,
        ACLSMIAOntologyInfo.ACL_ONTOLOGY_CSS_SERVICE: JSON_SCHEMA_CSS_SERVICE
    }