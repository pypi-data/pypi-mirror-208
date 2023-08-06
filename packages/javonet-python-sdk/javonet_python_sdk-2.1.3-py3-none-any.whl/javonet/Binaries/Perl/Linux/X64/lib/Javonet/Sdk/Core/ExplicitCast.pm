package Javonet::Sdk::Core::ExplicitCast;
use strict;
use lib 'lib';

use warnings FATAL => 'all';
    sub cast {
        my $value = shift;
        my $target_type = shift;

        return Javonet::Sdk::Core::PerlCommand->new(
            runtime      => 100,
            command_type => Javonet::Sdk::Core::PerlCommandType::get_command_type('Cast'),
            payload      => [
                $value,
                Javonet::Sdk::Core::PerlCommand->new(
                    runtime      => 100,
                    command_type => Javonet::Sdk::Core::PerlCommandType::get_command_type('GetType'),
                    payload      => [
                        $target_type
                    ]

                )
            ]
        );
    }
1;