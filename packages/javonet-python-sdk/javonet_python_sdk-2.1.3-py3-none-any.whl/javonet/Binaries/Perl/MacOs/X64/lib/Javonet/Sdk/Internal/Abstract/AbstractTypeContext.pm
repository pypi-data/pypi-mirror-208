package Javonet::Sdk::Internal::Abstract::AbstractTypeContext;
use strict;
use warnings FATAL => 'all';
use Moose;
use Scalar::Util qw( blessed );
use Attribute::Abstract;

sub get_type : Abstract;

no Moose;
1;