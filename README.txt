BLACKBAUD ON to CANVAS INTEGRATION DOCUMENTATION

PYTHON AUTOMATION
The python program is commented in a detailed manner so that anyone with python experience will know what each part of the program does. The template should just be edited for individual instances.
The Windows Task Scheduler is set to run this script every day at 5:00pm (Adjust to 4:00pm during Standard Time). This is approx. ½ hour before the Kimono picks up the information
The program will pull all required information from the specified lists above and export final CSV files to Kimono via SFTP.
It is important that the ON Advanced Lists ARE NOT copied. The list id from Blackbaud ON is how the program pulls the correct information.

ON ADVANCED LISTS & KIMONO FILES: - Organized by Kimono File Name (See Screenshots Folder for examples of the advanced lists configuration in ON)
1. manifest.xml
	Maps our exported data from ON into Kimono Platform
	Is not specific to Canvas or another platform.
2. SCHOOL.csv 
	Static CSV file. Not exported from ON.
	School IDs - Matches sub account ID in Canvas
3. TERM.csv - Exported Nightly
	Kimono Term Export in ON lists
	Set filter for current year terms (School Year.Current is True)
4. STAFF.csv - Exported Nightly
	Kimono Staff Export in ON Lists
	Set filter for role of Non-Teaching Staff or Teacher
	If staff member leaves, role changes so their user will be deleted in Canvas
5. STUDENTS.csv - Exported Nightly
	Kimono Student Export in ON Lists
	Set filter for users with role of student.
6. COURSE.csv - Exported Nightly
	Kimono Course Export in ON
	Set filter for ACTIVE courses
	This is NOT school-year specific
7. COURSE_SECTION.csv - Exported Nightly
	Kimono Course Section Export in ON. 
	Creates course sections & enrolls teachers into sections
	Set filter for courses based on school year & trimester fields
8. STUDENT_COURSE_SECTION_ENROLLMENT.csv - Exported Nightly
	Kimono Student Course Enrollment Export in ON
	Set filter for CURRENT SCHOOL YEAR

End of Year
1. Change Active School year
a. Repository > School Year > Change to Current Year
b. Click Reset Repository

Collections:
1. Nightly as scheduled automatically
2. Manual Collection is possible - Repository > Refresh

Required User Accounts & Kimono Access

Kimono Dashboard:
https://us1.kimonocloud.com

Canvas Kimono Admin Account - Used for OUATH2 token so kimono changes can be pushed to Canvas
Username: XXXXX
PW: XXXXX

Blackbaud Service Account - Used in Python Scripts to authorize ON API
Blackbaud KB on using their API to pull lists: http://on-api.developer.blackbaud.com/API/list/get-listID/
Full Name: Account, Service
Username: XXXXX
Password: XXXXX

Kimono SFTP Information:
Username: XXXXX
Password: XXXXX
Host: sftp://kimono.exavault.com
Port: 22
