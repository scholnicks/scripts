#!/usr/bin/perl
#
# zap:  kills open application by their name
#
# zap kills open application by their name.  It is different
# than killall in that it can kill an app by just part of the name
#
# (c) Steven Scholnick <steve@scholnick.net>
#
# The zap source code is published under version 2.1 of the GNU Lesser General Public License</a> (LGPL).
# 
# In brief, this means there's no warranty and you can do anything you like with it.
# However, if you make changes to zap and redistribute those changes, 
# then you must publish your modified version under the LGPL. 
#
#############################################################################################################

use strict;
use warnings;

if( scalar(@ARGV) != 1 )
{
	print "Usage : zap <application name>\n\n";
	exit 1;
}

my $app = $ARGV[0];

if( $app =~ /^[0-9]+$/ )
{
	print "zap : invalid application name\n";
	exit 1;
}

# run ps with just pid and command name
# use grep to make the list smaller

open(PS, "ps -o \"pid,command\" -a -x | grep $app  |") or die;

while( <PS> )
{
	if( m|/Applications| )		# a small limitation, it must be in the apps directory
	{
		/([0-9]+) /;
		#print "$_\n";
		kill 9, $1;
		last;
	}
}

close PS;

exit 0;

