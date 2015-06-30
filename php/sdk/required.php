<?php
$root = realpath($_SERVER["DOCUMENT_ROOT"]);
require_once "$root/sdk/aws-autoloader.php";
use Aws\Ec2\Ec2Client;

$ec2Client = Ec2Client::factory(array(
    'key'    => 'AKIAJVRBUZEU75ITKYVA',
    'secret' => '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',
    'region' => 'us-east-1',
));
?>
