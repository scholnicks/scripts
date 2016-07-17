#!/usr/bin/perl

# mfc - Music Format Changer
#
# (c) Steven Scholnick <scholnicks@gmail.com>
# The mfc source code is published under a MIT license. See http://www.scholnick.net/license.txt for details.

use strict;
use warnings;

use Cwd;
use Getopt::Long;

my $format = 'mp3';

my $delete = 0;
my $quiet  = 0;

GetOptions(
	'aiff'		=> sub { $format = 'aiff' },
	'delete!'	=> \$delete,
	'help'      => \&help,
	'mp3'       => sub { $format = 'mp3' },
	'ogg'       => sub { $format = 'ogg' },
	'quiet'		=> \$quiet,
	'wav'		=> sub { $format = 'wav' },
) or help();


my %encoders =(
	'aiff'	=> 'sox',
	'mp3'	=> 'lame --nohist',
	'ogg'	=> 'sox',
	'wav'	=> 'sox',
);

foreach (@ARGV) {
   	next if (! /\.(wav|aiff|ogg|mp3)$/);

   	my $inFile  = $_;
	my $outFile = $_;

  	$outFile =~ s/\.(wav|aiff|ogg|mp3)$/\.$format/;

  	print "Converting $inFile to $format\n" if ! $quiet;

	my $command = qq($encoders{$format} "$inFile" "$outFile");

	$command .= " > /dev/null 2>&1" if $quiet;

  	if (system($command) == 0) {
  		unlink $inFile if ($delete);
  	}
  	else {
  		warn "Failed : $?\n";
  	}
}

exit 0;

sub help
{
	print <<EOH;
       mfc help
       --------
--aiff        Convert a WAV file to AIFF
--delete      Delete the input file after conversion
--help        this help screen
--mp3         Convert a WAV or AIFF file to MP3 (Default)
--quiet       quiet mode

EOH
	exit 1;
}
