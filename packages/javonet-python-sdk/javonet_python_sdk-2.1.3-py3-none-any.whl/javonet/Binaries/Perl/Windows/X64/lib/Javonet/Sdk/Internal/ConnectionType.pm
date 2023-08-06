package Javonet::Sdk::Internal::ConnectionType;
use strict;
use warnings FATAL => 'all';
use Exporter;
use Moose;

our @ISA = qw(Exporter);
our @EXPORT = qw(get_connection_type);


my %connection_type = (
    'InMemory'       => 0,
    'Tcp'    => 1
);

sub get_connection_type {
    my $type = shift;
    return $connection_type{$type};
}


no Moose;
1;