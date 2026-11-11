<div class="body_padded">
	<h1>Help - Cross Site Scripting (DOM Based)</h1>

	<div id="code">
	<table width='100%' bgcolor='white' style="border:2px #C0C0C0 solid">
	<tr>
	<td><div id="code">
		<h3>关于</h3>
		<p>“跨站点脚本（XSS）”攻击是一种注入问题，在这种问题中，恶意脚本被注入到良性和可信的网站中。当攻击者使用Web应用程序发送恶意代码（通常以浏览器端脚本的形式）时，会发生XSS攻击。给不同的最终用户。允许这些攻击成功的缺陷非常普遍，并且发生在Web应用程序使用输出中用户输入的任何地方，没有验证或编码。</p>

		<p>攻击者可以使用XSS将恶意脚本发送给不知情的用户。最终用户的浏览器无法知道不应信任该脚本，并执行javascript。因为它认为脚本来自可信源，恶意脚本可以访问任何cookie、会话令牌或其他由浏览器保留并与该网站一起使用的敏感信息。这些脚本甚至可以重写HTML页面的内容。</p>

		<p>基于DOM的XSS是一种特殊的情况，它反映了javascript隐藏在URL中，并在呈现时由javascript在页面中拉出，而不是在提供服务时嵌入到页面中。这可以使它比其他攻击和WAF或其他正在读取页面正文的保护更隐蔽，不会看到任何恶意内容。</p>

		<p><hr /></p>

		<h3>目标</h3>
		<p>在另一个用户的浏览器中运行自己的javascript，使用它来窃取登录用户的cookie。</p>

		<p><hr /></p>

		<h3>低水平</h3>
		<p>低水平 在将其包含在输出文本中之前，不会检查请求的输入。 </p>
		<pre>扰流器: <span class="spoiler"><?=htmlentities ("/vulnerabilities/xss_d/?default=English<script>alert(1)</script>")?></span>.</pre>

		<p><br /></p>

		<h3>中水平</h3>
		<p> 开发人员试图添加一个简单的模式匹配来删除任何参考文献  "&lt;script"  禁用任何javascript。找到一种不使用脚本标记运行javascript的方法。 </p>
		<pre>扰流器: <span class="spoiler">必须先从选择块中分离出来，然后才能添加具有OnError事件的图像:<br />
<?=htmlentities ("/vulnerabilities/xss_d/?default=English>/option></select><img src='x' onerror='alert(1)'>");?></span>.</pre>

		<p><br /></p>

		<h3>高水平</h3>
		<p>开发人员现在只列出了允许的语言，您必须找到一种方法来运行您的代码，而不必将其发送到服务器。</p>
		<pre>扰流器: <span class="spoiler">URL的片段部分（任何在#符号之后的部分）不会发送到服务器，因此无法阻止。用于呈现页面的错误javascript在创建页面时从中读取内容。<br />
<?=htmlentities ("/vulnerabilities/xss_d/?default=English#<script>alert(1)</script>")?></span>.</pre>

		<p><br /></p>

		<h3>不可能的水平</h3>
		<p>大多数浏览器默认对从URL获取的内容进行编码，以防止执行任何注入的javascript。</p>
	</div></td>
	</tr>
	</table>

	</div>

	<br />

	<p>参考文献: <?php echo dvwaExternalLinkUrlGet( 'https://www.owasp.org/index.php/Cross-site_Scripting_(XSS)' ); ?></p>
</div>
