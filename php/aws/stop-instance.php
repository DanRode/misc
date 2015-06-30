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
$cmd = "stop";
require __DIR__ . "/aws-autoloader.php";

use Aws\Ec2\Ec2Client;
 
$ec2Client = Ec2Client::factory(array(
    'key'    => 'AKIAJVRBUZEU75ITKYVA',
    'secret' => '8bpZxvfqqIA81r2xj/Pc6C2V4qvQzFZAi6XW4S9G',
    'region' => 'us-east-1' // (e.g., us-east-1)
));

if($cmd == 'start'){
 $result = $ec2Client->startInstances(array(
 'InstanceIds' => array($instanceID,),
 'DryRun' => false,
 ));
} elseif($cmd == 'stop'){
 $result = $ec2Client->stopInstances(array(
 'InstanceIds' => array($instanceID,),
 'DryRun' => false,
 ));
}
echo "<pre>";
print_r($result); // uncomment to see results of request
echo "OK\n";
echo "</pre>";
?>
