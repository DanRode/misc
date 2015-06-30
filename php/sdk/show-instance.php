#!/usr/bin/env php
<?php
//phpinfo();
set_include_path("/home/drode/public_html/xxx/");
ini_set('display_errors',1);
ini_set('display_startup_errors',1);
error_reporting(-1);
/*
$cmd = $argv[1] or die("please supply a command(start/stop)...\n");
$instanceID = $argv[2] or die("please supply an instance ID\n");
*/

$instanceID = 'i-9c95f335';
$cmd = "start";
require __DIR__ . "/aws-autoloader.php";
/*
*/
use Aws\Ec2\Ec2Client;
$ec2Client = Ec2Client::factory(array(
    'key'    => 'AKIAJVRBUZEU75ITKYVA',
    'secret' => '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',
    'region' => 'us-east-1',
));
$result = $ec2Client->describeInstances();
echo "<b>DESCRIBE INSTANCES 1</b><br>";
echo "<hr>";
echo "<pre>";
print_r($result);
echo "</pre>";
//echo current($result->getPath('Reservations/*/Instances/*/PublicDnsName')) . "<br>\n";
echo "<hr>";
echo "OK\n";
?>
