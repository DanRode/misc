<?php
ini_set('display_errors',1);
ini_set('display_startup_errors',1);
error_reporting(-1);

$root = realpath($_SERVER["DOCUMENT_ROOT"]);
require_once "$root/sdk/required.php";

//$result = $ec2Client->DescribeInstances(array(
//  'Filters' => array(
//    array('Name' => 'instance-type', 'Values' => array('m1.small')),
//  ) ));
$result = $ec2Client->DescribeInstances();
//print_r($result);
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

    echo "<ul>";
    echo '<li><b>Name:</b> ' . $instanceName . '</li>';
    echo '<li><b>ID:</b> ' . $instance['InstanceId'] . '</li>';
    echo '<li><b>State:</b> ' . $instance['State']['Name'] . '</li>';
    //echo '<li><b>Image ID:</b> ' . $instance['ImageId'] . '</li>';
    //echo '<li><b>Private Dns Name:</b> ' . $instance['PrivateDnsName'] . '</li>';
    //echo '<li><b>Instance Type:</b> ' . $instance['InstanceType'] . '</li>';
    //echo '<li><b>Security Group:</b> ' . $instance['SecurityGroups'][0]['GroupName'] . '</li>';
    echo "</ul>";
  }

}
?>
