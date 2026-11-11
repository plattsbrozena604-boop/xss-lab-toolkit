<?php

$page[ 'body' ] .= "
<div class=\"body_padded\">
	<h1>漏洞：文件包含</h1>
	<div class=\"vulnerable_code_area\">
		<h3>文件 3</h3>
		<hr />
		欢迎回来 <em>" . dvwaCurrentUser() . "</em><br />
		你的IP: <em>{$_SERVER[ 'REMOTE_ADDR' ]}</em><br />";
if( array_key_exists( 'HTTP_X_FORWARDED_FOR', $_SERVER )) {
	$page[ 'body' ] .= "Forwarded for: <em>" . $_SERVER[ 'HTTP_X_FORWARDED_FOR' ];
	$page[ 'body' ] .= "</em><br />";
}
		$page[ 'body' ] .= "你的用户代理地址: <em>{$_SERVER[ 'HTTP_USER_AGENT' ]}</em><br />";
if( array_key_exists( 'HTTP_REFERER', $_SERVER )) {
		$page[ 'body' ] .= "你来自: <em>{$_SERVER[ 'HTTP_REFERER' ]}</em><br />";
}
		$page[ 'body' ] .= "我的主机: <em>{$_SERVER[ 'HTTP_HOST' ]}</em><br /><br />
		[<em><a href=\"?page=include.php\">back</a></em>]
	</div>

	<h2>更多信息</h2>
	<ul>
		<li>" . dvwaExternalLinkUrlGet( 'https://en.wikipedia.org/wiki/Remote_File_Inclusion' ) . "</li>
		<li>" . dvwaExternalLinkUrlGet( 'https://www.owasp.org/index.php/Top_10_2007-A3' ) . "</li>
	</ul>
</div>\n";

?>
