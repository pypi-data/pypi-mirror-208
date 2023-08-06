package Javonet::Core::Interpreter::Interpreter;
use strict;
use warnings;
use lib 'lib';
use aliased 'Javonet::Core::Handler::PerlHandler' => 'PerlHandler';
use aliased 'Javonet::Core::Protocol::CommandSerializer' => 'CommandSerializer', qw(encode);
use aliased 'Javonet::Core::Protocol::CommandDeserializer' => 'CommandDeserializer', qw(decode);

use Exporter;

our @ISA = qw(Exporter);
our @EXPORT = qw(process execute_);

my $handler = PerlHandler->new();


sub execute_ {
    my $self = shift;
    my $command = shift;
    my $connection_type = shift;
    my $tcp_address = shift;

    require Javonet::Core::Transmitter::PerlTransmitter;
    my $commandSerializer = Javonet::Core::Protocol::CommandSerializer->new();
    my @byte_message = $commandSerializer->encode($command, $connection_type, $tcp_address, 0);
    my @byte_array = Javonet::Core::Transmitter::PerlTransmitter->send_command(\@byte_message);
    my $commandDeserializer = CommandDeserializer->new(\@byte_array);
    my $response_command = $commandDeserializer->decode();
    return $response_command;

}

sub process {
    my ($self, $array_ref) = @_;
    my @byte_array = @$array_ref;
    my $commandDeserializer = CommandDeserializer->new(\@byte_array);
    my $command = $commandDeserializer->decode();
    my $response = $handler->handle_command($command);
    my $commandSerializer = CommandSerializer->new();
    my @byte_message = $commandSerializer->encode($response, 0, 0, 0);
    return @byte_message;
}

1;
