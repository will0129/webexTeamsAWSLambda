import json
import http.client
import mimetypes
import os




def lambda_handler(event, context):



    # If the message is native (say from IOT Device) we will set message to the message key
    
    if 'message' in event.keys():
        message=event['message']
    
    
    #If we are using Meraki Webhooks, we will have a different dictionary and will format the response in a subroutine
    # look for if 'organization' and ???  in event.keys(): then call subroutine
    
    
    
    # If we passed the Room ID in the event, we will use that. Otherwise we will source it from environment variable if set. 
    try:
        roomId=event['roomId']
    except:
        roomId=os.environ['teamsRoom']
        
    teamsAPIKey=os.environ['teamsAPIKey']
    conn = http.client.HTTPSConnection("api.ciscospark.com")
    payload = 'roomId='+roomId+'&text='+message
    headers = {
      'Authorization': 'Bearer '+teamsAPIKey,
     'Content-Type': 'application/x-www-form-urlencoded'
    }
    conn.request("POST", "/v1/messages", payload, headers)
    print(event['message'])
#    print(message)

    
    ## After this we need error control, if you get status 200, etc. 
    
    
    return {
        'statusCode': 200,
        'body': json.dumps('this post has been sent to teams, ')
    }
