#!/usr/bin/perl
#
# space:  Calculates disk space in MBs
#
# (c) Steven Scholnick <scholnicks@gmail.com>
# The space source code is published under a MIT license.

use strict;
use warnings;

use Cwd;
use File::Find;

print "\n";

if (! scalar(@ARGV) ) {
	reportSize( cwd() );
}
else {
	foreach (@ARGV) {
		reportSize($_);
	}
}

print "\n";

exit 0;

sub reportSize {
	my $path  = shift;
	my $file  = 0;
	my $sizeb = 0;

	&find ( sub { $sizeb += -s }, "$path");
	&find ( sub { $file += 1 },   "$path");

	my $sizemb = int ($sizeb / 1024 / 1024);

	print "$path = $file files using $sizemb megs of disk space\n";
}
