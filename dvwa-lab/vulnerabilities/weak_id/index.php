<?php

define( 'DVWA_WEB_PAGE_TO_ROOT', '../../' );
require_once DVWA_WEB_PAGE_TO_ROOT . 'dvwa/includes/dvwaPage.inc.php';

dvwaPageStartup( array( 'authenticated', 'phpids' ) );

$page = dvwaPageNewGrab();
$page[ 'title' ]   = '漏洞： 弱口令' . $page[ 'title_separator' ].$page[ 'title' ];
$page[ 'page_id' ] = 'weak_id';
$page[ 'help_button' ]   = 'weak_id';
$page[ 'source_button' ] = 'weak_id';
dvwaDatabaseConnect();

$method            = 'GET';
$vulnerabilityFile = '';
switch( $_COOKIE[ 'security' ] ) {
	case 'low':
		$vulnerabilityFile = 'low.php';
		break;
	case 'medium':
		$vulnerabilityFile = 'medium.php';
		break;
	case 'high':
		$vulnerabilityFile = 'high.php';
		break;
	default:
		$vulnerabilityFile = 'impossible.php';
		$method = 'POST';
		break;
}

require_once DVWA_WEB_PAGE_TO_ROOT . "vulnerabilities/weak_id/source/{$vulnerabilityFile}";


$page[ 'body' ] .= <<<EOF
<div class="body_padded">
	<h1>漏洞： 弱口令</h1>
	<p>
		每次单击按钮时，此页面都将设置一个名为dvwaSession的新cookie。<br />
	</p>
	<form method="post">
		<input type="submit" value="生成" />
	</form>
$html

EOF;

/*
Maybe display this, don't think it is needed though
if (isset ($cookie_value)) {
	$page[ 'body' ] .= <<<EOF
	The new cookie value is $cookie_value
EOF;
}
*/

dvwaHtmlEcho( $page );

?>
