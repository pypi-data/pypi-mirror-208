#!/usr/bin/perl
package Javonet::Sdk::Core::RuntimeLib;
use warnings;
use strict;
use Exporter;


our @ISA = qw(Exporter);
our @EXPORT = qw(get_runtime);

my %runtimes = (
    'Clr'       => 0,
    'Go'        => 1,
    'Jvm'       => 2,
    'Netcore'   => 3,
    'Perl'      => 4,
    'Python'    => 5,
    'Ruby'      => 6,
    'Nodejs'        => 7
);

sub get_runtime {
    my $runtime = shift;
    return $runtimes{$runtime};
}

1;
