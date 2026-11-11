<?php

$page[ 'body' ] .= "
<div class=\"body_padded\">
	<h1>漏洞：文件包含</h1>
	<div class=\"vulnerable_code_area\">
		<h3>文件 1</h3>
		<hr />
		你好 <em>" . dvwaCurrentUser() . "</em><br />
		你的IP: <em>{$_SERVER[ 'REMOTE_ADDR' ]}</em><br /><br />
		[<em><a href=\"?page=include.php\">back</a></em>]
	</div>

	<h2>更多信息</h2>
	<ul>
		<li>" . dvwaExternalLinkUrlGet( 'https://en.wikipedia.org/wiki/Remote_File_Inclusion' ) . "</li>
		<li>" . dvwaExternalLinkUrlGet( 'https://www.owasp.org/index.php/Top_10_2007-A3' ) . "</li>
	</ul>
</div>\n";

?>
