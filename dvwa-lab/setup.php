<?php

define( 'DVWA_WEB_PAGE_TO_ROOT', '' );
require_once DVWA_WEB_PAGE_TO_ROOT . 'dvwa/includes/dvwaPage.inc.php';

dvwaPageStartup( array( 'phpids' ) );

$page = dvwaPageNewGrab();
$page[ 'title' ]   = '安装程序' . $page[ 'title_separator' ].$page[ 'title' ];
$page[ 'page_id' ] = 'setup';

if( isset( $_POST[ 'create_db' ] ) ) {
	// Anti-CSRF
	checkToken( $_REQUEST[ 'user_token' ], $_SESSION[ 'session_token' ], 'setup.php' );

	if( $DBMS == 'MySQL' ) {
		include_once DVWA_WEB_PAGE_TO_ROOT . 'dvwa/includes/DBMS/MySQL.php';
	}
	elseif($DBMS == 'PGSQL') {
		// include_once DVWA_WEB_PAGE_TO_ROOT . 'dvwa/includes/DBMS/PGSQL.php';
		dvwaMessagePush( 'PostgreSQL is not yet fully supported.' );
		dvwaPageReload();
	}
	else {
		dvwaMessagePush( 'ERROR: Invalid database selected. Please review the config file syntax.' );
		dvwaPageReload();
	}
}

// Anti-CSRF
generateSessionToken();

$page[ 'body' ] .= "
<div class=\"body_padded\">
	<h1>数据库设置 <img src=\"" . DVWA_WEB_PAGE_TO_ROOT . "dvwa/images/spanner.png\" /></h1>

	<p> 单击下面的“创建/重置数据库”按钮创建或重置数据库。 <br />
	 如果出现错误，请确保在以下位置具有正确的用户凭据：  <em>" . realpath(  getcwd() . DIRECTORY_SEPARATOR . "config" . DIRECTORY_SEPARATOR . "config.inc.php" ) . "</em></p>

	<p>如果数据库已经存在，<em>它将被清除，数据将被重置。</em><br />
	您还可以在任何时候使用它重置管理员 (\"<em>admin</em> // <em>password</em>\") </p>
	<hr />
	<br />

	<h2>设置检查</h2>

	{$DVWAOS}<br />
	后台数据库: <em>{$DBMS}</em><br />
	PHP 版本: <em>" . phpversion() . "</em><br />
	<br />
	{$SERVER_NAME}<br />
	<br />
	{$phpDisplayErrors}<br />
	{$phpSafeMode}<br/ >
	{$phpURLInclude}<br/ >
	{$phpURLFopen}<br />
	{$phpMagicQuotes}<br />
	{$phpGD}<br />
	{$phpMySQL}<br />
	{$phpPDO}<br />
	<br />
	{$MYSQL_USER}<br />
	{$MYSQL_PASS}<br />
	{$MYSQL_DB}<br />
	{$MYSQL_SERVER}<br />
	<br />
	{$DVWARecaptcha}<br />
	<br />
	{$DVWAUploadsWrite}<br />
	{$DVWAPHPWrite}<br />
	<br />
	<br />
	{$bakWritable}
	<br />
	<i><span class=\"failure\">红色状态</span> ，表示在尝试完成某些模块时会出现问题。 </i><br />
	<br />
	 如果在<i>allow-url-fopen</i>或<i>allow-url-include</i>上看到禁用，请在php.ini文件中设置以下内容，然后重新启动apache。 <br />
	<pre><code>allow_url_fopen = On
allow_url_include = On</code></pre>
	 这些只是文件包含实验室所必需的，所以除非您想使用它们，否则可以忽略它们。 

	<br /><br /><br />

	<!-- Create db button -->
	<form action=\"#\" method=\"post\">
		<input name=\"create_db\" type=\"submit\" value=\"创建 / 重置数据库\">
		" . tokenField() . "
	</form>
	<br />
	<hr />
</div>";

dvwaHtmlEcho( $page );

?>
