#!/usr/bin/env python3
####################################################################################################
# ipyemail.py                                                                                      #
# This function takes input parameters for email and sends it out through our IBM                  #
#                                                                                                  #
# Copyright (c) 2019 StateStreetOpenSource                                                       #
####################################################################################################

import smtplib
import os
import re
import mimetypes
from email.mime.multipart import MIMEMultipart
from email import encoders
from email.message import Message
from email.mime.audio import MIMEAudio
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email.mime.text import MIMEText

def iPyEmail(toEmail   = ' ',          fromEmail = ' ',\
             subject   = 'no subject', bodyText  = ' ',\
             attachments = 'n/a',      attachAsBody  = 'N'):
    #____________________________________________    
    # Requirements Check
    if toEmail == '' or toEmail == ' ':
        print('error: "to email" not provided')
        return
    
    if fromEmail == '' or fromEmail == ' ':
        print('error: "from email" not provided')
        return
    if checkEmailSyntax(toEmail) == False:
        print('error: bad "to email" syntax')        
        return
    
    if checkEmailSyntax(fromEmail) == False:
        print('error: bad "from email" syntax')        
        return
    
    #____________________________________________            
    # Initialization
    fileExt  = '.wxyz'
    body     = ' '  
    bodyType = 'html'
    if bodyText != ' ' and bodyText != '':
        bodyText = bodyText + '\r\r'

    # Standardize case
    bodyType     = bodyType.lower()
    attachAsBody = attachAsBody.upper()

    # Server Connection
    smtp = smtplib.SMTP('YOUR IBM i SMTP SERVER')
    msg  = MIMEMultipart('alternative')
    
    #_____________________________________________________________
    # Add provided body text to email when attachment not for body
    if attachAsBody == 'N' and bodyText != ' ':
        bodyType = 'plain'
        msg_text = MIMEText(bodyText, bodyType)
        msg.attach(msg_text)

    # Add attachments (not "As Body") if file path(s) given
    if attachments != 'n/a':
        if attachAsBody  != 'Y' or attachAsBody == 'B':
            # Add mutiple attachments to an Email (not "As Body")
            # Attachment_paths is a list, like this:['/home/x/a.pdf', '/home/x/b.txt']
            for attachment in attachments:
                ctype, encoding = mimetypes.guess_type(attachment)
                if ctype is None or encoding is not None:
                    ctype = "application/octet-stream"

                maintype, subtype = ctype.split('/', 1)

                try:
                    with open(attachment, 'rb') as f:
                        part = MIMEBase(maintype, subtype)
                        part.set_payload(f.read())
                        encoders.encode_base64(part)
                        part.add_header('Content-Disposition', 'attachment', filename=os.path.basename(attachment))
                        msg.attach(part)

                except IOError:
                     print ("error: Can't open the file %s"%attachment)

    # Add attachments "As Body" if file path(s) given
    if attachAsBody == 'Y' or attachAsBody == 'B':
        bodyType = 'plain'
        attachmentCount = 0
        for attachment in attachments:
            attachmentCount = attachmentCount + 1
            ctype, encoding = mimetypes.guess_type(attachment)
            if ctype is None or encoding is not None:
                ctype = "application/octet-stream"

            maintype, subtype = ctype.split("/", 1)

            # Only text based files can be added as body text!
            if maintype == "text":
                if subtype == 'html':
                    bodyType = subtype
                else:
                    bodyType = 'plain'

                try:
                    # Loop through the given files and add to body
                    with open(attachment, 'r') as file:
                        # First add the bodyText content if provided by user
                        if attachmentCount == 1:
                            if bodyText != ' ' and bodyText != '':
                                body = bodyText + file.read()
                            else:
                                body = file.read()
                        else:
                            body = body + file.read()

                except IOError:
                     print ("error: Can't open the file %s"%attachment)

            # Tried to use a non-text file type!
            else:
                bodyType = 'plain'
                if attachmentCount == 1:
                    body = 'File ' + attachment + ', type "' + maintype + '" must be attached! Please contact sender.'
                else:
                    body = body + 'File ' + attachment + ', type "' + maintype + '" must be attached! Please contact sender.'

        # Add the completed body to the email
        msg_text = MIMEText(body, bodyType)
        msg.attach(msg_text)

    # Add remaining email options and send!
    msg['From']    = fromEmail
    msg['To']      = toEmail
    msg['Subject'] = subject
    smtp.send_message(msg)
    smtp.quit()

    return

def checkEmailSyntax(addressToVerify = ' '):
    addressToVerify = addressToVerify.lower()
    if re.match('^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$', addressToVerify) == None:  
        return False
    else:
        return True    

def main():
    print("========================================================================")
    print("--------------------T E S T I N G    E X A M P L E S--------------------")
    print("========================================================================")
    # Simple Message Without Attachments
    iPyEmail('toEmail@somesite.com', 'fromEmail@yourSite.com','Test without Attachment','Test body text...1 2 3...A B. C')

    # HTML Send Test
    Attachments = ['/IFSPATH/IFSFile.HTM']
    iPyEmail('toEmail@somesite.com', 'fromEmail@yourSite.com','HTML Send Test (as body)','', Attachments, 'Y')
    iPyEmail('toEmail@somesite.com', 'fromEmail@yourSite.com','HTML Send Test','', Attachments, 'N')

    # Image Send Test
    Attachments = ['/IFSPATH/images/YourImage.jpg']
    # Image Send Test (this first one should fail (binaries can't be the body)	
    iPyEmail('toEmail@somesite.com', 'fromEmail@yourSite.com'','Image Send Test (as body)','', Attachments, 'Y')
    iPyEmail('toEmail@somesite.com', 'fromEmail@yourSite.com','Image Send Test','Body Text...', Attachments, 'N')

    #Source/Text File Send Test
    Attachments = ['/IFSPATH/YourPythonProg.py']
    iPyEmail('toEmail@somesite.com', 'fromEmail@yourSite.com','Source/Text File Send (as body)','', Attachments, 'Y')
    iPyEmail('toEmail@somesite.com', 'fromEmail@yourSite.com','Source/Text File Send','Body Text...', Attachments, 'N')
    iPyEmail('toEmail@somesite.com', 'fromEmail@yourSite.com','Source/Text File Send (both)','', Attachments, 'B')

    #Multi Attachment Send Test
    Attachments = ['/IFSPATH/IFSFile.HTM', '/IFSPATH/YourPythonProg.py']
    iPyEmail('toEmail@somesite.com', 'fromEmail@yourSite.com','Multi Attachment (as body)','', Attachments, 'Y')
    Attachments = ['/IFSPATH/IFSFile.HTM', '/IFSPATH/images/YourImage.jpg']
    iPyEmail('toEmail@somesite.com', 'fromEmail@yourSite.com','Multi Attachment (all attached)','Body Text...', Attachments, 'N')

if __name__ == "__main__":
    main()