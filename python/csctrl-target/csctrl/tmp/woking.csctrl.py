#!/usr/bin/env python
# $Id:$
#
import sys, os, optparse, re
import pwd
import urllib2
import time
import inspect

# The app config file
myCfgFile  = "conf_test.cfg"
# options from command line
options = object

def main(argv):
    "Run command line"
    global options
    global myCfg
    global releaseCfg

    #--------
    # Process command line (in argv)
    usage = "Usage: %s [showconf|gettomcats|deploy]" % (os.path.basename(__file__))

    parser = optparse.OptionParser(usage=usage)
    parser.add_option('-d', '--debug',
        action='store_true', default=False,
        help='display debugging messages')
    options, args = parser.parse_args(argv[1:])

    #--------

    # Read conf file before we do anything
    parse_my_cfg_file(myCfgFile)
    logger("Running in Debug Mode \n", "debug")

    # Check to see if we're the correct user
    check_uid(myCfg['Runas_User'])

    # Read in the release config file
    releaseCfg = parse_release_cfg()

    # Figure out what to do from the args
    #   showconf dumps the config and exits
    #   gettomcats prints the tomcat bases and init scripts
    #   deploy makes svn updates and deploys the code
    # This script does not do tomcat start/stop
    if (len(args) > 0):
        if (args[0] == "showconf"):
            logger("showconf mode", "debug")
            show_config()
        elif (args[0] == "gettomcats"):
            logger("gettomcats mode", "debug")
            get_tomcat_init()
        elif (args[0] == "deploy"):
            logger("deploy mode", "debug")
            logger("Staring deploy")
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
    return  open(file).readline().rstrip('\r\n')

def logger(message, type="normal"):
    "Print messages to the log"

    if (options.__dict__.get("debug")):
        message = "DEBUG: " + message
    elif (type == "debug"):
        return

    with open(myCfg['Logfile'], 'a') as log:
        log.write(time.strftime("[%b %d %Y %H:%M:%S] ") +  message + "\n")

def get_release_cfg_file(file):
    """Determines if the file is local or remote, fetches the file and then
    returns a list of non-blank lines stripped of line ends"""
    if file.startswith("https://"):
        u = urllib2.urlopen(file)
        lines = filter(None, [line.strip() for line in u.readlines()])
    else:
        lines = filter(None, [line.strip() for line in open(file, 'r')])

    return lines

def parse_release_cfg():
    "Returns the release config for the local servers CF role"
    global myCfg
    cfg = {}
    role = 0
    myRole = myCfg['CF_Role']

    if (myCfg['Boxenv'] == 'prod'):
        cfgList = get_release_cfg_file(myCfg['Prod_Release_Config'])
    elif (myCfg['Boxenv'] == 'stage'):
        cfgList = get_release_cfg_file(myCfg['Stage_Release_Config'])
    else: 
        print "Don't know what config file to use"
        exit(-1)

    for line in cfgList:
        li=line.strip()
        if li.startswith("#"):
            continue
        line = line.partition('#')[0]
        match = re.search(r'^\[(.*)\]', line)
        if match:
            role = 0
            type = 0
            roleGrp = match.group(1)
            match = re.search(r',', roleGrp)
            if match:
                roleList = re.split(',', roleGrp)
                for i in roleList:
                    if (i == myCfg['CF_Role']):
                        role = 1
                        continue
            else:
                if (roleGrp == myCfg['CF_Role']):
                    role = 1
                    continue
        else:
            if role:
                match = re.search(r'^:(.*):', line)
                if match:
                    type = match.group(1)
                    continue

                cfg.setdefault(type, []).append(line)

    return cfg

def do_deploy():
    get_current_svn_cfg()
    #update_svn_checkouts()
    #clear_old_deploy_files()
    #copy_new_deploy_files()

def is_it_a(type, path):
    logger(get_func_name() + "()", "debug")
    if (type == "svn"):
        if (os.access(path + "/.svn", os.W_OK)
            and os.path.isdir(path + "/.svn")):
            return(True)
        else:
            return(False)
    elif (type == "dir"):
        if (os.access(path, os.W_OK)
            and os.path.isdir(path)):
            return(True)
        else:
            return(False)
    else:
        print "Don't know how to check %s" % type
        exit(-1)
def check_svn_checkouts():
    "Check the status of the target dir for svn checkouts"
    logger(get_func_name() + "()", "debug")

    global releaseCfg
    coList = []
    upList = []
    badList = []
    exit_flag = 0

    for line in releaseCfg['SVN'] :
        path, checkout, revision = line. split(',')

        if is_it_a("svn", path):
            logger(path + " is a svn checkout")
            upList.append(line)
        elif is_it_a("dir", path):
            logger(path + " is a writable dir")
            coList.append(line)
        else:
            badList.append(line)

    return (coList, upList, badList)


def get_current_svn_cfg():
    global releaseCfg
    xxx = []
    co, up, bad =  check_svn_checkouts()
    if len(co):
        print "co has len"

    if len(xxx):
        print "xxx has len"
    else:
        print "xxx has no len"

    print "co: %s" % len(co)
    print "up: %s" % len(up)
    print "xxx: %s" % len(xxx)

def update_svn_checkouts():
    global releaseCfg
    logger(get_func_name() + "()", "debug")

def clear_old_deploy_files():
    global releaseCfg
    logger(get_func_name() + "()", "debug")

def copy_new_deploy_files():
    global releaseCfg
    logger(get_func_name() + "()", "debug")

def show_config():
    "Shows the config settings for the app and release without doing anything"
    global releaseCfg
    global myCfg
    print "%s Configuration\n" % (os.path.basename(__file__))
    print "Application config settings from %s" % myCfgFile
    for key in sorted(myCfg):
        print "%s: %s" % (key, myCfg[key])

    print "\n=== Release Config for  %s role ===" % myCfg['CF_Role']
    for key, val in releaseCfg.iteritems():
        for ll in val:
            print "%s: %s" % (key, ll)

def get_tomcat_init():
    "Returns the tomcat base and init script for each \
            instance in the release config file"
    global releaseCfg
    for i in releaseCfg['APP']:
        base, init = i.split(',')
        print "%s %s" % (base, init)


if __name__ == '__main__':
    retcode = 0
    try:
	main(sys.argv)
    except KeyboardInterrupt:
	# Could put script cleanup here
	retcode = 1
    sys.exit(retcode)
