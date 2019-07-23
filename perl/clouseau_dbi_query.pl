#!/usr/bin/perl
#
#
use English;
use Getopt::Std;
use DBI;


@audit_only = split(/\s+/, "8222 8219 10909 10908 20022 10907 11048 10547 10548 10550 10790 10789 10788 11076 21945 10849 2220Z 10927 11655 22241");
#print join("--\n", @audit_only) . "\n";
@db_only = split(/\s+/, "3293 3287 10737 7132 4357 11777 10082 7152 10009 7164 22205 7209 22073 18065 7217 7186 7185 7184 22245 7181 10141 11049 7215 7188 7130 7129 22287 22089 7165 7150 7144"); 


$| = 1;	# Continously flush the buffer.
$db = "webops";
$dbhost = "dc3-ops1.ops.ag.com";
$dbuser = "webops";
$dbpasswd = "ax437b";

$dbh = DBI->connect("DBI:mysql:$db:$dbhost", $dbuser, $dbpasswd) or die "Can't connect to DB $!\n";
$sql = q(SELECT server.asset  FROM server LEFT JOIN location ON (server.asset = location.asset) WHERE server.asset REGEXP '^-?[0-9]+$' AND model_id not like "UNK" AND (location.datacenter = 'dc3' )  order by datacenter, rack);
$sql2 = q(SELECT server.asset, server.cf_role, server.serial_number, server.model_id, location.datacenter, location.rack, location.bottom  FROM server LEFT JOIN location ON (server.asset = location.asset) WHERE server.asset REGEXP '^-?[0-9]+$' AND model_id not like "UNK" AND (location.datacenter = 'dc3' )  order by datacenter, rack);

$sth = $dbh->prepare("$sql2");
$sth->execute() or die "SQL Error: $DBI::errstr\n";
while (@row = $sth->fetchrow_array) {
    $dc3_assets{$row[0]} = "@row"
}
#%dc3_assets = map {$_ => 1} @dc3_assets;

print "Asset count: " . scalar @dc3_assets . "\n";

print "Audit Only\n";
$acount = 0;
$dcount = 0;
for $asset (@audit_only) {
    if (exists($dc3_assets{$asset})) {
        $acount++;
        print $dc3_assets{$asset} .  "\n";
    }
}
print "Audit only count $acount\n";
print "DB Only\n";

for $asset (@db_only) {
    if (exists($dc3_assets{$asset})) {
        $dcount++;
        print $dc3_assets{$asset} .  "\n";
    }
}
print "DB only count $dcount\n";

