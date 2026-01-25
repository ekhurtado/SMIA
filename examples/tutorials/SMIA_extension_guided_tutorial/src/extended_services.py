def extended_agent_service(extended_param: int):
    print("Hi! I am an extended agent service for duplicating numbers...")
    try:
        result = int(extended_param) * 2
        print("The value received and duplicate value: {}, {}".format(extended_param, result))
        return result
    except Exception as e:
        print("ERROR: The received parameter is not an integer: {}".format(extended_param))