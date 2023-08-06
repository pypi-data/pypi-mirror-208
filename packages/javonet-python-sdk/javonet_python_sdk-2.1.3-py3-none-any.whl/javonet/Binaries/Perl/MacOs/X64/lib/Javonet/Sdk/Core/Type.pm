package Javonet::Sdk::Core::Type;
use strict;
use warnings FATAL => 'all';
use Exporter;

our @ISA = qw(Exporter);
our @EXPORT = qw(get_type);


my %my_type = (
    'Command' => 0,
    'JavonetString' => 1,
    'JavonetInteger' => 2,
    'JavonetBoolean' => 3,
    'JavonetFloat' => 4,
    'JavonetBytes' => 5,
    'JavonetChar' => 6,
    'JavonetLongLong' => 7,
    'JavonetDouble' => 8,
    'JavonetUnsignedLongLong' => 9,
    'JavonetUnsignedInteger' => 10
);

sub get_type {
    my ($self, $type) = @_;
    return $my_type{$type};
}

1;