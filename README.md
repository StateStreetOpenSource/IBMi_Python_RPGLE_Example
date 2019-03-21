# IBMi_Python_RPGLE_Example
Demonstrate a method to run a Python script from an IBMi RPGLE program. This example uses Python (launched by RPG) to create basic file documentation and email it (also Python) to the provided mail address.

1)	Create your python program and test it so that it works from the “open source” command line
	i.	See… demoEmail.py and supporting Python scripts… dbconn.py and ipyemail.py

2)	Create a Bash script that does the following
	a.	Receive parameters from the RPGLE/CLLE program that’s calling this script
	b.	Adjust the “PATH” so that the open source binaries can be accessed
	c.	“Activate” the Python virtual environment
	d.	Using the environment parameter, change your current directory to the IFS folder containing your Python sources
	e.	Execute your Python script, passing along any needed parameters
	f.	Deactivate your virtual environment and exit
	g.	See… demoEmail.sh

3)	Create your RPGLE or CLLE program that does the following
	a.	Using either QCMDEXC or the ILE C “system” function, execute your Bash program with Qshell (QSH).
		i.	This program should determine the environment it’s running in. The environment variable can then be used for the following:
			1.	Ensure the Bash script is run from the intended production or development IFS source folders.
			2.	The Bash script can then run the Python script from the intended production or development IFS source folders.
			3.	The Python program can use the environment information in their SQL “From” statements to pull data from the correct libraries. 
			
		ii.	Pipe “>>” the console to a log file in the IFS so that the Qshell screen isn’t opened. Any output from errors or print statements will then be directed to the log file.
		
	b.	See… DEMOEMAIL.RPGLE
