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
	<p>与 high level不同，它执行JSONP调用，但不使用回调，而是硬编码要调用的函数。</p><p>CSP设置只允许在本地服务器上使用外部javascript，不允许使用内联代码。</p>
	<p>1+2+3+4+5=<span id="answer"></span></p>
	<input type="button" id="solve" value="求和" />
</form>

<script src="source/impossible.js"></script>
';

