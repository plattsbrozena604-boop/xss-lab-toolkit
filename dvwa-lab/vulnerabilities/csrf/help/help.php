<div class="body_padded">
	<h1>帮助-跨站点请求伪造（CSRF）</h1>

	<div id="code">
	<table width='100%' bgcolor='white' style="border:2px #C0C0C0 solid">
	<tr>
	<td><div id="code">
		<h3>关于</h3>
		<p>CSRF 是一种攻击，它强制最终用户在当前经过身份验证的Web应用程序上执行不需要的操作。借助社会工程的一点帮助（例如通过电子邮件/聊天发送链接），攻击者可能会迫使Web应用程序的用户执行攻击者的选择.</p>

		<p>成功地利用CSRF可以在正常用户情况下危害最终用户数据和操作。如果目标最终用户是管理员帐户，这可能会危害整个Web应用程序。</p>

		<p>这种攻击也可以称为“XSRF”，类似于“跨站点脚本（XSS）”，它们通常一起使用。</p>

		<br /><hr /><br />

		<h3>目标</h3>
		<p> 您的任务是让当前用户更改自己的密码，而不让他们知道自己的行为，使用CSRF攻击。 </p>

		<br /><hr /><br />

		<h3>低水平</h3>
		<p>目前还没有任何措施来防止这次袭击。这意味着一个链接可以被精心设计来实现某个动作（在本例中，更改当前用户的密码）。然后用一些基本的社会工程，让目标点击链接（或只是访问某个页面），触发动作。</p>
		<pre>扰流器: <span class="spoiler">?password_new=password&password_conf=password&Change=Change</span>.</pre>

		<br />

		<h3>中等水平</h3>
		<p>对于中级挑战，将检查最后一个请求页面的来源。开发人员认为如果它与当前域匹配，它必须来自Web应用程序，这样才能被信任。</p>
		<p> 可能需要连接多个漏洞以利用此向量，例如反射XSS。 </p>

		<br />

		<h3>高水平</h3>
		<p>在高层，开发人员添加了一个“反跨站点请求伪造（CSRF）令牌”。为了绕过此保护方法，需要另一个漏洞。</p>
		<pre>扰流器: <span class="spoiler">e.g. Javascript is a executed on the client side, in the browser</span>.</pre>

		<br />

		<h3>不可能的水平</h3>
		<p>在不可能的级别，挑战将扩展到高级别，并请求当前用户的密码。因为这是无法发现的（只有预测或暴力强迫）这里没有攻击向量。 </p>
	</div></td>
	</tr>
	</table>

	</div>

	<br />

	<p>Reference: <?php echo dvwaExternalLinkUrlGet( 'https://www.owasp.org/index.php/Cross-Site_Request_Forgery_(CSRF)' ); ?></p>
</div>
