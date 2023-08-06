package Javonet::Core::Protocol::TypeDeserializer;
use strict;
use warnings;
use Moose;
use Encode;
use lib 'lib';

sub deserializeInt {
    my ($self, $acc_ref) = @_;
    my @int_array = @$acc_ref;
    my $decoded_int = unpack "V", pack "C4",  @int_array;
    return $decoded_int;
}

sub deserializeString {
    my ($self, $string_encoding_mode, $acc_ref) = @_;
    my @string_array = @$acc_ref;
    my $string_array_joined = join '', map chr, @string_array;
    my $decoded_string = Encode::decode("utf8", $string_array_joined);
    return $decoded_string;
}

sub deserializeDouble {
    my ($self, $acc_ref) = @_;
    my @double_array = @$acc_ref;
    my $decoded_double = unpack "d", pack "C8",  @double_array;
    return $decoded_double;
}

sub deserializeFloat {
    my ($self, $acc_ref) = @_;
    my @float_array = @$acc_ref;
    my $decoded_float = unpack "f", pack "C4",  @float_array;
    return $decoded_float;
}

sub deserializeBoolean {
    my ($self, $boolean_value) = @_;
    return $boolean_value;
}

no Moose;
1;