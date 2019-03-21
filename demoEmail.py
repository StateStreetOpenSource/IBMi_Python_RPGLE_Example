#!/usr/bin/env python3
'''
----------------------------------------------------------------------------------------------------
 Copyright (c) 2019 StateStreetOpenSource
 All rights reserved.

 Program Name: demoEmail.py
 Program Description:  Example Python program to create and email a PDF documenting an IBM i file

 Redistribution of this code, with or without modification, is permitted providing the following
 conditions are met.
   1. Redistributions of source code must retain the above copyright notice, this list of
      conditions and the following disclaimers.

 This software is only to be used for demo / learning purposes.
 It is NOT intended to be used in a live environment.

 THIS SOFTWARE IS PROVIDED BY THE AUTHOR "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES,
 INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A
 PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE AUTHOR OR THE AUTHOR'S EMPLOYER BE
 LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
 (INCLUDING, BUT NOT LIMITED TO, LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION),
 HOWEVER CAUSED (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
 SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

 Sample execution...
 python3 demoEmail.py YOURLIB YOURFILE DEV YOU@YOUREMAIL.COM 
 python3 demoEmail.py QSYS2 SYSCOLUMNS DEV YOU@YOUREMAIL.COM 
----------------------------------------------------------------------------------------------------
'''

from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Spacer, Image
from reportlab.lib.enums import TA_JUSTIFY, TA_RIGHT
from reportlab.lib.pagesizes import letter, portrait,landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle, TA_CENTER, TA_LEFT
from reportlab.lib import colors
from reportlab.rl_config import defaultPageSize
from reportlab.lib.units import inch, cm
import datetime
from sys import argv

#Custom Utilities
from dbconn import db2conn
from ipyemail import iPyEmail

#_______________________________________________________________________________________________________
scriptName, libName, fileName, environment, toEmail = argv
CenterParagraph = ParagraphStyle(name="centered", alignment=TA_CENTER)
LeftParagraph   = ParagraphStyle(name="left", alignment=TA_LEFT)        
sdate = datetime.date.today().strftime("%B %d, %Y")
styles = getSampleStyleSheet()
styles.wordWrap = 'CJK'
blanks = "                                            "

#_______________________________
# Page header for the first page
def myFirstPage(canvas, doc):
    canvas.saveState()
    canvas.setPageSize([11*inch, 8.5*inch])
    canvas.setFont('Times-Roman',12)
    canvas.drawImage('./openSource.jpg', 18,560, width=3.8 * cm, height=0.8 * cm)    
    canvas.drawString(28, 540,  "Table: " + table_description + blanks + sdate)
    canvas.restoreState()   
    canvas.translate(-0.5*inch, 0*inch)
    
#_______________________________________________________
# Page header with page number on all but the first page
def myLaterPages(canvas, doc):
    canvas.saveState()
    canvas.setPageSize([11*inch, 8.5*inch])
    canvas.setFont('Times-Roman',12)
    canvas.drawImage('./openSource.jpg', 18,560, width=3.8 * cm, height=0.8 * cm)    
    canvas.drawString(28, 540,  "Table: " + table_description + blanks + sdate + blanks + "Page %d" % (doc.page))   
    canvas.restoreState()   
    canvas.translate(-0.5*inch, 0*inch) 
    
#____________________________________________________________
# Get the table's description
def getTableDesc():
    
    table_description = " "
    
    # Open the connection for the SQL access
    try:
        c1, conn = db2conn()
    except:
        return False, "Bad SQL Connection!" 
        
    # Table Description
    sqlstr = ("SELECT TABLE_TEXT FROM QSYS2.SYSTABLES WHERE TABLE_SCHEMA = ? and TABLE_NAME = ?")
    
    try:        
        c1.execute(sqlstr, (libName, fileName))        
    except:
        conn.close()
        return False, "Bad SQL Statement!"
    
    try:
        row_data = c1.fetchone()
        table_description = (libName + "/" + fileName + " - " + row_data[0])
        
    except:
        return False, "Table not Found!"
        
    try:
        conn.close()
    except:
        return True, table_description
        
    return True, table_description
        
