#!/usr/bin/env python
# $Id:$
#
import sys, os, optparse, re, glob, shutil
import pwd
import time
import inspect
from subprocess import Popen, PIPE, STDOUT, call, check_call
from urllib2 import urlopen, URLError, HTTPError

# The app config file
myCfgFile  = "/opt/our/script/bin/csctrl.conf"
# options from command line
options = object

def main(argv):
    "Run command line"
    global options
    global myCfg
    global relCfg

    #--------
    # Process command line (in argv)
    usage = "Usage: %s [showconf|gettomcats|deploy]" % (os.path.basename(__file__))

    parser = optparse.OptionParser(usage=usage)
    parser.add_option('-d', '--debug',
        action='store_true', default=False,
        help='display debugging messages')
    parser.add_option('-f', '--force',
        action='store_true', default=False,
        help='Force is ignored')
    parser.add_option('-r', '--rollback',
        action='store_true', default=False,
        help='Allows deployment to previous versions')
    options, args = parser.parse_args(argv[1:])

    #--------

    # Read conf file before we do anything
    parse_my_cfg_file(myCfgFile)

    # Check to see if we're the correct user
    check_uid(myCfg['Runas_User'])

    # Read in the release config file
    parse_release_cfg()

    # Figure out what to do from the args
    #   showconf        dumps the config and exits
    #   gettomcats      prints the tomcat bases and init scripts
    #   deploy          makes svn updates and deploys the code
    # This script does not do tomcat start/stop

    if (len(args) > 0):
        if (args[0] == "gettomcats"):
            gti_exit = get_tomcat_init()
            exit(gti_exit)

        gsi_exit = get_svn_info()

        if (args[0] == "showconf"):
            show_config()
        elif (args[0] == "deploy"):
            if (options.rollback == True):
                logger("Staring in deploy mode with rollback enabled")
                cfr_exit = 0
            else:
                cfr_exit = check_for_rollback()
                logger("Staring in deploy mode")

            dump_state_to_log()

            if (gsi_exit) :
                print "Aborting deploy. Check log for errors"
                logger("Cannot deploy due to errors while checking svn")
                exit (1)
            elif (cfr_exit):
                print "Aborting deploy. Check log for errors"
                logger("'rollback' is required to update svn to an eariler revision")
                exit (1)
            else:
                do_deploy()
        else:
            parser.print_help()
            exit(-1)
    else:
        parser.print_help()
        exit(-1)

def get_func_name(verbose=False):
    if (verbose) :
        rev = []
        for i in  reversed(inspect.stack()[1:-1]):
            rev.append(i[3]) 
        return ', '.join(rev)
    else:
        return inspect.stack()[1][3]
def dump_state_to_log():
    for type in relCfg.keys():
        if (type == 'SVN'):
            for i in relCfg[type]:

                logger("SVN target dir: %s" % i[0])
                if (i[3] == 'svn'):
                    logger("Current: %s rev %s" % (i[4], i[5]))
                    logger("Release: %s rev %s" % (i[1], i[2]))
                elif (i[3] == 'dir'):
                    logger("Current: Writable directory")
                    logger("Release: %s rev %s" % (i[1], i[2]))
                elif (i[3] == 'bad'):
                    logger("ERROR: Not a writable directory")
                    logger("Release: %s rev %s" % (i[1], i[2]))

def logger(message, type="normal"):
    "Print messages to the log"

    if (options.__dict__.get("debug")):
        message = "DEBUG: " + message
    elif (type == "debug"):
        return

    with open(myCfg['Logfile'], 'a') as log:
        log.write(time.strftime("[%b %d %Y %H:%M:%S] ") +  message + "\n")

def parse_my_cfg_file(file):
    "Read config file and create a global dictionary of settings"
    global myCfg
    myCfg = {}

    lines = filter(None, [line.strip() for line in open(file)])

    for line in lines:
        if line.startswith("#"):
            continue
        k, v = line.split('=', 1)
        k = k.strip()
        v = v.strip()

        match = re.search(r'^"(.*)"$', v)
        if match:
            v = match.group(1)
            
        match = re.search(r'^\'(.*)\'$', v)
        if match:
            v = match.group(1)

        myCfg[k] = v

    # Reset the global value from filename to file contents
    myCfg['CF_Role'] = get_first_line(myCfg['CF_Role'])
    myCfg['Boxenv'] = get_first_line(myCfg['Boxenv'])

def check_uid(runasUser):
    logger(get_func_name() + "()", "debug")
    "Check the UID and change if possible"
    runasUid = pwd.getpwnam(runasUser)[2]
    if (os.getuid() == runasUid):
        return
    elif (os.getuid() == 0):
        os.setuid(runasUid)
    else:
        print "Must be %s  or root to run %s" % (runasUser, os.path.basename(__file__))
        exit(-1)

def get_first_line(file):
    "Returns the first line of a file sans line endings"
    logger(get_func_name() + "()", "debug")
    return  open(file).readline().rstrip('\r\n')

