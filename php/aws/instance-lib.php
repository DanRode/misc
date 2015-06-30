<?php
$root = realpath($_SERVER["DOCUMENT_ROOT"]);
require_once "$root/sdk/required.php";
ini_set('display_errors',1);
ini_set('display_startup_errors',1);
error_reporting(-1);

function show_instances($ec2Client) {

  $hosts_array = [];
  $result = $ec2Client->DescribeInstances();
  $reservations = $result['Reservations'];

  foreach ($reservations as $reservation) {
    $instances = $reservation['Instances'];
    foreach ($instances as $instance) {
      $instanceName = '';
      foreach ($instance['Tags'] as $tag) {
        if ($tag['Key'] == 'Name') {
          $instanceName = $tag['Value'];
        }
      }
      $hosts_array[] = [
        'name' => $instanceName,
        'id' => $instance['InstanceId'],
        'state' => $instance['State']['Name'],
        'ami_id' => $instance['ImageId'],
        'priv_dns' => $instance['PrivateDnsName'],
        'type' => $instance['InstanceType'],
        'groups' => $instance['SecurityGroups'][0]['GroupName'],
        ];

    }

  }
  return($hosts_array);
}
$array = show_instances($ec2Client);
echo "<pre>";
print_r($array);
echo "</pre>";
?>

