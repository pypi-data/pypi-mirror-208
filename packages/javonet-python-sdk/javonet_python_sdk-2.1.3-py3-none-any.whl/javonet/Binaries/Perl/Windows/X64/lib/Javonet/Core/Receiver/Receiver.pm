package Javonet::Core::Receiver::Receiver;
use utf8;
use strict;
use warnings;
use Exporter;
use Config;
use File::Basename;

my $perlLibDirJavonet;
my $perlLibDirDeps;

BEGIN {
    my $thisFileDir = dirname(__FILE__);
    $perlLibDirJavonet = "$thisFileDir/../../../";
    $perlLibDirDeps = "$thisFileDir/../../../../deps/lib/perl5"
}

use lib "$perlLibDirJavonet";
use lib "$perlLibDirDeps";

use aliased 'Javonet::Core::Interpreter::Interpreter' => 'Interpreter', qw(process);

our @ISA = qw(Exporter);
our @EXPORT = qw(send_command heart_beat);

sub heart_beat {
    my (@byte_array) = @_;
    my $response = "10";
    return $response;
}

sub send_command {
    my ($byte_array_as_string) = @_;
    my @byte_array = unpack("C*", Encode::encode("ascii", $byte_array_as_string));
    my @response = Interpreter->process(\@byte_array);
    return join '', map chr, @response;
}

1;
