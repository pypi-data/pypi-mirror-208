package Javonet::Sdk::Internal::InvocationContext;
use strict;
use warnings FATAL => 'all';
use Moose;

use aliased 'Javonet::Core::Handler::PerlHandler' => 'PerlHandler';
use aliased 'Javonet::Core::Interpreter::Interpreter' => 'Interpreter';
use aliased 'Javonet::Core::Exception::ExceptionThrower' => 'ExceptionThrower';

extends 'Javonet::Sdk::Internal::Abstract::AbstractInstanceContext',
    'Javonet::Sdk::Internal::Abstract::AbstractMethodInvocationContext',
    'Javonet::Sdk::Internal::Abstract::AbstractInvocationContext';

my $perl_handler = Javonet::Core::Handler::PerlHandler->new();

sub new {
    my $class = shift;

    my $self = {
        runtime_lib     => shift,
        connection_type => shift,
        tcp_address     => shift,
        current_command => shift,
        isExecuted      => shift
    };

    bless $self, $class;
    return $self;
}

DESTROY {
    my $self = $_[0];

    if ($self->{current_command}->{command_type} == Javonet::Sdk::Core::PerlCommandType::get_command_type('Reference') &&
        $self->{isExecuted} == 1) {
        $self->{current_command} = Javonet::Sdk::Core::PerlCommand->new(
            runtime      => $self->{runtime_lib},
            command_type => Javonet::Sdk::Core::PerlCommandType::get_command_type('DestructReference'),
            payload      => $self->{current_command}->{payload}
        );
        $self->execute();
    }
}

#@override
sub execute {
    my $self = $_[0];
    my $response;
    if ($self->{runtime_lib} == Javonet::Sdk::Core::RuntimeLib::get_runtime('Perl')) {
        $response = $perl_handler->handle_command($self->{current_command});
    }
    else {
        $response = Interpreter->execute_($self->{current_command}, $self->{connection_type}, $self->{tcp_address});
    }

    if ($response->{command_type} == Javonet::Sdk::Core::PerlCommandType::get_command_type('Exception')) {
        ExceptionThrower->throwException($response)
    }

    if ($self->{current_command}->{command_type} == Javonet::Sdk::Core::PerlCommandType::get_command_type('CreateClassInstance')) {
        $self->{current_command} = $response;
        $self->{isExecuted} = 1;
        return $self;
    }

    return Javonet::Sdk::Internal::InvocationContext->new(
        $self->{runtime_lib},
        $self->{connection_type},
        $self->{tcp_address},
        $response,
        1
    );
}


#@override
sub invoke_instance_method {
    my ($self, @arguments) = @_;
    my $command = Javonet::Sdk::Core::PerlCommand->new(
        runtime      => $self->{runtime_lib},
        command_type => Javonet::Sdk::Core::PerlCommandType::get_command_type('InvokeInstanceMethod'),
        payload      => \@arguments
    );
    return Javonet::Sdk::Internal::InvocationContext->new(
        $self->{runtime_lib},
        $self->{connection_type},
        $self->{tcp_address},
        $self->build_command($command),
        0
    );
}

#@override
sub get_instance_field {
    my ($self, @arguments) = @_;
    my $command = Javonet::Sdk::Core::PerlCommand->new(
        runtime      => $self->{runtime_lib},
        command_type => Javonet::Sdk::Core::PerlCommandType::get_command_type('GetInstanceField'),
        payload      => \@arguments
    );
    return Javonet::Sdk::Internal::InvocationContext->new(
        $self->{runtime_lib},
        $self->{connection_type},
        $self->{tcp_address},
        $self->build_command($command),
        0
    );
}

#@override
sub create_instance {
    my ($self, @arguments) = @_;
    my $command = Javonet::Sdk::Core::PerlCommand->new(
        runtime      => $self->{runtime_lib},
        command_type => Javonet::Sdk::Core::PerlCommandType::get_command_type('CreateClassInstance'),
        payload      => \@arguments
    );
    return Javonet::Sdk::Internal::InvocationContext->new(
        $self->{runtime_lib},
        $self->{connection_type},
        $self->{tcp_address},
        $self->build_command($command),
        0
    );
}

