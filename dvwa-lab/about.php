<?php

define( 'DVWA_WEB_PAGE_TO_ROOT', '' );
require_once DVWA_WEB_PAGE_TO_ROOT . 'dvwa/includes/dvwaPage.inc.php';

dvwaPageStartup( array( 'phpids' ) );

$page = dvwaPageNewGrab();
$page[ 'title' ]   = 'About' . $page[ 'title_separator' ].$page[ 'title' ];
$page[ 'page_id' ] = 'about';

$page[ 'body' ] .= "
<div class=\"body_padded\">
	<h2>About</h2>
	<p>Version " . dvwaVersionGet() . " (Release date: " . dvwaReleaseDateGet() . ")</p>
	<p>漏洞测试的Web应用程序（dvwa）是一个漏洞测试的php/mysql Web应用程序。其主要目标是帮助安全专业人员在法律环境中测试他们的技能和工具，帮助Web开发人员更好地了解保护Web应用程序的过程，并帮助教师/学生在教室环境中教授/学习Web应用程序安全性。</p>
	<p> 可以找到DVWA的官方文件  <a href=\"docs/DVWA_v1.3.pdf\">here</a>.</p>
	<p> 所有材料版权所有2008-2015 Randomstorm&Ryan Dewhurst .</p>

	<h2>链接</h2>
	<ul>
		<li>主页: " . dvwaExternalLinkUrlGet( 'http://www.dvwa.co.uk/' ) . "</li>
		<li>项目首页: " . dvwaExternalLinkUrlGet( 'https://github.com/RandomStorm/DVWA' ) . "</li>
		<li>错误追踪系统: " . dvwaExternalLinkUrlGet( 'https://github.com/RandomStorm/DVWA/issues' ) . "</li>
		<li>源头控制: " . dvwaExternalLinkUrlGet( 'https://github.com/RandomStorm/DVWA/commits/master' ) . "</li>
		<li>维基: " . dvwaExternalLinkUrlGet( 'https://github.com/RandomStorm/DVWA/wiki' ) . "</li>
	</ul>

	<h2>工作人员</h2>
	<ul>
		<li>Brooks Garrett: " . dvwaExternalLinkUrlGet( 'http://brooksgarrett.com/','www.brooksgarrett.com' ) . "</li>
		<li>Craig</li>
		<li>g0tmi1k: " . dvwaExternalLinkUrlGet( 'https://blog.g0tmi1k.com/','g0tmi1k.com' ) . "</li>
		<li>Jamesr: " . dvwaExternalLinkUrlGet( 'https://www.creativenucleus.com/','www.creativenucleus.com' ) . " / " . dvwaExternalLinkUrlGet( 'http://www.designnewcastle.co.uk/','www.designnewcastle.co.uk' ) . "</li>
		<li>Jason Jones: " . dvwaExternalLinkUrlGet( 'http://www.linux-ninja.com/','www.linux-ninja.com' ) . "</li>
		<li>RandomStorm: " . dvwaExternalLinkUrlGet( 'https://www.randomstorm.com/','www.randomstorm.com' ) . "</li>
		<li>Ryan Dewhurst: " . dvwaExternalLinkUrlGet( 'https://www.dewhurstsecurity.com/','www.dewhurstsecurity.com' ) . "</li>
		<li>Shinkurt: " . dvwaExternalLinkUrlGet( 'http://www.paulosyibelo.com/','www.paulosyibelo.com' ) . "</li>
		<li>Tedi Heriyanto: " . dvwaExternalLinkUrlGet( 'http://tedi.heriyanto.net/','tedi.heriyanto.net' ) . "</li>
		<li>Tom Mackenzie: " . dvwaExternalLinkUrlGet( 'https://www.tmacuk.co.uk/','www.tmacuk.co.uk' ) . "</li>
		<li>汉化作者Thieves: " . dvwaExternalLinkUrlGet( 'https://weibo.com/u/5695213464/','https://weibo.com/u/5695213464' ) . "
		<p>没错，这玩意就是我一个字一个字汉化的</p>
	<ul>
		<br />
		<li>PHPIDS - Copyright (c) 2007 " . dvwaExternalLinkUrlGet( 'http://github.com/PHPIDS/PHPIDS', 'PHPIDS group' ) . "</li>
	</ul>

	<h2>许可证</h2>
	<p>漏洞测试的Web应用程序（dvwa）是免费软件：您可以重新发布和/或修改它。
	根据GNU通用公共许可证的条款
	自由软件基金会，或者许可证的第3版，或者
	（由您选择）任何更高版本.</p>
	<p>PHPIDS 库包含在这个DVWA发行版中。PHPIDS的运行不需要DVWA团队的支持。它是根据<a href=\"" . DVWA_WEB_PAGE_TO_ROOT . "instructions.php?doc=PHPIDS-license\">单独条款</a>  至DVWA代码 .</p>

	<h2>发展</h2>
	<p>欢迎所有人贡献和帮助使dvwa尽可能成功。所有投稿人都可以将其姓名和链接（如果愿意）放在“工作人员”部分。若要进行贡献，请从项目主页中选择要处理的问题或向问题列表提交修补程序。</p>
</div>\n";

dvwaHtmlEcho( $page );

exit;

?>
