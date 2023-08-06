package Javonet::Core::Transmitter::PerlTransmitter;
use strict;
use warnings;
use Cwd;
use aliased 'Javonet::Core::Transmitter::PerlTransmitterWrapper' => 'PerlTransmitterWrapper' , qw(send_command_ activate_);
use Exporter;

our @ISA = qw(Exporter);
our @EXPORT = qw(send_command activate_with_licence_file activate_with_credentials activate_with_credentials_and_proxy);

sub send_command {
    my ($self, $message_ref) = @_;
    my @response = PerlTransmitterWrapper->send_command_($message_ref);
    return @response;
}

sub activate_with_licence_file {
    return __activate();
}

sub activate_with_credentials {
    my($self, $email, $licenceKey) = @_;
    return __activate($email, $licenceKey);
}

sub activate_with_credentials_and_proxy {
    my($self, $email, $licenceKey, $proxyHost, $proxyUserName, $proxyPassword) = @_;
    return __activate($email, $licenceKey, $proxyHost, $proxyUserName, $proxyPassword);
}

sub __activate {
    my($email, $licenceKey, $proxyHost, $proxyUserName, $proxyPassword) = @_;
    #set default values
    $email //="";
    $licenceKey //="";
    $proxyHost //="";
    $proxyUserName //="";
    $proxyPassword //="";
    return PerlTransmitterWrapper->activate_($email, $licenceKey, $proxyHost, $proxyUserName, $proxyPassword);
}

1;
