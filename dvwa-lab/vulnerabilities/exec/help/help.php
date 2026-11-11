<div class="body_padded">
	<h1> 帮助-命令注入 </h1>

	<div id="code">
	<table width='100%' bgcolor='white' style="border:2px #C0C0C0 solid">
	<tr>
	<td><div id="code">
		<h3>关于</h3>
		<p>命令注入攻击的目的是注入和执行攻击者在易受攻击的应用程序中指定的命令。在这种情况下，执行不需要的系统命令的应用程序就像一个伪系统外壳，攻击者可以使用它作为任何授权系统用户。但是，命令的执行权限和环境与Web服务相同。</p>

		<p>在大多数情况下，命令注入攻击是可能的，因为缺乏正确的输入数据验证，攻击者可以操纵这些验证。（表单、cookie、HTTP头等）。</p>

		<p> 根据所需的操作，Linux和Windows等操作系统之间的语法和命令可能有所不同。 </p>

		<p> 这种攻击也可以称为“远程命令执行（RCE）”。 </p>

		<br /><hr /><br />

		<h3>目标</h3>
		<p> 远程查找操作系统上的Web服务用户，以及通过RCE查找机器主机名。 </p>

		<br /><hr /><br />

		<h3>低水平</h3>
		<p>这允许直接输入将在操作系统上执行命令的<u>多个php函数之一。可以脱离设计的命令执行了无意的行动。</p>
		<p> 这可以通过向请求添加“一旦命令成功执行，运行此命令”来完成。 </p>
		<pre>扰流器: <span class="spoiler">添加命令 "&&"</span>. 例子: <span class="spoiler">127.0.0.1 && dir</span>.</pre>

		<br />

		<h3>中水平</h3>
		<p> 开发人员已经阅读了命令注入的一些问题，并放置了各种模式补丁来过滤输入。然而，这还不够。 </p>
		<p> 可以使用各种其他系统语法来中断所需的命令。 </p>
		<pre>扰流器: <span class="spoiler">e.g.  后台ping命令 </span>.</pre>

		<br />

		<h3>高水平</h3>
		<p> 在高水平中，开发人员返回到绘图板并放入更多的模式来匹配。但即使这样也不够。 </p>
		<p> 开发人员要么对过滤器做了轻微的拼写错误，并相信某个PHP命令可以避免这种错误。 </p>
		<pre>扰流器: <span class="spoiler"><?php echo dvwaExternalLinkUrlGet( 'https://secure.php.net/manual/en/function.trim.php', 'trim()' ); ?>
		删除所有前导和尾随空格，对吗？ </span>.</pre>

		<br />

		<h3>不可能的水平</h3>
		<p>在不可能的水平中，挑战被重新编写，只允许非常严格的输入。如果这不匹配并且不能产生某种结果，不允许执行。而不是“黑名单”过滤（允许任何输入和删除不需要的），这使用“白名单”（只允许某些值）。</p>
	</div></td>
	</tr>
	</table>

	</div>

	<br />

	<p>参考文献: <?php echo dvwaExternalLinkUrlGet( 'https://www.owasp.org/index.php/Command_Injection' ); ?></p>
</div>