#________________________________
# Field listing for the given file
def getReptDtl(): 
    
    # Define the row, column, and table style to use
    style = TableStyle([('ALIGN',(0,0),(0,-1),'RIGHT'),
                        ('ALIGN',(1,0),(1,-1),'LEFT'),                    
                        ('ALIGN',(2,0),(2,-1),'LEFT'),                                     
                        ('ALIGN',(3,0),(3,-1),'LEFT'),                                        
                        ('ALIGN',(4,0),(4,-1),'LEFT'),                                        
                        ('VALIGN',(0,0),(-1,-1),'MIDDLE'),                                      
                        ('TEXTCOLOR',(0,0),(4,0),colors.blue),
                        ('INNERGRID', (0,0), (-1,-1), 0.25, colors.black),
                        ('BOX', (0,0), (-1,-1), 0.25, colors.black),])
                        
    # Create an empty table...
    table_data = []
    
    # Add column headers to the table
    table_data.append(["Field No.", "Long Field Name", "Sys Field Name", "Field Heading/Text", "Data Type"])

    # Open the connection for the SQL access
    try:
        c1, conn = db2conn()
    except:
        return "Bad SQL Connection!"
        
    # Fields and data information             
    sqlstr = ("SELECT ORDINAL_POSITION, COLUMN_NAME, SYSTEM_COLUMN_NAME, coalesce(COLUMN_TEXT, ' '), " +
                  "cast(case " +
                          "when CHARACTER_MAXIMUM_LENGTH > 0 then " +
                            "(DATA_TYPE || '(' || rtrim(char(CHARACTER_MAXIMUM_LENGTH)) || ')') " +
                          "when (DATA_TYPE = 'INTEGER' or DATA_TYPE = 'SMALLINT' or DATA_TYPE = 'BIGINT') then " +
                            "(DATA_TYPE || '(' || rtrim(char(NUMERIC_PRECISION)) || ')') " +
                          "when NUMERIC_PRECISION > 0 then " +
                            "(DATA_TYPE || '(' || rtrim(char(NUMERIC_PRECISION))) || coalesce( (',' || " +
                            "rtrim(char(NUMERIC_SCALE)) ||')') , ')') " +
                          "else DATA_TYPE " +
                       "end as VARCHAR(40) CCSID 37) AS DATATYPE, COLUMN_HEADING " +
              "FROM QSYS2.SYSCOLUMNS " +
              "WHERE TABLE_SCHEMA=? and TABLE_NAME=? " +
              "ORDER BY ORDINAL_POSITION")

    try:        
        # Execute the query and return results for the given library and file
        c1.execute(sqlstr, (libName, fileName))        
        
        try:       
            
            # Loop through all fields defined in the table
            for row in c1.fetchall():
                field_num        = row[0]
                longField_name   = row[1]
                sysField_name    = row[2]
                data_type        = row[4]

                # No use showing both column heading and column text if they're the same                
                if row[5].strip() == row[3].strip():
                    col_Text_Heading = row[5].strip() 
                else:
                    # Paragraph needed to allow adding HTML tags into table cells               
                    col_Text_Heading = Paragraph(row[5].strip() + "<br/>" + row[3].strip(), LeftParagraph)              
                
                # Add the SQL record just read to the table
                table_data.append([field_num, longField_name, sysField_name, col_Text_Heading, data_type])
            
        except:
            conn.close()
            return "SQL Fetch Error!!!"  

    except:
        conn.close()
        return "Bad SQL Statement!"
        
    try:
        conn.close()
    except:
        return "DB Connection Wasn't Closed"         
            

    # Finalize the table build
    t= Table(table_data, repeatRows=1, hAlign='LEFT',colWidths=(0.7*inch, 2.5*inch, 1.2*inch, 3.0*inch, 2.0*inch))   
       
    # Finalize the table styling
    t.setStyle(style)
    
    # Add the table to the document
    story.append(t)
    
    return "Detail finished"

#________________________________
# Report footer..only printed once at end of report
def getReptFtr():    
    if environment != 'PRD':
        p = Paragraph(("<br/><B><U>****T E S T I N G ****</U></B><br/><br/>"), CenterParagraph)
        story.append(p)
        
    return "Report finished"
    
#_________________________________________
# Control building of the document's parts
def buildReport():
    try:       
        print(getReptDtl())
        print(getReptFtr())
        
        #__S T O R E   P D F   N O W________________________________________
        doc.build(story, onFirstPage=myFirstPage, onLaterPages=myLaterPages)
        return True
        
    except:
        return False
#_________________________________________________________________
# Use custom wrappers over standard Python email related libraries
def emailReport():
    try:       
        fromEmail = toEmail.strip()
        subject = ("PDF test and documentation for file " + libName + "/" + fileName)
        Attachments = [docName]
        
        # Custom wrapper over standard Python email related libraries       
        iPyEmail(toEmail.strip(), fromEmail, subject, '', Attachments, 'N')
        
    except:
        print("Email send failure!")
        
#__________________________________________________________________________
# Create document in IFS to build the PDF
tableExists, table_description = getTableDesc()

if tableExists == True:
    docName = "./demo_Email.pdf"
    doc = SimpleDocTemplate(docName, rightMargin=72, leftMargin=72, topMargin=72, 
                            bottomMargin=36, pagesize=landscape(letter))

    # Create an empty space to add document components
    story = []

    # Procedure to control the document build
    if buildReport() == True:
        emailReport()
else:
    print("Table doesn't exist!")

