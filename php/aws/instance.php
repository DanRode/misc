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
    select {
        font-family: Verdana, Helvetica, sans-serif; 
        font-size: 0.8em;
    }
    input[type="text"] {
        font-family: Verdana, Helvetica, sans-serif; 
        font-size: 0.75em;
    }
    input[type="password"] {
        font-family: Verdana, Helvetica, sans-serif; 
        font-size: 0.75em;
    }
</style>
</head>
<body>
<h1>drode-aws</h1>
<div>
<?php
  if (isset($_GET['error_message'])) {
    echo "<p>{$_GET['error_message']}</p>";
  } else {
    echo "<p>&nbsp;</p>";
  }
?>
</div>
<div>
    <p>
        <form action="start.php" method="post">
        <input type="hidden" name="check_submit" value="1" />
    <table cellspacing="8">
    <tr>
        <td>Action:</td>
        <td>
            <select name="action">
                <option selected='selected'>Select One</option>
                <option value='start'>start</option>
                <option value='stop'>stop</option>
                <option value='reboot'>reboot</option>
                <option value='show'>show</option>
            </select>
        </td>
    </tr>
    <tr>
        <td>Instance:</td>
        <td>
            <select name="instance">
                <option value='i-9c95f335'>drode-aws</option>
                <option value='i-xxxxxxxx'>drode2-aws</option>
            </select>
        </td>
    </tr>
    <tr>
        <td>User Id:</td>
        <td>
            <input type="text" name="name">
        </td>
    </tr>
    <tr>
        <td>Password:</td>
        <td>
            <input type="password" name="password">
        </td>
    </tr>
    <tr>
        <td>&nbsp;</td>
        <td><input type="submit"></td>
    </tr>

        </form>
  </p>
</div>
</body>
</html>
