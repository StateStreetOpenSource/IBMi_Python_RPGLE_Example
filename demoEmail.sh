#!/QOpenSys/pkgs/bin/bash
# Program: demoEmail.sh
# This calls a Python program to create a PDF documenting a file and it's fields

#  THIS SCRIPT IS USED BY RPGLE PROGRAM DEMOEMAIL
#              D. Thierman 2019-03-13                     

libName=$1
fileName=$2
environment=$3
toEmail=$4
if [ $# -gt 3 ] 
then
    # Make sure script has access to the open source binaries
    PATH=/QOpenSys/pkgs/bin:$PATH
	
    # Activate the Python 3.6.8 virtual environment	
    cd /home/opensource/pysource/v368/
    source /home/opensource/pysource/v368/bin/activate
	
    # Run the Python script from the requested evironment, passing along the required parameters	
    if [ $environment == 'PRD' ]; then
        cd /home/opensource/pysource/prdsrc/
        python3 /home/opensource/pysource/prdsrc/demoEmail.py $libName $fileName $environment $toEmail
    else
        cd /home/opensource/pysource/devsrc/
        python3 /home/opensource/pysource/devsrc/demoEmail.py $libName $fileName $environment $toEmail
    fi
    deactivate  
	
else
    echo Library, file name, environment, and to email are needed!
fi
