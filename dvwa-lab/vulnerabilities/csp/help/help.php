<div class="body_padded">
	<h1>帮助-绕过内容安全策略（CSP）</h1>

	<div id="code">
	<table width='100%' bgcolor='white' style="border:2px #C0C0C0 solid">
	<tr>
	<td><div id="code">
		<h3>关于</h3>
		<p> 内容安全策略（CSP）用于定义从何处加载或执行脚本和其他资源。本模块将指导您根据开发人员的常见错误绕过策略。 </p>
		<p> 这些漏洞都不是CSP中的实际漏洞，它们是实施过程中的漏洞。 </p>

		<br /><hr /><br />

		<h3>目标</h3>
		<p> 绕过内容安全策略（CSP）并在页面中执行javascript。 </p>

		<br /><hr /><br />

		<h3>低水平</h3>
		<p>检查策略以查找可用于承载外部脚本文件的所有源.</p>
		<pre>扰流器: <span class="spoiler">Scripts can be included from Pastebin, try storing some JavaScript on there and then loading it in.</span></pre>

		<br />

		<h3>中水平</h3>
		<p> CSP策略试图使用nonce防止攻击者添加内联脚本。 .</p>
		<pre>扰流器: <span class="spoiler"> 检查一下nonce，看看它是如何变化的（或者没有变化）。 </span></pre>

		<br />

		<h3>高水平 </h3>
		<p>页面对source/jsonp.php进行jsonp调用，将要回调的函数名传递给，您需要修改jsonp.php脚本来更改回调函数。</p>
		<pre>扰流器: <span class="spoiler">页面上的javascript将执行页面返回的任何内容，将其更改为您自己的代码将执行该操作。</span></pre>

		<br />

		<h3>不可能的水平</h3>
		<p>
			此级别是对高级的更新，其中jsonp调用的回调函数是硬编码的，并且CSP策略被锁定为仅允许外部脚本。
		</p>
	</div></td>
	</tr>
	</table>

	</div>

	<br />

	<p>参考文献: <?php echo dvwaExternalLinkUrlGet( 'https://content-security-policy.com/', "Content Security Policy Reference" ); ?></p>
	<p>参考文献: <?php echo dvwaExternalLinkUrlGet( 'https://developer.mozilla.org/en-US/docs/Web/HTTP/CSP', "Mozilla Developer Network - CSP: script-src"); ?></p>
	<p>参考文献: <?php echo dvwaExternalLinkUrlGet( 'https://blog.mozilla.org/security/2014/10/04/csp-for-the-web-we-have/', "Mozilla Security Blog - CSP for the web we have" ); ?></p>
</div>
