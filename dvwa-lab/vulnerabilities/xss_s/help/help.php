<div class="body_padded">
	<h1>Help - Cross Site Scripting (Stored)</h1>

	<div id="code">
	<table width='100%' bgcolor='white' style="border:2px #C0C0C0 solid">
	<tr>
	<td><div id="code">
		<p>“跨站点脚本（XSS）”攻击是一种注入问题，在这种问题中，恶意脚本被注入到良性和可信的网站中。当攻击者使用Web应用程序发送恶意代码（通常以浏览器端脚本的形式）时，会发生XSS攻击。给不同的最终用户。允许这些攻击成功的缺陷非常普遍，并且发生在Web应用程序使用输出中用户输入的任何地方，没有验证或编码。</p>

		<p>攻击者可以使用XSS将恶意脚本发送给不知情的用户。最终用户的浏览器无法知道不应信任该脚本，并执行javascript。因为它认为脚本来自可信源，恶意脚本可以访问任何cookie、会话令牌或其他由浏览器保留并与该网站一起使用的敏感信息。这些脚本甚至可以重写HTML页面的内容。</p>

		<p> XSS存储在数据库中。XSS是永久的，直到重置数据库或手动删除有效负载。 </p>

		<br /><hr /><br />

		<h3>目标</h3>
		<p> 将所有人重定向到您选择的网页。 </p>

		<br /><hr /><br />

		<h3>低水平</h3>
		<p> 低水平将不检查请求的输入，在将其包括在输出文本中使用之前。 </p>
		<pre>扰流器: <span class="spoiler"> 名称或消息字段 : &lt;script&gt;alert("XSS");&lt;/script&gt;</span>.</pre>

		<br />

		<h3>中水平</h3>
		<p> 开发人员添加了一些保护，但并没有以相同的方式对每个字段进行保护。 </p>
		<pre>扰流器: <span class="spoiler">名称字段: &lt;sCriPt&gt;alert("XSS");&lt;/sCriPt&gt;</span>.</pre>

		<br />

		<h3>高水平</h3>
		<p> 开发人员认为他们已经通过删除模式禁用了所有脚本使用。  "&lt;s*c*r*i*p*t".</p>
		<pre>扰流器: <span class="spoiler"> HTML事件 </span>.</pre>

		<br />

		<h3>不可能的水平</h3>
		<p> 使用内置的PHP函数（例如  "<?php echo dvwaExternalLinkUrlGet( 'https://secure.php.net/manual/en/function.htmlspecialchars.php', 'htmlspecialchars()' ); ?>"),
			 它可以转义任何改变输入行为的值。 </p>
	</div></td>
	</tr>
	</table>

	</div>

	<br />

	<p>参考文献: <?php echo dvwaExternalLinkUrlGet( 'https://www.owasp.org/index.php/Cross-site_Scripting_(XSS)' ); ?></p>
</div>
