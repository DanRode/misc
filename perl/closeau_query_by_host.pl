#!/usr/bin/perl
#
#
use English;
use Getopt::Std;
use DBI;

$| = 1;	# Continously flush the buffer.

$db = "webops";
$dbhost = "dc3-ops1.ops.ag.com";
$dbuser = "webops";
$dbpasswd = "ax437b";


@myhosts = `cat myhosts`;
chomp @myhosts;

$dbh = DBI->connect("DBI:mysql:$db:$dbhost", $dbuser, $dbpasswd) || die "Can't connect to DB $!\n";
print "hostname, asset, cf_role, serial_number, model_id, ram_size, datacenter, rack, bottom, vendor, description \n";
for $i (@myhosts) {
    my $sth = $dbh->prepare("SELECT hostname, asset, cf_role, serial_number, model_id, ram_size from server where hostname='$i'");

    $sth->execute();
#    while (my $hash_ref = $sth->fetchrow_hashref) {
    #print $hash_ref->{name}, " is ", $hash_ref->{age}, 
    #" years old, and has a " , $hash_ref->{pet}, "\n";
    #}

    my @xrow;
    while(my @row = $sth->fetchrow_array) {
        @xrow = @row;

        my $sth1 =  $dbh->prepare("SELECT datacenter, rack, bottom from location where asset='@row[1]'");
        $sth1->execute();
        while(my @row1 = $sth1->fetchrow_array) {
            @xrow = (@xrow, @row1);
        }


        my $sth2 =  $dbh->prepare("SELECT vendor, description from hardware where id='@row[4]'");
        $sth2->execute();
        while(my @row2 = $sth2->fetchrow_array) {
            for $x (@row2) {
                $x =~ s/,//g;
                push(@xrow, "$x");
            }
                    # @xrow = (@xrow, @row2);
        }




        print join(', ', @xrow), "\n";

    }


}
$dbh->disconnect();
