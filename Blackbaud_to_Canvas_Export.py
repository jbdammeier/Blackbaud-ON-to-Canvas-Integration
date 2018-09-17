#-----------------------------------------------------------------------------------------#
# Name:        Blackbaud_ON_to_Canvas_Export.py                                              #
# Purpose:     Program to pull data from Blackbaud onProduct lists to Kimono for Canvas   #
#              integration using list api call & send to Kimono via sftp                  #
#                                                                                         #                                                                              
# Author:      Justin Dammeier                                                            #
#                                                                                         #
# Created:     8/16/2017                                                                  #
# Copyright:   (c) jdammeier 2018                                                         #
#-----------------------------------------------------------------------------------------#

#The following modules must mbe imported. All are standard python libraies except for Paraminko
import json
from urllib.request import Request, urlopen
import csv
import paramiko
import smtplib
from string import Template
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

def get_bb_token(username,password):
      '''Generates user token. Current method as of 9/16/18. '''
      
      # defining the api-endpoint  
      url = api_endpoint + 'authentication/login'
           
      #set up authetication data to be sent to api 
      auth = {'username':username,
              'password':password}
      params = json.dumps(auth).encode('utf8')

      #make the call
      req = Request(url, data=params,headers={'content-type': 'application/json'})
      response = urlopen(req)

      #get access token
      token_data = json.loads(response.read().decode('utf8'))
      token = token_data.get('Token')
      return (token)

def getInput(file_in):
    '''Opens the file, produces list of lines in the file, removes the header row, and returns the list'''
    inFile = open(file_in)
    inputList = inFile.read().splitlines()
    del inputList[0]
    inFile.close()
    return inputList

def get_bb_file(list_id, file_out):
      '''Converts JSON formatted data from Blackbaud LIST API into csv file. Provde onProduct list ID and final filename'''
      url = api_enpoint + 'api/list/' + list_id + '/?t=' + token
      response = urlopen(url)
      data = json.loads(response.read().decode('utf-8'))

      with open(file_out, 'w', newline= '') as f:
            #Assuming that all dictionaries in the list have the same keys.
            headers = ([k for k, v in sorted(data[0].items())])
            csv_data = [headers]

            for d in data:
                  csv_data.append([d[h] for h in headers])

            writer = csv.writer(f)
            writer.writerows(csv_data)

def course_merge(file_in, file_out, subaccount_id):
    '''Produces Temp CSV for courses and adds the correct SchoolID to the file'''
    outFile = open(file_out, 'w')
    lines = getInput(file_in) #path to input file

    #define & write header row for final CSV
    header = ['CourseID','CourseTitle','SchoolLevel','SchoolID']
    columnHead = ','.join(header)
    outFile.write(columnHead + '\n')

    for line in lines:
          part1 = line[0:]
          final = [part1, subaccount_id]
          result = ','.join(final)
          outFile.write(result + '\n')

    outFile.close()

def ftp_upload(local_path, remote_path):
      #open host
      host = 'kimono.exavault.com' #kimono sftp server or sftp address from Canvas
      port = 22
      transport = paramiko.Transport((host, port))

      #authenticate with username and password obtained from Kimono or Canvas
      username = 'kimono_sftp_username'
      password = 'kimono_sftp_password'
      transport.connect(username = username, password = password)

      #go
      sftp = paramiko.SFTPClient.from_transport(transport)

      #upload
      sftp.put(local_path, remote_path)

      #close
      sftp.close()
      transport.close()

def get_contacts(filename):
    """
    Return two lists names, emails containing names and email addresses
    read from a file specified by filename.
    """
    names = []
    emails = []
    export = []
    with open(filename, mode='r', encoding='utf-8') as contacts_file:
        for a_contact in contacts_file:
            names.append(a_contact.split(',')[0])
            emails.append(a_contact.split(',')[1])
    return names, emails

def read_template(filename):
    """
    Returns a Template object comprising the contents of the file specified by filename.
    """
    
    with open(filename, 'r', encoding='utf-8') as template_file:
        template_file_content = template_file.read()
    return Template(template_file_content)

def send_email(username, password, subject, contacts, message):
    """
    Sends email via google smtp server. Limited to approximately 90 emails per run.
    """
    names, emails = get_contacts(contacts) #read contacts
    message_template = read_template(message) # get message body

    # set up the SMTP (this example uses gmail)
    s = smtplib.SMTP(host='smtp.gmail.com', port=587)
    s.starttls()
    s.login(username, password)

    # For each contact, send the email:
    for name, email in zip(names, emails):
        msg = MIMEMultipart()       # create a message

        # add in the actual person name to the message template
        message = message_template.substitute(PERSON_NAME=name.title(), SUBJECT=subject)

        # setup the parameters of the message
        msg['To']=email
        msg['Subject']=subject
        
        # add in the message body
        msg.attach(MIMEText(message, 'plain'))
        
        # send the message via the smpt connection set up earlier and then deletes the message.
        s.send_message(msg)

        #comment out next line to keep message in the sent folder
        del msg
        
    # Terminate the SMTP session and close the connection
    s.quit()

#-------------------------------------------------------------------------------#
# main program - only edit content below.                                       #
#-------------------------------------------------------------------------------#

#define global variables
token = get_bb_token('username','password') #first parameter is username and second is password of user account with WEB API role
api_endpoint = 'https://#yourschool#.myschoolapp.com/api/' #sets first part of api urls throughout the program


#Build files from Blackbaud onProducts
#First paremeter is Blackbaud advanced list id, second is Path to output file
get_bb_file('00000','C:\Path_to_output_file\STAFF.csv')
get_bb_file('00000','C:\Path_to_output_filefile\STUDENT.csv')
get_bb_file('00000','C:\Path_to_output_filefile\TERM.csv')
get_bb_file('00000','C:\Path_to_output_filefile\COURSE_TEMP.csv')
get_bb_file('00000','C:\Path_to_output_filefile\COURSE_SECTION.csv')
get_bb_file('00000','C:\Path_to_output_filefile\STUDENT_COURSE_SECTION_ENROLLMENT.csv')

#Edit course files
#First parameter is Path to input file, second is path to output file, third is Canvas SIS ID for the subaccount the courses will go into
course_merge('C:\Path_to_input_file\COURSE_TEMP.csv', 'C:\Path_to_output_file\COURSE.csv', '3')

#Send files to Kimono via sftp, comment out to test program before sending files
#only edit first parameter path. filenames should not be edited.
ftp_upload('C:\Path_to_input_file\STAFF.csv', '/STAFF.csv')
ftp_upload('C:\Path_to_input_file\STUDENT.csv', '/STUDENT.csv')
ftp_upload('C:\Path_to_input_file\TERM.csv', '/TERM.csv')
ftp_upload('C:\Path_to_input_file\COURSE.csv', '/COURSE.csv')
ftp_upload('C:\Path_to_input_file\COURSE_SECTION.csv', '/COURSE_SECTION.csv')
ftp_upload('C:\Path_to_input_file\STUDENT_COURSE_SECTION_ENROLLMENT.csv', '/STUDENT_COURSE_SECTION_ENROLLMENT.csv')

#Send email confirmations
#First parameter is email address, Second is Password, Third is Subject, Fourth is contact list, Fifth is message body
send_email('gmail_address', 'password', 'Subject', 'C:\Path_to_file\mycontacts.txt', 'C:\Path_to_file\message.txt')
