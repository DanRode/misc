#!/usr/bin/env perl
# $Id:$
#
# Template for webops perl scripts. Copy to desired script name (drop the
# .pl suffix). Remove sections that you do not need.
#

use strict;
use warnings;

#----------------------------------------------------------------------
package Script;

use English (-no_match_vars);
use Getopt::Long;
use vars qw($testrun);

#----------------------------------------------------------------------

my $help = 0;
my $testrun = 0;
my $rollback = 0;
my $check = 0;
my $Tag;
my $Rev;
my $Dir;

# Run command line
Getopt::Long::Configure("require_order");
GetOptions(
	'dir=s' => \$Dir,
	'revision=i' => \$Rev,
	'tag=s' => \$Tag,
	'testrun' => \$testrun,
	'check' => \$check,
	'rollback' => \$rollback,
	'help|h' => \$help,
	) or Usage(2);
Usage(1) if ($help);
Usage(-exitstatus => 0, -verbose => 2) if ($help);
Usage(2) unless ($Tag && $Rev && $Dir);

if ($check) { &svnCheck($Tag,$Rev,$Dir); }
my $svnStatus = &isItSvn($Dir);

open (LOG, ">>", "/var/log/cs-update-svn.log") or die $!;
print LOG `date`;
# Looks like an svn checkout.  Try to update it
if ($svnStatus == 0 ) { 
    print LOG "$Dir is an svn checkout.\n";
    &doSvnUpdate($Tag, $Rev, $Dir);
}
# Looks like it's a dir but not an svn checkout. Try to do a fresh checkout
elsif ($svnStatus == 1 ) { 
    print LOG "$Dir is not an svn checkout. Trying a fresh checkout\n";
    &doSvnUpdate($Tag, $Rev, $Dir, 1);
}
# Looks like it exists but is not a dir.
elsif ($svnStatus == 2 ) { 
    print LOG "ERROR: $Dir is not a directory. Exiting\n"; 
    exit "$Dir is not a dir\n"; }
# Looks like the dir does not exist
elsif ($svnStatus == 3 ) { 
    print LOG "ERROR: $Dir Does not exist. Exiting\n"; 
    exit "$Dir does not exist\n"; }

print LOG "\n";
close LOG;
sub Main() {
}

sub Usage {
    require Pod::Usage;
    Pod::Usage::pod2usage(@_);
}

sub isItSvn {
# Return codes
#   0 - Appears to be under svn control
#   1 - A dir not under svn control
#   2 - Exists but not a dir
#   3 - Doesn't exist
    exit "No path given" unless $_[0];
    if ( -d "$_[0]/.svn") {return(0);}
    elsif ( -d "$_[0]")   {return(1);}
    elsif ( -e "$_[0]")   {return(2);}
    else                  {return(3);}
}
# Give a path, get back a tag and revision
sub getSvnRev {
    my $cTag;
    my $cRev;  # revision number
    exit "No path given" unless $_[0];
    my @lines = `svn info $_[0] 2>/dev/null`;
    chomp @lines;
    for my $line (@lines) {
	next if ($line =~ /^s*$/);
	my ($name, $value) = split(/:\s/,$line);
	if ($name eq "URL") {
	    $cTag = $value;
	}
	if ($name eq "Revision") {
	    $cRev = $value;
	}
    }
    return($cTag, $cRev);
}
sub doSvnUpdate {
    exit "doSvnUpdate requires svn url, revision and target dir" unless $_[2];
    my $Tag = $_[0];
    my $Rev = $_[1];
    my $Dir = $_[2];
    my $svnCmd;
    my $skip;
    my $cTag = "none"; 
    my $cRev = "none";
    ($cTag, $cRev) = &getSvnRev("$Dir") unless $_[3];
    if ($_[3]) { $svnCmd = "svn co $Tag -r $Rev $Dir";}
    elsif ($Tag eq $cTag && $Rev eq $cRev ) {$skip=1;}
    elsif ($Tag ne $cTag) { $svnCmd = "svn switch $Tag -r $Rev $Dir"; } 
    else { $svnCmd = "svn update $Tag -r $Rev $Dir"; }

    if ($skip) {
	print LOG "$Dir is up to date at:\n$cTag rev $cRev\n";
	print LOG "No updates required\n";
	return;
    }
    else {
	if ($testrun) { 
	    print "DRY RUN\n";
	    print "CURRENT $Dir is $cTag revision $cRev\n";
	    print "WANTED $Tag revision $Rev\n";
	    print "COMMAND $svnCmd\n"; 
	}
	else { 
	    print LOG "$Dir is $cTag revision $cRev\n";
	    print LOG "Updating to $Tag revision $Rev\nCommand: $svnCmd"; 
	    `$svnCmd`; 
	}

    }
    
}

sub svnCheck {
    die "svnCheck requires svn url, revision and target dir" unless $_[2];
    my $Tag = $_[0];
    my $Rev = $_[1];
    my $Dir = $_[2];
    my $cTag = "none"; 
    my $cRev = "none";
    
    if (&isItSvn($Dir) != 0 ) {
	print "$Dir is not an SVN checkout\n";
	exit (1);
    }

    ($cTag, $cRev) = &getSvnRev("$Dir");
    if (!$rollback && $Rev < $cRev) {
	print "Cannot revert $Dir from $cRev to $Rev without --rollback\n";
	exit(2)
    }
    if ($Tag eq $cTag && $Rev eq $cRev ) {
	print "$Dir is up to date\n";
	exit(0);
    }
    else {
	print "$Dir is not up to date\n";
	exit(3);
    }
}

package main;

import Script;
use English (-no_match_vars);

# Process command line if this is the main program (not used as module)
if ($PROGRAM_NAME eq __FILE__) {
    Script::Main();
    exit(0);
}

1;
__END__

=head1 NAME

cs-update-svn.pl

=head1 SYNOPSIS

cs-update-svn.pl --dir TARGET_DIR --tag SVN_TAG_NAME  --rev SVN_REV [--testrun --help]

=head1 OPTIONS
--dir, d
The local directory for the checkout or update.

--revision, -r
The revision of the svn tag.

--tag, -t
The name of the svn tag.

--testrun
Print the update commands but do not execute.

--help, -h
Display man page.


=head1 DESCRIPTION

Updates https://subversion.ops.ag.com/repos/cs/fs/tags/<TAG_NAME>/conf to the
specified subversion tag and revision in /fs/conf/.

This script will perform an svn checkout, switch or update of /fs/conf from
https://subversion.ops.ag.com/repos/cs/fs/tags/<TAG_NAME>/conf depending on
the current state of /fs/conf.


=head1 FILES

None

=cut
