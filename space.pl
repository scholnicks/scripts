#!/usr/bin/perl
#
# space:  Calculates disk space in MBs
#
# (c) Steven Scholnick <steve@scholnick.net>
#
# The space source code is published under version 2.1 of the GNU Lesser General Public License</a> (LGPL).
# 
# In brief, this means there's no warranty and you can do anything you like with it.
# However, if you make changes to space and redistribute those changes, 
# then you must publish your modified version under the LGPL. 
#
##################################################################################################################

use strict;
use warnings;

use Cwd;
use File::Find;

print "\n";

if( ! scalar(@ARGV) )
{
	reportSize( cwd() );
}
else
{
	foreach( @ARGV )
	{
		reportSize( $_ );
	}
}

print "\n";

exit 0;

sub reportSize
{
	my $path  = shift;
	my $file  = 0;
	my $sizeb = 0;
	
	&find ( sub { $sizeb += -s }, "$path");
	&find ( sub { $file += 1 },   "$path");
	
	my $sizemb = int ($sizeb / 1024 / 1024);
	
	print "$path = $file files using $sizemb megs of disc space\n";
}
