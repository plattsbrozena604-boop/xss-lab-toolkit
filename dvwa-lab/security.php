<?php

define( 'DVWA_WEB_PAGE_TO_ROOT', '' );
require_once DVWA_WEB_PAGE_TO_ROOT . 'dvwa/includes/dvwaPage.inc.php';

dvwaPageStartup( array( 'authenticated', 'phpids' ) );

$page = dvwaPageNewGrab();
$page[ 'title' ]   = 'DVWA安全' . $page[ 'title_separator' ].$page[ 'title' ];
$page[ 'page_id' ] = 'security';

$securityHtml = '';
if( isset( $_POST['seclev_submit'] ) ) {
	// Anti-CSRF
	checkToken( $_REQUEST[ 'user_token' ], $_SESSION[ 'session_token' ], 'security.php' );

	$securityLevel = '';
	switch( $_POST[ 'security' ] ) {
		case 'low':
			$securityLevel = 'low';
			break;
		case 'medium':
			$securityLevel = 'medium';
			break;
		case 'high':
			$securityLevel = 'high';
			break;
		default:
			$securityLevel = 'impossible';
			break;
	}

	dvwaSecurityLevelSet( $securityLevel );
	dvwaMessagePush( "安全级别设置为 {$securityLevel}" );
	dvwaPageReload();
}

if( isset( $_GET['phpids'] ) ) {
	switch( $_GET[ 'phpids' ] ) {
		case 'on':
			dvwaPhpIdsEnabledSet( true );
			dvwaMessagePush( "PHPIDS 现已启用" );
			break;
		case 'off':
			dvwaPhpIdsEnabledSet( false );
			dvwaMessagePush( "PHPIDS 现已禁用" );
			break;
	}

	dvwaPageReload();
}

$securityOptionsHtml = '';
$securityLevelHtml   = '';
foreach( array( 'low', 'medium', 'high', 'impossible' ) as $securityLevel ) {
	$selected = '';
	if( $securityLevel == dvwaSecurityLevelGet() ) {
		$selected = ' selected="selected"';
		$securityLevelHtml = "<p>安全级别当前为: <em>$securityLevel</em>.<p>";
	}
	$securityOptionsHtml .= "<option value=\"{$securityLevel}\"{$selected}>" . ucfirst($securityLevel) . "</option>";
}

$phpIdsHtml = 'PHPIDS 目前: ';

// Able to write to the PHPIDS log file?
$WarningHtml = '';

if( dvwaPhpIdsIsEnabled() ) {
	$phpIdsHtml .= '<em>启用</em>. [<a href="?phpids=off">Disable PHPIDS</a>]';

	# Only check if PHPIDS is enabled
	if( !is_writable( $PHPIDSPath ) ) {
		$WarningHtml .= "<div class=\"warning\"><em>无法写入 PHPIDS 日志文件</em>: ${PHPIDSPath}</div>";
	}
}
else {
	$phpIdsHtml .= '<em>禁用</em>. [<a href="?phpids=on">启用 PHPIDS</a>]';
}

// Anti-CSRF
generateSessionToken();

$page[ 'body' ] .= "
<div class=\"body_padded\">
	<h1> DVWA安全  <img src=\"" . DVWA_WEB_PAGE_TO_ROOT . "dvwa/images/lock.png\" /></h1>
	<br />

	<h2>安全等级</h2>

	{$securityHtml}

	<form action=\"#\" method=\"POST\">
		{$securityLevelHtml}
		<p>您可以将安全级别设置为低、中、高或不可能。安全级别改变了dvwa的漏洞级别:</p>
		<ol>
			<li> 低-此安全级别是完全脆弱的，并且没有任何安全措施。它的用途是作为Web应用程序漏洞如何通过糟糕的编码实践表现出来的一个例子，并作为一个平台来教授或学习基本的开发技术。</li>
			<li> 中-此设置主要是为“Bad Security Practices”的用户提供一个示例，其中开发人员已尝试但未能保护应用程序。它还对用户完善其利用技术构成挑战。</li>
			<li> 高-此选项是对中等难度的扩展，混合了<em>较难的或可选的错误做法</em>以尝试保护代码。漏洞可能不允许相同程度的利用，类似于各种捕获旗帜（CTF）比赛。</li>
			<li>不可能-此级别应针对所有漏洞进行安全保护。它用于比较易受攻击的源代码和安全的源代码。<br />
				在DVWA v1.9之前，这个级别被称为“高”.</li>
		</ol>
		<select name=\"security\">
			{$securityOptionsHtml}
		</select>
		<input type=\"submit\" value=\"提交\" name=\"seclev_submit\">
		" . tokenField() . "
	</form>

	<br />
	<hr />
	<br />

	<h2>PHPIDS</h2>
	{$WarningHtml}
	<p>" . dvwaExternalLinkUrlGet( 'https://github.com/PHPIDS/PHPIDS', 'PHPIDS' ) . " v" . dvwaPhpIdsVersionGet() . " (PHP入侵检测系统) 是基于PHP的Web应用程序的安全层.</p>
	<p>PHPIDS 通过根据潜在恶意代码的黑名单过滤任何用户提供的输入。它在dvwa中用作Web应用程序防火墙（wafs）如何帮助提高安全性以及在某些情况下如何规避wafs的实时示例.</p>
	<p>您可以在会话期间在此站点上启用phpids.</p>

	<p>{$phpIdsHtml}</p>
	[<a href=\"?test=%22><script>eval(window.name)</script>\">Simulate attack</a>] -
	[<a href=\"ids_log.php\">查看IDS日志</a>]
</div>";

dvwaHtmlEcho( $page );

?>
