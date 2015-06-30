<html>
<head>
<link rel="stylesheet" type="text/css" href="http://fonts.googleapis.com/css?family=Megrim">

<title>danrode.com test page</title>
<style>
p.serif {
    font-family: "Times New Roman", Times, serif;
}

p.sansserif {
    font-family: Verdana, Helvetica, sans-serif;
    font-size: 1.0em;
}
p.copy {
    font-family: Verdana, Helvetica, sans-serif;
    font-size: 0.7em;
}
h1 {
    /*font-family: Verdana, Helvetica, sans-serif;*/
    font-family: 'Megrim', cursive;
    font-size: 3.5em;
    text-shadow: 0 0 6px rgba(0, 0, 0, 0.6);
    color: maroon;
}
</style>
</head>
<body>
<h1>DanRode.com</h1>
<div>
  <p class="sansserif">
  <?php 
  echo $_SERVER['SERVER_ADDR'] . "<br>" . gethostbyname('rode.org'); 
  ?>
  </p>
</div>
<div>
  <p class="sansserif">
  <a href="http://blog.danrode.com">Dan Rode's Blog</a>
  <br>
  <a href="https://www.flickr.com/photos/10781509@N07">My Flickr page (photos)</a>
  </p>
</div>
<div>
  <p class="sansserif">
  System Load Average: 
  <?php print_r(sys_getloadavg()[0]); ?>
  <br>
  </p>
</div>
<div>
<hr width=20% align='left'>
<p class="copy">
&copy; Dan Rode - <?php echo date("Y")?>
</p>
</div>
</body>
</html>
