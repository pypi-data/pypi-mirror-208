package Javonet::Sdk::Internal::Abstract::AbstractModuleContext;
use strict;
use warnings FATAL => 'all';
use Moose;
use Scalar::Util qw( blessed );
use Attribute::Abstract;

sub load_library : Abstract;

sub get_module : Abstract;

no Moose;
1;