#@override
sub invoke_static_method {
    my ($self, @arguments) = @_;
    my $command = Javonet::Sdk::Core::PerlCommand->new(
        runtime      => $self->{runtime_lib},
        command_type => Javonet::Sdk::Core::PerlCommandType::get_command_type('InvokeStaticMethod'),
        payload      => \@arguments
    );
    return Javonet::Sdk::Internal::InvocationContext->new(
        $self->{runtime_lib},
        $self->{connection_type},
        $self->{tcp_address},
        $self->build_command($command),
        0
    );
}

#@override
sub set_generic_type {
}

#@override
sub get_static_field {
    my ($self, @arguments) = @_;
    my $command = Javonet::Sdk::Core::PerlCommand->new(
        runtime      => $self->{runtime_lib},
        command_type => Javonet::Sdk::Core::PerlCommandType::get_command_type('GetStaticField'),
        payload      => \@arguments
    );
    return Javonet::Sdk::Internal::InvocationContext->new(
        $self->{runtime_lib},
        $self->{connection_type},
        $self->{tcp_address},
        $self->build_command($command),
        0
    );
}

#@override
sub set_static_field {
    my ($self, @arguments) = @_;
    my $command = Javonet::Sdk::Core::PerlCommand->new(
        runtime      => $self->{runtime_lib},
        command_type => Javonet::Sdk::Core::PerlCommandType::get_command_type('SetStaticField'),
        payload      => \@arguments
    );
    return Javonet::Sdk::Internal::InvocationContext->new(
        $self->{runtime_lib},
        $self->{connection_type},
        $self->{tcp_address},
        $self->build_command($command),
        0
    );
}

sub get_index {
    my ($self, @arguments) = @_;
    my $command = Javonet::Sdk::Core::PerlCommand->new(
        runtime      => $self->{runtime_lib},
        command_type => Javonet::Sdk::Core::PerlCommandType::get_command_type('ArrayGetItem'),
        payload      => \@arguments
    );
    return Javonet::Sdk::Internal::InvocationContext->new(
        $self->{runtime_lib},
        $self->{connection_type},
        $self->{tcp_address},
        $self->build_command($command),
        0
    );
}

sub get_size {
    my ($self, @arguments) = @_;
    my $command = Javonet::Sdk::Core::PerlCommand->new(
        runtime      => $self->{runtime_lib},
        command_type => Javonet::Sdk::Core::PerlCommandType::get_command_type('ArrayGetSize'),
        payload      => \@arguments
    );
    return Javonet::Sdk::Internal::InvocationContext->new(
        $self->{runtime_lib},
        $self->{connection_type},
        $self->{tcp_address},
        $self->build_command($command),
        0
    );
}

sub get_rank {
    my ($self, @arguments) = @_;
    my $command = Javonet::Sdk::Core::PerlCommand->new(
        runtime      => $self->{runtime_lib},
        command_type => Javonet::Sdk::Core::PerlCommandType::get_command_type('ArrayGetRank'),
        payload      => \@arguments
    );
    return Javonet::Sdk::Internal::InvocationContext->new(
        $self->{runtime_lib},
        $self->{connection_type},
        $self->{tcp_address},
        $self->build_command($command),
        0
    );
}

sub set_index {
    my ($self, @arguments) = @_;
    my $command = Javonet::Sdk::Core::PerlCommand->new(
        runtime      => $self->{runtime_lib},
        command_type => Javonet::Sdk::Core::PerlCommandType::get_command_type('ArraySetSize'),
        payload      => \@arguments
    );
    return Javonet::Sdk::Internal::InvocationContext->new(
        $self->{runtime_lib},
        $self->{connection_type},
        $self->{tcp_address},
        $self->build_command($command),
        0
    );
}

#@override
sub get_value {
    my $self = shift;
    return $self->{current_command}->{payload}[0]
}

sub build_command {
    my ($self, $command) = @_;
    my $command_payload_length = @{$self->{current_command}->{payload}};

    for (my $i = 0; $i < $command_payload_length; $i++) {
        if (blessed($self->{current_command}->{payload}[$i]) and $self->{current_command}->{payload}[$i]->isa('Javonet::Sdk::Internal::InvocationContext')) {
            $self->{current_command}->{payload}[$i] = $self->{current_command}->{payload}[$i]->current_command;
        }
    }

    if (!defined $self->{current_command}) {
        return $command;
    }
    else {
        return $command->add_arg_to_payload_on_beginning($self->{current_command});
    }
}

no Moose;
1;