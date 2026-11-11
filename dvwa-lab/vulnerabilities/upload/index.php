<?php

define( 'DVWA_WEB_PAGE_TO_ROOT', '../../' );
require_once DVWA_WEB_PAGE_TO_ROOT . 'dvwa/includes/dvwaPage.inc.php';

dvwaPageStartup( array( 'authenticated', 'phpids' ) );

$page = dvwaPageNewGrab();
$page[ 'title' ]   = '漏洞： 文件上传' . $page[ 'title_separator' ].$page[ 'title' ];
$page[ 'page_id' ] = 'upload';
$page[ 'help_button' ]   = 'upload';
$page[ 'source_button' ] = 'upload';

dvwaDatabaseConnect();

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
		break;
}

require_once DVWA_WEB_PAGE_TO_ROOT . "vulnerabilities/upload/source/{$vulnerabilityFile}";

// Check if folder is writeable
$WarningHtml = '';
if( !is_writable( $PHPUploadPath ) ) {
	$WarningHtml .= "<div class=\"warning\">文件夹权限: {$PHPUploadPath}<br /><em>文件夹不可写。</em></div>";
}
// Is PHP-GD installed?
if( ( !extension_loaded( 'gd' ) || !function_exists( 'gd_info' ) ) ) {
	$WarningHtml .= "<div class=\"warning\">未安装PHP GD 模块</div>";
}

$page[ 'body' ] .= "
<div class=\"body_padded\">
	<h1>漏洞： 文件上传</h1>

	{$WarningHtml}

	<div class=\"vulnerable_code_area\">
		<form enctype=\"multipart/form-data\" action=\"#\" method=\"POST\">
			<input type=\"hidden\" name=\"MAX_FILE_SIZE\" value=\"100000\" />
			选择要上传的图片:<br /><br />
			<input name=\"uploaded\" type=\"file\" /><br />
			<br />
			<input type=\"submit\" name=\"Upload\" value=\"上传\" />\n";

if( $vulnerabilityFile == 'impossible.php' )
	$page[ 'body' ] .= "			" . tokenField();

$page[ 'body' ] .= "
		</form>
		{$html}
	</div>

	<h2>更多信息</h2>
	<ul>
		<li>" . dvwaExternalLinkUrlGet( 'https://www.owasp.org/index.php/Unrestricted_File_Upload' ) . "</li>
		<li>" . dvwaExternalLinkUrlGet( 'https://blogs.securiteam.com/index.php/archives/1268' ) . "</li>
		<li>" . dvwaExternalLinkUrlGet( 'https://www.acunetix.com/websitesecurity/upload-forms-threat/' ) . "</li>
	</ul>
</div>";

dvwaHtmlEcho( $page );

?>
