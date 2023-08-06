package Javonet::Core::Protocol::TypeSerializer;
use utf8;
use strict;
use warnings;
use Moose;
use Encode;
use lib 'lib';

use aliased 'Javonet::Sdk::Core::Type' => 'Type', qw(get_type);
use aliased 'Javonet::Sdk::Core::StringEncodingMode' => 'StringEncodingMode', qw(get_string_encoding_mode);

sub serializeInt {
    my ($self, $int_value) = @_;
    my $length = 4;
    my @initial_array = (Type->get_type('JavonetInteger'), $length);
    my @bytes =  unpack "C*", pack "V",  $int_value;
    return (@initial_array, @bytes);
}

sub serializeString {
    my $self = $_[0];
    my $string = $_[1];
    my @serialized_string = unpack("C*", Encode::encode("utf8", $string));
    my $length = @serialized_string;

    my @length =  unpack "C*", pack "V",  $length;
    my @initial_array =(Type->get_type('JavonetString'),
        StringEncodingMode->get_string_encoding_mode('UTF8'),
    @length, @serialized_string);

    return @initial_array;
}

sub serializeDouble {
    my ($self, $double_value) = @_;
    my $length = 8;
    my @initial_array = (Type->get_type('JavonetDouble'), $length);
    my @bytes =  unpack "C*", pack "d",  $double_value;
    return (@initial_array, @bytes);
}

sub serializeFloat {
    my ($self, $float_value) = @_;
    my $length = 4;
    my @initial_array = (Type->get_type('JavonetFloat'), $length);
    my @bytes = unpack "C*", pack "f",  $float_value;
    return (@initial_array, @bytes);
}

sub serializeBoolean {
    my ($self, $bool_value) = @_;
    my $length = 1;
    my @initial_array = (Type->get_type('JavonetBoolean'), $length);
    my @bytes;
    if ($bool_value) {
        @bytes =  ($bool_value);
    }
    else{
        @bytes =  ($bool_value);
    }

    return (@initial_array, @bytes);
}

sub serializeCommand {
    my $self = $_[0];
    my $command = $_[1];
    my $length = @{$command->{payload}};
    my @length =  unpack "C*", pack "V",  $length;
    my @initial_array =(Type->get_type('Command'), @length, $command->{runtime},$command->{command_type});

    return @initial_array;
}
1;