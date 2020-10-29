import json
import http.client
import mimetypes
import os


#testing Content Filter
import contentFilter 

#We Set an internal failure mechanism to respond back to appropriate requests or webhooks
internalFailReturn={}

def checkShared(secretKey):
#The Purpose of this function is to provide a way to check shared secret for webhooks that do not have API Gateway aws strings. 

  if os.environ['webhookSecret']!=secretKey:
  
    internalFailReturn.update([('errorCode','401'),('errorMessage','The Shared Secret provided in the body of the message does not match expectd value')])
    return
  else:
    return
    
    
    
    
    
    
    
def lambda_handler(event, context):
    
        
    # If we passed the Room ID in the event, we will use that. Otherwise we will source it from environment variable if set. 
    # roomID could be set in message by third party apps or IOT devices, or whatnot. Not for webhooks.
    
    
    
    
    
    try:
        roomId=event['roomId']
    except:
        roomId=os.environ['teamsRoom']
    



    internalFailReturn.clear()    # Successive iterations in AWS did not reinstantiate this, we clear this because it would hold errors between API calls.

    # If the message is native (say from IOT Device) we will set message to the message key
    
    if 'message' in event.keys():
        message=event['message']
    # Or, if it is from Meraki we will use the other keys    

    elif 'organizationUrl' in event.keys():
        if event['organizationUrl'].find('meraki.com'):
            checkShared(event['sharedSecret'])

            message='Meraki Log for organization {orgid} on network {netname} : {alertType} : {alertData}'.format(orgid=event['organizationId'], netname=event['networkName'], alertType=event['alertType'],alertData=event['alertData'])
    
    elif 'source' in event.keys():
        if event['source']=='ndb' or event['source']=='DNAC':
            checkShared(event['sharedSecret'])
            message='Cisco DNA Center log {category}:{status}:{severity}:{title}'.format(category=event['category'],status=event['status'],severity=event['severity'],title=event['title'])

    ## To apply content filters you can use one of the below.

    if contentFilter.messageLengthFilter(message, 500)==False: 
        
        internalFailReturn.update([('errorCode','401'),('errorMessage','Thoo long')])
    if contentFilter.checkEsclation(message) == True:
        roomId=os.environ['escalationRoom']
        message="Emergency!!! Quickly, lets all jump on cs.co/wnellis bridge for issue "+message
        


### if any existing logic checks have not created an error, we can send the message to teams.
        
    if not 'errorCode' in internalFailReturn.keys():
        
        teamsAPIKey=os.environ['teamsAPIKey']
        conn = http.client.HTTPSConnection("api.ciscospark.com")
        payload = 'roomId='+roomId+'&text='+message
        headers = {
          'Authorization': 'Bearer '+teamsAPIKey,
         'Content-Type': 'application/x-www-form-urlencoded'
        }
        conn.request("POST", "/v1/messages", payload, headers)
        ## After this we need error control, if you get status 200, etc. 
    
        response = conn.getresponse()
        statuscode = response.status



    if 'errorCode' in internalFailReturn.keys() and 'errorMessage' in internalFailReturn.keys():
        return {
            'statusCode': internalFailReturn['errorCode'],
            'body': internalFailReturn['errorMessage'],
    }
    elif statuscode == 200:
        return {
            'statusCode': statuscode,
            'body': 'SUCCESS - This post has been sent to teams'
    }
    elif statuscode == 401:
        return {
            'statusCode': statuscode,
            'body': 'ERROR - Authentication Failed, '
    }
    elif statuscode == 404:
        return {
            'statusCode': statuscode,
            'body': 'ERROR - URI Not Found, '
    }
    elif statuscode == 429:
        return {
            'statusCode': statuscode,
            'body': 'ERROR - Too Many Requests, '
    }
    elif statuscode >= 500:
        return {
            'statusCode': statuscode,
            'body': 'ERROR - Server Error, '
    }
    else:
          return {
             ## consider updating, this may not account for use case there was internal error
            'statusCode': statuscode,
            'body': 'ERROR - Unknown Error, '
    }