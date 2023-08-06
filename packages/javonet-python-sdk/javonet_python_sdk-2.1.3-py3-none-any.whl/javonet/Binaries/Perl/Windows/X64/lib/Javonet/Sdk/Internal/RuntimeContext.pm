package Javonet::Sdk::Internal::RuntimeContext;
use strict;
use warnings FATAL => 'all';
use Moose;
use aliased 'Javonet::Sdk::Core::PerlCommand' => 'PerlCommand';
use aliased 'Javonet::Sdk::Internal::InvocationContext' => 'InvocationContext';
use aliased 'Javonet::Core::Handler::PerlHandler' => 'PerlHandler';
use aliased 'Javonet::Core::Interpreter::Interpreter' => 'Interpreter';
use aliased 'Javonet::Core::Exception::ExceptionThrower' => 'ExceptionThrower';

extends 'Javonet::Sdk::Internal::Abstract::AbstractModuleContext',
    'Javonet::Sdk::Internal::Abstract::AbstractTypeContext';

my $perl_handler = Javonet::Core::Handler::PerlHandler->new();
our %memoryRuntimeContexts;
our %networkRuntimeContexts;

#@override
sub new {
    my $class = shift;

    my $self = {
        runtime_lib     => shift,
        connection_type => shift,
        tcp_address     => shift
    };
    bless $self, $class;
    return $self;
}

sub get_instance {
    my $runtime_lib = shift;
    my $connection_type = shift;
    my $tcp_address = shift;
    if($connection_type eq Javonet::Sdk::Internal::ConnectionType::get_connection_type("Tcp") && $tcp_address ne "") {
        if(exists $networkRuntimeContexts{$tcp_address}) {
            my $runtimeCtx = $networkRuntimeContexts{$tcp_address};
            $runtimeCtx->{current_command} = undef();
            return $runtimeCtx;
        }
        else {
            my $runtimeCtx = Javonet::Sdk::Internal::RuntimeContext->new($runtime_lib, $connection_type, $tcp_address);
            $networkRuntimeContexts{$tcp_address} = $runtimeCtx;
            return($runtimeCtx);
        }
    }
    else {
        if(exists $memoryRuntimeContexts{$runtime_lib}) {
            my $runtimeCtx = $memoryRuntimeContexts{$runtime_lib};
            $runtimeCtx->{current_command} = undef();
            return $runtimeCtx;
        }
        else {
            my $runtimeCtx = Javonet::Sdk::Internal::RuntimeContext->new($runtime_lib, $connection_type, '');
            $memoryRuntimeContexts{$runtime_lib} = $runtimeCtx;
            return($runtimeCtx);
        }
    }
}


sub execute {
    my $command = shift;
    my $connection_type = shift;
    my $tcp_address = shift;
    my $response;
    if($command->{runtime} eq Javonet::Sdk::Core::RuntimeLib::get_runtime('Perl')) {
        $response = $perl_handler->handle_command($command);
    }
    else{
        $response = Interpreter->execute_($command, $connection_type, $tcp_address);
    }
    if ($response->{command_type} == Javonet::Sdk::Core::PerlCommandType::get_command_type('Exception')) {
        ExceptionThrower->throwException($response)
    }
}


#@override
sub load_library {
    my $self = shift;
    my @load_library_parameters = @_;

    my $command = PerlCommand->new(
        runtime => $self->{runtime_lib},
        command_type => Javonet::Sdk::Core::PerlCommandType::get_command_type('LoadLibrary'),
        payload => \@load_library_parameters
    );

    execute($command, $self->{connection_type}, $self->{tcp_address});
    return $self;
}

#@override
sub get_type {
    my $self = shift;
    my @arguments = @_;

    my $command = PerlCommand->new(
        runtime => $self->{runtime_lib},
        command_type => Javonet::Sdk::Core::PerlCommandType::get_command_type('GetType'),
        payload => \@arguments
    );

    return Javonet::Sdk::Internal::InvocationContext->new(
        $self->{runtime_lib},
        $self->{connection_type},
        $self->{tcp_address},
        $self->build_command($command),
        0
    );
}

sub build_command {
    my $self = shift;
    my $command = shift;

    if(!defined $self->{current_command}){
        return $command;
    }
    else{
        return $command->add_arg_to_payload_on_beginning($self->{current_command});
    }
}


no Moose;
1;