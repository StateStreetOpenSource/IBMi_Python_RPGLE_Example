**free
ctl-opt DEBUG bnddir('QC2LE') dftactgrp(*no) actgrp(*caller) option(*SRCSTMT : *NODEBUGIO) GENLVL(10);

//----------------------------------------------------------------------------------------------------
// Copyright (c) 2019 StateStreetOpenSource
// All rights reserved.
//
// Program Name: DEMOEMAIL
// Program Description:  Kick off Python program to create and email a PDF documenting an IBM i file
//
// Redistribution and use in source and binary forms, with or without modification, is permitted
// providing the following conditions are met.
//   1. Redistributions of source code must retain the above copyright notice, this list of
//      conditions and the following disclaimers.
//   2. Redistributions in binary form must reproduce the above copyright notice, this list of
//      conditions and the following disclaimer in documentation provided with the distribution.
//
// This software is only to be used for demo / learning purposes.
// It is NOT intended to be used in a live environment.
//
// THIS SOFTWARE IS PROVIDED BY THE AUTHOR "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES,
// INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A
// PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE AUTHOR OR THE AUTHOR'S EMPLOYER BE
// LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
// (INCLUDING, BUT NOT LIMITED TO, LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION),
// HOWEVER CAUSED (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
// SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
//
// Sample parameters...
// CALL PGM(YOURLIB/DEMOEMAIL) PARM('YOURDTALIB' 'YOURFILE  ' 'YOU@YOUREMAIL.COM             ' 'DEV')
//----------------------------------------------------------------------------------------------------

//____________________________________________________________________________________________________
// *** PROGRAM INPUT DEFINITION  *ENTRY PLIST
//----------------------------------------------------------------------------------------------------
dcl-pr DEMOEMAIL extpgm('DEMOEMAIL');
  @LibName  char(10) const;
  @FileName char(10) const;
  @ToEmail  char(30) const;
  @Env      char(3)  const;
end-pr;
dcl-pi DEMOEMAIL;
  @LibName  char(10) const;
  @FileName char(10) const;
  @ToEmail  char(30) const;
  @Env      char(3)  const;
end-pi;

//___________________________________________
// --External procedures---------------------
dcl-pr SysCmd int(10) extproc('system') ;
  *n pointer value options(*string) ;
end-pr ;

//___________________________________________
// Global Variables and constants------------
dcl-s env char(3) inz('DEV');
dcl-s OpenSrcPathPRD varchar(128) inz('/home/opensource/pysource/prdsrc/');
dcl-s OpenSrcPathDEV varchar(128) inz('/home/opensource/pysource/devsrc/');
dcl-s OpenSrcFile    varchar(30)  inz('demoEmail.sh');
dcl-s OpenSrcPathLOG varchar(128) inz('/home/opensource/logs/');
dcl-s OpenSrcLogFile varchar(30)  inz('demoEmail.log');
dcl-c sq x'7D';

 //____________________________________________________________
 // Check to see required parameters are provided.
 if %parms() > 2;
   if @LibName <> *blanks and @FileName <> *blanks and @ToEmail <> *blanks;
     exsr sRunPython;
   else;
     dsply ('Parms must not be blank!');
   endif;

   // Environment parameter is optional..."DEV" is defaulted when "PRD" isn't provided
   if %parms() > 3;
     if @Env = 'PRD';
       env = 'PRD';
     else;
       env = 'DEV';
     endif;
   endif;

 else;
   dsply ('Library, file, and email needed!');
 endif;

 *inlr = *on;

 //_______________________________________________________________________________________________
 // Executes a Bash script in the requested opensource environment folder. The Bash script starts
 // up the virtual Python environment and passes parameters to the Python program doing the work.
 // Console output is piped to a log file in the IFS to keep the QSHELL screen from showing.
 begsr sRunPython;
   if env = 'PRD';
     SysCmd('QSH CMD(' + sq + OpenSrcPathPRD + OpenSrcFile + ' ' +
            %trim(@libName) + ' ' + %trim(@fileName) + ' PRD ' + %trim(@ToEmail)  +
            ' >>' + OpenSrcPathLOG + OpenSrcLogFile + sq + ')');

   else;
     SysCmd('QSH CMD(' + sq + OpenSrcPathDEV + OpenSrcFile + ' ' +
            %trim(@libName) + ' ' + %trim(@fileName) + ' DEV ' + %trim(@ToEmail)  +
            ' >>' + OpenSrcPathLOG + OpenSrcLogFile + sq + ')');
   endif;
 endsr;