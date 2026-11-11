<div class="body_padded">
	<h1>Help - SQL Injection (Blind)</h1>

	<div id="code">
	<table width='100%' bgcolor='white' style="border:2px #C0C0C0 solid">
	<tr>
	<td><div id="code">
		<h3>关于</h3>
		<p>当攻击者执行SQL注入攻击时，有时服务器会响应来自数据库服务器的错误消息，抱怨SQL查询的语法不正确。盲SQL注入与正常的SQL注入相同，只是当攻击者试图利用应用程序，而不是获取有用的错误消息时，他们得到的是开发人员指定的通用页面。这使得利用潜在的SQL注入攻击变得更加困难，但并非不可能。攻击者仍然可以通过SQL语句询问一系列正确和错误的问题，并监视Web应用程序如何响应来窃取数据。（有效条目RETURED或404头集）。</p>

		<p>“基于时间”的注入方法通常用于没有可见反馈的情况下，页面的响应如何不同（因此是一种盲攻击）。这意味着攻击者将等待页面返回响应所需的时间。如果时间比正常时间长，则查询成功。</p>

		<br /><hr /><br />

		<h3>目标</h3>
		<p> 通过盲SQL攻击查找SQL数据库软件的版本。 </p>

		<br /><hr /><br />

		<h3>低水平</h3>
		<p>SQL查询使用由攻击者直接控制的原始输入。他们所需要做的就是退出查询，然后执行他们想要的任何SQL查询。</p>
		<pre>扰流器: <span class="spoiler">?id=1' AND sleep 5&Submit=Submit</span>.</pre>

		<br />

		<h3>中水平</h3>
		<p> 中水平使用一种SQL注入保护形式，具有 
			"<?php echo dvwaExternalLinkUrlGet( 'https://secure.php.net/manual/en/function.mysql-real-escape-string.php', 'mysql_real_escape_string()' ); ?>".
			 但是，由于SQL查询在参数周围没有引号，这不会完全保护查询不被更改。 </p>

		<p> 文本框已替换为预定义的下拉列表，并使用Post提交表单。 </p>
		<pre>扰流器: <span class="spoiler">?id=1 AND sleep 3&Submit=Submit</span>.</pre>

		<br />

		<h3>高水平</h3>
		<p>这与低水平非常相似，但是这次攻击者以不同的方式输入值。输入值设置在不同的页面上，而不是GET请求。</p>
		<pre>扰流器: <span class="spoiler">ID: 1' AND sleep 10&Submit=Submit</span>.
			扰流器: <span class="spoiler"> 应该可以切断中间人。 </span>.</pre>

		<br />

		<h3>不可能的水平</h3>
		<p>查询现在是参数化查询（而不是动态查询）。这意味着查询是由开发人员定义的，并区分哪些部分是代码，其余部分是数据。</p>
	</div></td>
	</tr>
	</table>

	</div>

	<br />

	<p>参考文献: <?php echo dvwaExternalLinkUrlGet( 'https://www.owasp.org/index.php/Blind_SQL_Injection' ); ?></p>
</div>
