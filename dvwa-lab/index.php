<?php

define( 'DVWA_WEB_PAGE_TO_ROOT', '' );
require_once DVWA_WEB_PAGE_TO_ROOT . 'dvwa/includes/dvwaPage.inc.php';

dvwaPageStartup( array( 'authenticated', 'phpids' ) );

$page = dvwaPageNewGrab();
$page[ 'title' ]   = '欢迎光临' . $page[ 'title_separator' ].$page[ 'title' ];
$page[ 'page_id' ] = '根目录';

$page[ 'body' ] .= "
<div class=\"body_padded\">
	<h1>欢迎来到DVWA!</h1>
	<p>DVWA 是一个脆弱易受攻击的PHP / MySQL的Web应用程序。 它的主要目标是帮助专业安全人员在合法环境中测试他们的技能和工具，帮助Web开发人员更好地理解Web应用程序的安全性保护过程，并帮助学生和教师在受控的教室环境中学习Web应用程序的安全性。</p>
	<p>DVWA的目的是 <em>以不同等级的困难度和简单的接口来实现一些最常见的WEB漏洞。</em></p>
	<hr />
	<br />

	<h2>一般性说明</h2>
	<p>如何使用DVWA完全取决于用户。通过每个模块的固定级别，或者选择任何模块，并在达到下一个模块之前都能达到最高的水平。完成每个模块没有固定的方式；然而，用户应该觉得他们已经尽可能利用这些漏洞成功地探索了整个系统。 </p>
	<p>请注意，该软件既有记录在案的也有未记录的漏洞。这是有意为之，旨在鼓励你尽可能多地实践并发现问题。 </p>
	<p>DVWA还包括Web应用防火墙（WAF），PHPIDS，这可以使任何阶段的难度进一步加大。这些功能将演示如何添加另一层安全性以阻止某些恶意操作。请注意，还有一些公开的方法绕过了这些保护（因此可以看作是对更高级用户的扩展）！ </p>
	<p>每一页的底部都有一个帮助按钮，它允许您查看该漏洞的建议和提示。还有进一步的背景阅读的附加链接，涉及到一些安全争论。 </p>
	<hr />
	<br />

	<h2>警告!</h2>
	<p>DVWA是真他娘的脆弱！ <em>不要把它上传到你的托管服务提供商的公共HTML文件夹或任何面向Internet的服务器</em>，因为它们将受到损害。我们推荐使用设置NAT网络模式的虚拟机 (比如 " . dvwaExternalLinkUrlGet( 'https://www.virtualbox.org/','VirtualBox' ) . " 或者 " . dvwaExternalLinkUrlGet( 'https://www.vmware.com/','VMware' ) . ")。 在一个虚拟机里，您可以下载并安装 " . dvwaExternalLinkUrlGet( 'https://www.apachefriends.org/en/xampp.html','XAMPP' ) . "的Web服务器和数据库。</p>
	<br />
	<h3>免责声明 </h3>
	<p>我们不承担任何一个使用该应用（DVWA）的使用者的责任。我们已经明确了该应用的目的，不应恶意使用。我们已经给予了警告并采取措施以防止用户将应用安装在正在使用的WEB服务器上。如果您的Web服务器因为安装了DVWA而被攻破，这不是我们的责任，而是上传并安装他的人的责任。</p>
	<hr />
	<br />

	<h2>更多实训资源 </h2>
	<p>DVWA旨在涵盖在当今的Web应用程序中最常见的漏洞。然而，Web应用程序还有很多其他问题。如果您希望探索任何额外的攻击方式，或者想要更困难的挑战，您不妨查看下面的其他项目： </p>
	<ul>
		<li>" . dvwaExternalLinkUrlGet( 'http://www.itsecgames.com/', 'bWAPP') . "</li>
		<li>" . dvwaExternalLinkUrlGet( 'http://sourceforge.net/projects/mutillidae/files/mutillidae-project/', 'NOWASP') . " (以前称为" . dvwaExternalLinkUrlGet( 'http://www.irongeek.com/i.php?page=mutillidae/mutillidae-deliberately-vulnerable-php-owasp-top-10', 'Mutillidae' ) . ")</li>
		<li>" . dvwaExternalLinkUrlGet( 'https://www.owasp.org/index.php/OWASP_Broken_Web_Applications_Project', 'OWASP Broken Web Applications Project
') . "</li>
	</ul>
	<hr />
	<br />
	<h4>Brute Force（暴力（破解））|Command Injection（命令行注入）|CSRF（跨站请求伪造）<h4>
	<h4>File Inclusion（文件包含）|File Upload（文件上传）|Insecure CAPTCHA（不安全的验证码）<h4>
	<h4>SQL Injection（SQL注入）|SQL Injection（Blind）（SQL盲注）|WeakWeak Session IDs(弱口令)<h4>
	<h4>XSS（Reflected）（反射型跨站脚本）|XSS(DOM)（DOM型跨站脚本）|
	XSS（Stored）（存储型跨站脚本）<h4>
	
</div>";

dvwaHtmlEcho( $page );

?>
