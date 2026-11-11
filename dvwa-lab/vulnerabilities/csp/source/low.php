<?php

$headerCSP = "Content-Security-Policy: script-src 'self' https://pastebin.com  example.com code.jquery.com https://ssl.google-analytics.com ;"; // allows js from self, pastebin.com, jquery and google analytics.

header($headerCSP);

# https://pastebin.com/raw/R570EE00

?>
<?php
if (isset ($_POST['include'])) {
$page[ 'body' ] .= "
	<script src='" . $_POST['include'] . "'></script>
";
}
$page[ 'body' ] .= '
<form name="csp" method="POST">
	<p>您可以包括来自外部源的脚本、检查内容安全策略并在此处输入要包含的URL:</p>
	<input size="50" type="text" name="include" value="" id="include" />
	<input type="submit" value="确定" />
</form>
';