def get_file(file,target=None):
    """Determines if the file is local or remote, fetches the file and then
    returns a list of non-blank lines stripped of line ends or if a target 
    path and name is  is given saves the files as target"""

    logger(get_func_name() + "()", "debug")
    if file.startswith("/"):
        file= "file://" + file
    elif file.startswith("https://") == False and file.startswith("http://") == False:
        print "%s is not an http(s) url or a local path"
        exit(1)

    # Open the url
    try:
        f = urlopen(file)
    except HTTPError, e:
        print "HTTP Error:", e.code, file
    except URLError, e:
        print "URL Error:", e.reason, file

    if (target == None):
    # If no target is specificed; return the cleaned up lines
        lines = filter(None, [line.strip() for line in f.readlines()])
        return lines
    else:
    # Write the contents to a local file 
        with open(target, "wb") as local_file:
            local_file.write(f.read())

def parse_release_cfg():
    "Returns the release config for the local servers CF role"
    logger(get_func_name() + "()", "debug")
    global myCfg
    global relCfg
    relCfg = {}
    role = 0
    myRole = myCfg['CF_Role']

    if (myCfg['Boxenv'] == 'prod'):
        cfgList = get_file(myCfg['Prod_Release_Config'])
    elif (myCfg['Boxenv'] == 'stage'):
        cfgList = get_file(myCfg['Stage_Release_Config'])
    else: 
        print "Don't know what config file to use"
        exit(-1)

    for line in cfgList:
        li=line.strip()
        if li.startswith("#"):
            continue
        # Look for role section
        match = re.search(r'^\[(.*)\]', line)
        if match:
            role = 0
            type = 0
            roleGrp = match.group(1)
            # It is a single role or a list of roles?
            match = re.search(r',', roleGrp)
            if match:
                roleList = re.split(',', roleGrp)
                for i in roleList:
                    # Does role match the server's CF role?
                    if (i == myCfg['CF_Role']):
                        role = 1
                        continue
            else:
                if (roleGrp == myCfg['CF_Role']):
                    role = 1
                    continue
        else:
            if role:
                # Look for TYPE sections
                match = re.search(r'^:(.*):', line)
                if match:
                    type = match.group(1)
                    continue
                # Append the list of values to a list of matches for "type"
                # dict['type'] = list_of_this_type = list_of_values
                relCfg.setdefault(type, []).append(re.split(',', line))

    return relCfg

def do_deploy():
    "Main app flow for the deploy functions"
    logger(get_func_name() + "()", "debug")
    global relCfg
    do_svn_updates()
    undeploy_wars()
    deploy_wars()
    copy_release_files()
    do_prod_rsync()

def do_prod_rsync():
    "Undeploys the webapps by removing everything from the webapps dir \
    and the tomcat cache by deleting out work/Catalina"
    logger(get_func_name() + "()", "debug")
    global relCfg
    rsyncCmd = 'rsync -av --progress /fs/remote/assets/print/sites/ /fs/remote/assets/web/sites/ --exclude "health.html" --exclude "cmyk/" --exclude "*original*" --exclude "*highres*"  --exclude "*.svn*"'
    # If environment is prod && svn == sites checkout
    # run the rsync command

    if (myCfg['Boxenv'] == 'prod') and (myCfg['CF_Role'] in ('cs_web', 'csag_web', 'dc3master2')):
        if relCfg['SVN']:
            print rsyncCmd
            logger("Running command: %s" % rsyncCmd)
            print "Running command: %s" % rsyncCmd
            r = 0
            #r = call(rsyncCmd)
            if r != 0:
                print "Command failed: %s" % rsyncCmd

    else:
        print "No rsync here, either"

def copy_release_files():
    "Main app flow for the deploy functions"
    logger(get_func_name() + "()", "debug")
    global relCfg
    if 'FILE' in relCfg:
        for l in relCfg['FILE'] :
            # Get relerase file(s) and copy to the specified location
            # The FILE convnetion is source_path/file_name, target_path
            # We'll have to add the filename to target_path if we are
            # to use get_file
            #get_file( l[0], l[1]+os.path.basename(l[0]) )
            #get_file( l[0], l[1]+os.path.basename(l[0]) )
            get_file( l[0], l[1] + '/' + os.path.basename(l[0]) )

def deploy_wars():
    "Main app flow for the deploy functions"
    logger(get_func_name() + "()", "debug")
    global relCfg
    if 'WAR' in relCfg:
        for l in relCfg['WAR'] :
            # Get war file(s) and copy to webapps dir
            get_file(l[0], l[1])

