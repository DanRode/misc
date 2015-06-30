<?php
$form_ref = 'http://danrode.com/instance.php';
$r = parse_url(getenv("HTTP_REFERER"));
$referer = "{$r['scheme']}://{$r['host']}{$r['path']}";
if($referer != $form_ref){
  echo getenv("HTTP_REFERER");
  die('Invalid input');
}

function error_message ($message) {
  header("Location: http://danrode.com/instance.php?error_message={$message}");
  exit();
}
//error_message("THIS IS A TEST!");
$page_header = "
<html>
  <head>
    <title>danrode.com test page</title>
    <style>
      body {
        font-family: Verdana, Helvetica, sans-serif;
        font-size: 1.0em;
      }
      h1 {
        font-family: Verdana, Helvetica, sans-serif;
        font-size: 2.5em;
      }
    </style>
  </head>
  <body>
    <h1>drode-aws</h1>
    <div>
      <p>";
ini_set('display_errors',1);
ini_set('display_startup_errors',1);
error_reporting(-1);
//$instanceID = 'i-9c95f335';
$root = realpath($_SERVER["DOCUMENT_ROOT"]);
require_once "$root/sdk/required.php";

//Check whether the form has been submitted
if (array_key_exists('check_submit', $_POST)) {
  if (isset($_POST['action'])) {
    $action = $_POST['action'];
    switch($action) {
    case "start":
      if (isset($_POST['instance'])) {
        $result = $ec2Client->startInstances(array(
          'InstanceIds' => array($_POST['instance'],),
          'DryRun' => false,
        ));
      } else {
        echo "BAD";
      }
      break;
    case "stop":
      if (isset($_POST['instance'])) {
        $result = $ec2Client->stopInstances(array(
          'InstanceIds' => array($_POST['instance'],),
          'DryRun' => false,
        ));
      } else {
        echo "BAD";
      }
      break;
    case "show":
      $result = $ec2Client->DescribeInstances(array(
        'Filters' => array(
          array('Name' => 'instance-type', 'Values' => array('m1.small')),
        )
      ));
      break;
    default:
      $formpage = getenv("HTTP_REFERER");
      echo "No action selected<br>";
      echo "<a href='{$formpage}'>Return to form</a>";
      exit(255);
    }

  } else {
    echo "Missing instance ID";
  }
} else {
  echo "\n<BR><B>ERROR: Form not submitted</B><BR>\n";
  exit(255);
}
echo "<pre>";
$result = nl2br($result);
print_r($result);
echo "</pre>";
?>
</body>
</html>
