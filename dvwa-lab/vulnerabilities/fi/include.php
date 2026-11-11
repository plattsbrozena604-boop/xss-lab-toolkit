<?php

// Check if the right PHP functions are enabled
$WarningHtml = '';
if( !ini_get( 'allow_url_include' ) ) {
	$WarningHtml .= "<div class=\"warning\">PHP 函数 <em>allow_url_include</em> 未启用。</div>";
}
if( !ini_get( 'allow_url_fopen' ) ) {
	$WarningHtml .= "<div class=\"warning\">PHP 函数 <em>allow_url_fopen</em> 未启用。</div>";
}


$page[ 'body' ] .= "
<div class=\"body_padded\">
	<h1>漏洞：文件包含</h1>

	{$WarningHtml}

	<div class=\"vulnerable_code_area\">
		[<em><a href=\"?page=file1.php\">文件1</a></em>] - [<em><a href=\"?page=file2.php\">文件2</a></em>] - [<em><a href=\"?page=file3.php\">文件3</a></em>]
	</div>

	<h2>更多信息</h2>
	<ul>
		<li>" . dvwaExternalLinkUrlGet( 'https://en.wikipedia.org/wiki/Remote_File_Inclusion' ) . "</li>
		<li>" . dvwaExternalLinkUrlGet( 'https://www.owasp.org/index.php/Top_10_2007-A3' ) . "</li>
	</ul>
</div>\n";

?>
