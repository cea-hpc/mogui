#!/usr/bin/env python3
# Copyright 2008 Marcus D. Hanwell <marcus@cryos.org>
# Minor changes for NUT by Charles Lepple
# Distributed under the terms of the GNU General Public License v2 or later

import re
import os
from textwrap import TextWrapper
import sys
import subprocess

rev_range = "HEAD"

if len(sys.argv) > 1:
    base = sys.argv[1]
    rev_range = "%s..HEAD" % base

# Execute git log with the desired command line options.
# Support Python2 and Python3 (esp. 3.6 and earlier) semantics
# with regard to utf-8 content support (avois ascii decoding in Py3)
fin_mode = 0
# Remove trailing end of line? spitlines() in py3 variant takes care of them
fin_chop = 0
try:
    p = subprocess.Popen(
        [
            "git",
            "log",
            "--pretty=medium",
            "--summary",
            "--stat",
            "--no-merges",
            "--date=short",
            ("%s" % rev_range),
        ],
        encoding="utf-8",
        close_fds=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    fin, ferr = p.communicate()
    if p.wait() != 0:
        print("ERROR getting git changelog")
        sys.exit(1)
    fin = fin.splitlines()
    fin_mode = 3
except TypeError:
    fin = os.popen(
        "git log --pretty=medium --summary --stat --no-merges --date=short %s"
        % rev_range,
        "r",
    )
    fin_mode = 2
    fin_chop = 1

# Create a ChangeLog file in the current directory.
if fin_mode == 3:
    fout = open("ChangeLog", "w", encoding="UTF-8")
else:
    fout = open("ChangeLog", "w")

# Set up the loop variables in order to locate the blocks we want
authorFound = False
dateFound = False
messageFound = False
filesFound = False
message = ""
messageNL = False
files = ""
prevAuthorLine = ""

wrapper = TextWrapper(
    initial_indent="  ",
    subsequent_indent="  ",
    width=78,
    break_on_hyphens=False
)

# The main part of the loop
for line in fin:
    # The commit line marks the start of a new commit object.
    if line.startswith("commit"):
        # Start all over again...
        authorFound = False
        dateFound = False
        messageFound = False
        messageNL = False
        message = ""
        filesFound = False
        files = ""
        continue
    # Match the author line and extract the part we want
    # (Don't use startswith to allow Author override inside commit message.)
    elif "Author:" in line:
        authorList = re.split(": ", line, 1)
        try:
            author = authorList[1]
            author = author[0 : len(author) - fin_chop]
            authorFound = True
        except:
            print("Could not parse authorList = '%s'" % (line))

    # Match the date line
    elif line.startswith("Date:"):
        dateList = re.split(":   ", line, 1)
        try:
            date = dateList[1]
            date = date[0 : len(date) - fin_chop]
            dateFound = True
        except:
            print("Could not parse dateList = '%s'" % (line))
    # The Fossil-IDs are ignored:
    elif line.startswith("    Fossil-ID:") or line.startswith("    [[SVN:"):
        continue
    # The svn-id lines are ignored
    elif "    git-svn-id:" in line:
        continue
    # The sign off line is ignored too
    elif "Signed-off-by" in line:
        continue
    # Extract the actual commit message for this commit
    elif authorFound and dateFound and messageFound is False:
        # Find the commit message if we can
        if len(line) == fin_chop:
            if messageNL:
                messageFound = True
            else:
                messageNL = True
        elif len(line) == 3 + fin_chop:
            messageFound = True
        else:
            if len(message) == 0:
                message = message + line.strip()
            else:
                message = message + " " + line.strip()
    # If this line is hit all of the files have been stored for this commit
    elif re.search("files? changed", line):
        filesFound = True
        continue
    # Collect the files for this commit. FIXME: Still need to add +/- to files
    elif authorFound and dateFound and messageFound:
        fileList = re.split(r' \| ', line, 2)
        if len(fileList) > 1:
            if len(files) > 0:
                files = files + ", " + fileList[0].strip()
            else:
                files = fileList[0].strip()
    # All of the parts of the commit have been found - write out the entry
    if authorFound and dateFound and messageFound and filesFound:
        # First the author line, only outputted if it is the first for that
        # author on this day
        authorLine = date + "  " + author
        if len(prevAuthorLine) == 0:
            fout.write(authorLine + "\n\n")
        elif authorLine == prevAuthorLine:
            pass
        else:
            fout.write("\n" + authorLine + "\n\n")

        # Assemble the actual commit message line(s) and limit the line length
        # to 80 characters.
        # Avoid printing same (or equivalen) filename lists twice, if commit
        # message starts with them.
        if message.startswith(files + ":"):
            commitLine = "* " + message
        else:
            namesF = None
            namesM = None
            try:
                namesM = sorted(re.split(r"[ ,]", message.split(":")[0]))
                namesF = sorted(re.split(r"[ ,]", files))
            except:
                pass

            if namesM is not None and namesM == namesF:
                commitLine = "* " + message
            else:
                commitLine = "* " + files + ": " + message

        # Write out the commit line
        fout.write(wrapper.fill(commitLine) + "\n")

        # Now reset all the variables ready for a new commit block.
        authorFound = False
        dateFound = False
        messageFound = False
        messageNL = False
        message = ""
        filesFound = False
        files = ""
        prevAuthorLine = authorLine

# Close the input and output lines now that we are finished.
if fin_mode == 3:
    p.stdout.close()
    p.stderr.close()
else:
    fin.close()
fout.close()
