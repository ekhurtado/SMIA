class SMIABPMNInfo:

    BPMN_SMIA_NAMESPACE = 'http://upv-ehu/gcis/smia/bpmn'

    # BPMN XML tags
    BPMN_SERVICE_TASK_XML_TAG = 'bpmn:serviceTask'
    BPMN_GATEWAY_XML_TAG = 'bpmn:exclusiveGateway'

    # Definition of required tasks in each step of the workflow
    TASK_CHECK_TIMEOUT = 'TaskCheckTimeout'
    TASK_REQUEST_DISTRIBUTED_CNP = 'TaskRequestDistributedCNP'
    TASK_REQUEST_DATA_TO_PREVIOUS = 'TaskRequestDataToPrevious'
    TASK_REQUEST_DATA_TO_FOLLOWING = 'TaskRequestDataToFollowing'
    TASK_REQUEST_DATA_TO_TASK = 'TaskRequestDataToTask'

    # SMIA own attributes for BPMN elements
    SERVICE_TASK_CAPABILITY_ATTRIBUTE = 'capability'
    SERVICE_TASK_SKILL_ATTRIBUTE = 'skill'
    SERVICE_TASK_SKILL_PARAMETERS_ATTRIBUTE = 'skillParameters'
    SERVICE_TASK_CAPABILITY_CONSTRAINTS_ATTRIBUTE = 'constraints'
    SERVICE_TASK_ASSET_ATTRIBUTE = 'asset'
    SERVICE_TASK_REQUEST_PREVIOUS_ATTRIBUTE = 'requestToPrevious'
    SERVICE_TASK_REQUEST_FOLLOWING_ATTRIBUTE = 'requestToFollowing'
    SERVICE_TASK_REQUEST_TASK_BY_ID = 'requestToTaskById'

    GATEWAY_TIMEOUT_ATTRIBUTE = 'timeoutValue'

    REQUEST_DATA_SPLIT_PATTERN = r"(\w+)\[(.*)\]"
    REQUEST_TASK_DATA_SPLIT_PATTERN = r"(\w+)\[(\w+)\[(.*)\]\]"


