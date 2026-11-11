<?php
$headerCSP = "Content-Security-Policy: script-src 'self';";

header($headerCSP);

?>
<?php
if (isset ($_POST['include'])) {
$page[ 'body' ] .= "
	" . $_POST['include'] . "
";
}
$page[ 'body' ] .= '
<form name="csp" method="POST">
	<p>页面调用 ' . DVWA_WEB_PAGE_TO_ROOT . '/vulnerabilities/csp/source/jsonp.php 加载一些代码。修改该页以运行您自己的代码。</p>
	<p>1+2+3+4+5=<span id="answer"></span></p>
	<input type="button" id="solve" value="求和" />
</form>

<script src="source/high.js"></script>
';

