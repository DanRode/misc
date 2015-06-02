#!/usr/bin/perl
#
#
use English;
use Getopt::Std;
use DBI;

$db = "webops";
$dbhost = "dc3-ops1.ops.ag.com";
$dbuser = "webops";
$dbpasswd = "ax437b";

$dbh = DBI->connect("DBI:mysql:$db:$dbhost", $dbuser, $dbpasswd) or die "Can't connect to DB $!\n";
$sql = q(SELECT server.asset, server.serial_number, server.model_id, location.datacenter, location.rack FROM server LEFT JOIN location ON (server.asset = location.asset) WHERE server.asset REGEXP '^-?[0-9]+$' AND model_id not like "UNK" AND (location.datacenter = 'dc3' OR location.datacenter = 'osc' or location.datacenter = 'cle' )  order by datacenter, rack);


#$sql = q(SELECT server.asset, server.serial_number, server.model_id, location.datacenter, location.rack, FROM server LEFT JOIN location ON (server.asset = location.asset) WHERE server.asset REGEXP '^-?[0-9]+$' AND model_id not like "UNK" AND (location.datacenter = 'dc3' )  order by datacenter, rack);
#$sql = q(SELECT asset, model_id  FROM server);

$sth = $dbh->prepare("$sql");
$sth->execute() or die "SQL Error: $DBI::errstr\n";
$assets = $sth->fetchall_arrayref;

print "Asset, serial number, description, datacenter, rack\n";
for $asset (@{$assets}) {
    $sql = "SELECT description FROM hardware  WHERE id = '@$asset[2]'";
    $sth = $dbh->prepare("$sql");
    $sth->execute() or die "SQL Error: $DBI::errstr\n";
    $desc = $sth->fetchrow_arrayref;

    $d = $$desc[0];
    $d  =~ s/\,/-/g;

    if ($$asset[1] eq "" ) {
        $sn = `fh -h $$asset[0] | grep ^serial | awk -F ": " '{print $2}'`;
        $sn  =~ s/^serial: //;
        if ($sn eq "" ) {
            $sn = "UNK";
            $xcount++;
        }
       
    }
    else {
        $sn = $$asset[1]
    }
    chomp $sn;
        

    print "$$asset[0], $sn, $d, $$asset[3], $$asset[4] \n";
}
$count = scalar @{$assets};
print "Count $count\n";
print "Missing serial count $xcount\n";
