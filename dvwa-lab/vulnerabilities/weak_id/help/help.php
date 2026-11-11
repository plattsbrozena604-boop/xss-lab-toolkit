<div class="body_padded">
	<h1>Help - Weak Session IDs</h1>

	<div id="code">
	<table width='100%' bgcolor='white' style="border:2px #C0C0C0 solid">
	<tr>
	<td><div id="code">
		<h3>关于</h3>
		<p>会话ID的知识通常是作为特定用户登录后访问站点所需的唯一内容，如果该会话ID能够计算或容易猜测，那么攻击者就可以轻松访问用户帐户，而无需强行输入密码或查找其他漏洞，如 Cross-Site Scripting.</p>

		<p><hr /></p>

		<h3>目标</h3>
		<p>本模块使用四种不同的方法来设置dvwasession cookie值，每个级别的目标是确定如何生成ID，然后推断其他系统用户的ID。</p>

		<p><hr /></p>

		<h3>低水平</h3>
		<p> cookie值应该很明显是可预测的。 </p>

		<h3>中水平</h3>
		<p> 这个值看起来比低值更随机，但是如果你收集了一些，你应该开始看到一个模式。 </p>

		<h3>高水平</h3>
		<p> 首先计算出值采用的格式，然后尝试计算出将什么作为输入来生成值。 </p>
		<p>额外的标志也被添加到cookie中，这不会影响挑战，但会突出显示可以添加以保护cookie的额外保护。 </p>


		<h3>不可能的水平</h3>
		<p>在这个级别上，cookie值不应该是可预测的，但您可以随意尝试。 </p>
		<p>除了额外的标志之外，cookie还被绑定到域和挑战的路径上。</p>
	</div></td>
	</tr>
	</table>

	</div>

	<p>参考文献: <?php echo dvwaExternalLinkUrlGet( 'https://www.owasp.org/index.php/Top_10_2013-A2-Broken_Authentication_and_Session_Management' ); ?></p>
</div>
