package Javonet::Sdk::Internal::RuntimeFactory;
use strict;
use warnings FATAL => 'all';
use Moose;
use aliased 'Javonet::Sdk::Internal::RuntimeContext' => 'RuntimeContext';
extends 'Javonet::Sdk::Internal::Abstract::AbstractRuntimeFactory';

my $connection_type;
my $tcp_address;

#@override
sub new {
    my $class = shift;
    my $self = {
        connection_type => shift,
        tcp_address     => shift
    };
    $connection_type = $self->{connection_type};
    $tcp_address = $self->{tcp_address};
    if($connection_type eq Javonet::Sdk::Internal::ConnectionType::get_connection_type('Tcp')){
        if(not( defined $tcp_address || $tcp_address eq "" )){
            die("Error: Tcp ip address must be specified");
        }
    }
    bless $self, $class;

    return $self;
}


#@override
sub clr {
    return Javonet::Sdk::Internal::RuntimeContext::get_instance(
        Javonet::Sdk::Core::RuntimeLib::get_runtime('Clr'),
        $connection_type,
        $tcp_address
    );
}

#@override
sub go {
    return Javonet::Sdk::Internal::RuntimeContext::get_instance(
        Javonet::Sdk::Core::RuntimeLib::get_runtime('Go'),
        $connection_type,
        $tcp_address
    );
}

#@override
sub jvm {
    return Javonet::Sdk::Internal::RuntimeContext::get_instance(
        Javonet::Sdk::Core::RuntimeLib::get_runtime('Jvm'),
        $connection_type,
        $tcp_address
    );
}

#@override
sub netcore {
    return Javonet::Sdk::Internal::RuntimeContext::get_instance(
        Javonet::Sdk::Core::RuntimeLib::get_runtime('Netcore'),
        $connection_type,
        $tcp_address
    );
}

#@override
sub perl {
    return Javonet::Sdk::Internal::RuntimeContext::get_instance(
        Javonet::Sdk::Core::RuntimeLib::get_runtime('Perl'),
        $connection_type,
        $tcp_address
    );
}

#@override
sub ruby {
    return Javonet::Sdk::Internal::RuntimeContext::get_instance(
        Javonet::Sdk::Core::RuntimeLib::get_runtime('Ruby'),
        $connection_type,
        $tcp_address
    );
}

#@override
sub nodejs {
    return Javonet::Sdk::Internal::RuntimeContext::get_instance(
        Javonet::Sdk::Core::RuntimeLib::get_runtime('Nodejs'),
        $connection_type,
        $tcp_address
    );
}

#@override
sub python {
    return Javonet::Sdk::Internal::RuntimeContext::get_instance(
        Javonet::Sdk::Core::RuntimeLib::get_runtime('Python'),
        $connection_type,
        $tcp_address
    );
}


no Moose;
1;