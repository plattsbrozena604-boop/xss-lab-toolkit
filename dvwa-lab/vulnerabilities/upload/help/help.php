<div class="body_padded">
	<h1>Help - File Upload</h1>

	<div id="code">
	<table width='100%' bgcolor='white' style="border:2px #C0C0C0 solid">
	<tr>
	<td><div id="code">
		<h3>关于</h3>
		<p>上载的文件对Web应用程序来说是一个巨大的风险。许多攻击的第一步是将一些代码发送到要被攻击的系统。然后攻击者只需要找到一种方法来执行代码。使用文件上传可以帮助攻击者完成第一步。</p>

		<p>不受限制的文件上传的后果可能不同，包括完全的系统接管、过载的文件系统、将攻击转发到后端系统，以及简单的脱脂。这取决于应用程序如何处理上载的文件，包括存储文件的位置。</p>

		<br /><hr /><br />

		<h3>目标</h3>
		<p>在目标系统上执行您选择的任何PHP函数（例如 <?php echo dvwaExternalLinkUrlGet( 'https://secure.php.net/manual/en/function.phpinfo.php', 'phpinfo()' ); ?>
			或 <?php echo dvwaExternalLinkUrlGet( 'https://secure.php.net/manual/en/function.system.php', 'system()' ); ?>)  由于此文件上载漏洞。 </p>

		<br /><hr /><br />

		<h3>低水平</h3>
		<p> 低水平不会以任何方式检查上传文件的内容。它只依赖信任。 </p>
		<pre>扰流器: <span class="spoiler"> 上载任何包含命令的有效PHP文件 </span>.</pre>

		<br />

		<h3>中水平</h3>
		<p> 当使用中间水平时，它将在上传时从客户端检查报告的文件类型。 </p>
		<pre>扰流器: <span class="spoiler"> 值得在任何“hidden”表单字段中查找任何限制 </span>.</pre>

		<br />

		<h3>高水平</h3>
		<p> 从客户机收到文件后，服务器将尝试调整请求中包含的任何图像的大小。 </p>
		<pre>扰流器: <span class="spoiler"> 需要链接到另一个漏洞，如文件包含 </span>.</pre>

		<br />

		<h3>不可能的水平</h3>
		<p>这将检查到目前为止所有级别的所有内容，然后重新编码图像。这将生成一个新图像，从而剥离任何“非图像”代码（包括元数据）。</p>
	</div></td>
	</tr>
	</table>

	</div>

	<br />

	<p>参考文献: <?php echo dvwaExternalLinkUrlGet( 'https://www.owasp.org/index.php/Unrestricted_File_Upload' ); ?></p>
</div>

