def lambda_handler(event, context):
    print("Polling Gmail and running LangChain agent...")
    # TODO: Add Gmail API logic and LangChain classification
    return {
        'statusCode': 200,
        'body': 'Function ran successfully!'
    }