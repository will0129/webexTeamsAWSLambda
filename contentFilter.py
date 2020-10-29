"""
Your module description
"""
escalationFilter=["BGP DOWN","NETWORK DOWN"]



def messageLengthFilter(message, length):
    if len(message) > length:
        messageLength=len(message)
        #internalFailReturn.update([('errorCode','401'),('errorMessage','That message is too long. bad on you'+str(messageLength))])
        return False
    else:

        return True
 

def checkEsclation(message):

    for item in escalationFilter:
        if message.find(item) > -1:
            return True
        else:
            return False
#    if contentFilter.checkEsclation(message) == True:
#        roomId=os.environ['escalationRoom']
        

