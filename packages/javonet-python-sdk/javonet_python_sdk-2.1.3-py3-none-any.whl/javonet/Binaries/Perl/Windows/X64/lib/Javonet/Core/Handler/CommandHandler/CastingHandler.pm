package Javonet::Core::Handler::CommandHandler::CastingHandler;
use strict;
use Moose;
use lib 'lib';
use warnings FATAL => 'all';
use aliased 'Javonet::Core::Exception::Exception' => 'Exception';

sub new {
    my $class = shift;
    my $self = {};
    return bless $self, $class;
}

sub process {
    die Exception->new("Explicit cast is forbidden in dynamically typed languages");
}


no Moose;
1;