def undeploy_wars():
    "Undeploys the webapps by removing everything from the webapps dir \
    and the tomcat cache by deleting out work/Catalina"
    logger(get_func_name() + "()", "debug")
    global relCfg
    if 'APP' in relCfg:
        logger("Undeploying webapps and clearing tomcat cache")
        for l in relCfg['APP'] :
            # Remove everything in the webapps and work (tomcat cache) dirs
            cleanupDirs = [ l[0] + '/work/',  l[0] + "/webapps/" ]
            for dir in cleanupDirs :
                logger("Cleaning up %s" % dir)
                for the_file in os.listdir(dir):
                    file_path = os.path.join(dir, the_file)
                    try:
                        if os.path.isfile(file_path):
                            os.unlink(file_path)
                        else:
                            shutil.rmtree(file_path)
                    except Exception, e:
                        print e
    else:
        logger("No 'APP' defined in the release cfg")
        print "No 'APP' defined in the release cfg"
        exit(1)
        
def check_for_rollback():
    "Check the svn revisions to see if we are rolling back"
    logger(get_func_name() + "()", "debug")
    global relCfg
    if 'SVN' in relCfg:
        for l in relCfg['SVN'] :
            if (l[3] == 'svn') and (l[2] < l[5]): 
                return(1)
    return(0)

def do_svn_updates():
    "Checkout, update or switch the target svn directories as specified in the release config file"
    logger(get_func_name() + "()", "debug")
    global relCfg
    if 'SVN' in relCfg:

        for line in relCfg['SVN'] :
            # [0] TARGET DIR  [1] SVN URL  [2] SVN REVISION  [3] type
            # [4] CURRENT SVN URL  [5] CURRENT SVN REVISION 
            svnCmd = ["svn", "co", line[1], "-r", line[2], line[0]]
            if (line[3] == 'dir'):
                svnCmd[1] = "co"
            elif (line[3] == 'svn'): 
                if (line[1] == line[4]) and (line[2] == line[5]):
                    logger("%s is up to date" % line[0])
                    continue
                elif (line[1] == line[4]):
                    svnCmd[1] = "update"
                else:
                    svnCmd[1] = "switch"
            else:
                print "I don't know how to update svn for %s" % line
                exit(1)

            logger("Running command: %s" % ' '.join(svnCmd))
            r = call(svnCmd)
            if r != 0:
                print "Command failed: %s" % svnCmd
                exit(r)
    else:
        logger("No SVN checkouts defined in the release cfg")
        print "No SVN checkouts defined in the release cfg"
        exit(1)

def get_svn_info():
    "Check the status of the target directories for svn checkouts"
    logger(get_func_name() + "()", "debug")
    global relCfg
    exit_status = 0

    if 'SVN' in relCfg:
        for line in relCfg['SVN'] :
            if (os.access(line[0] + "/.svn", os.W_OK)
                and os.path.isdir(line[0] + "/.svn")):
                line.append('svn')
                p = Popen( ('/usr/bin/svn info ' + line[0]), shell=True, stdout=PIPE).stdout
                plines = filter(None, [pline.strip() for pline in p.readlines()])
                for pline in plines:
                    k, v = re.split(': ', pline, 1)
                    if (k == 'URL'):
                        line.append(v)
                    if (k == 'Revision'):
                        line.append(v)

            elif (os.access(line[0], os.W_OK)
                and os.path.isdir(line[0])):
                line.append('dir')
            else:
                line.append('bad')
                exit_status = -1
    else:
        exit_status = -1

    return exit_status

def show_config():
    "Shows the config settings for the app and release without doing anything"
    logger(get_func_name() + "()", "debug")
    global relCfg
    global myCfg
    print "%s Configuration\n" % (os.path.basename(__file__))
    print "Application config settings from %s" % myCfgFile
    for key in sorted(myCfg):
        print "%s: %s" % (key, myCfg[key])

    print "\n=== Release Config for  %s role ===" % myCfg['CF_Role']
    for type in relCfg.keys():
        if (type == 'SVN'):
            for i in relCfg[type]:
                print "SVN target dir: %s" % i[0]
                if (i[3] == 'svn'):
                    print "Current: %s rev %s" % (i[4], i[5])
                    print "Release: %s rev %s" % (i[1], i[2])
                elif (i[3] == 'dir'):
                    print "Current: Writable directory"
                    print "Release: %s rev %s" % (i[1], i[2])
                elif (i[3] == 'bad'):
                    print "Current: Not a writable directory"
                    print "Release: %s rev %s" % (i[1], i[2])
                print ""

        else:
            for i in relCfg[type]:
                print "%s %s" % (type, ' '.join(i))
                print ""

def get_tomcat_init():
    "Returns the tomcat base and init script for each \
            instance in the release config file"
    logger(get_func_name() + "()", "debug")
    global relCfg
    if 'APP' in relCfg:
        for i in relCfg['APP']:
            print ' '.join(i)
            return(0)
    else:
        return(-1)

if __name__ == '__main__':
    retcode = 0
    try:
	main(sys.argv)
    except KeyboardInterrupt:
	# Could put script cleanup here
	retcode = 1
    sys.exit(retcode)
