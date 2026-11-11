<div class="body_padded">
	<h1>Help - SQL Injection</h1>

	<div id="code">
	<table width='100%' bgcolor='white' style="border:2px #C0C0C0 solid">
	<tr>
	<td><div id="code">
		<h3>关于</h3>
		<p>SQL注入攻击包括通过从客户端到应用程序的输入数据插入或“注入”SQL查询。成功的SQL注入漏洞可以从数据库中读取敏感数据、修改数据库数据（插入/更新/删除）、对数据库执行管理操作。（例如关闭DBMS），恢复DBMS文件系统上存在的给定文件的内容（加载文件），在某些情况下向操作系统发出命令。</p>

		<p> SQL注入攻击是一种注入攻击，其中SQL命令被注入到数据平面输入中，以影响预定义SQL命令的执行。 </p>

		<p>这种攻击也可以称为 "SQLi".</p>

		<br /><hr /><br />

		<h3>目标</h3>
		<p> 数据库中有5个用户，ID从1到5。你的任务…通过sqli窃取他们的密码。 </p>

		<br /><hr /><br />

		<h3>低水平</h3>
		<p>SQL查询使用由攻击者直接控制的原始输入。他们所需要做的就是退出查询，然后执行他们想要的任何SQL查询。 </p>
		<pre>扰流器: <span class="spoiler">?id=a' UNION SELECT "text1","text2";-- -&Submit=Submit</span>.</pre>

		<br />

		<h3>中水平</h3>
		<p> 中水平使用一种SQL注入保护形式，具有 
			"<?php echo dvwaExternalLinkUrlGet( 'https://secure.php.net/manual/en/function.mysql-real-escape-string.php', 'mysql_real_escape_string()' ); ?>".
			 但是，由于SQL查询在参数周围没有引号，这不会完全保护查询不被更改。 </p>

		<p> 文本框已替换为预定义的下拉列表，并使用Post提交表单。 </p>
		<pre>扰流器: <span class="spoiler">?id=a UNION SELECT 1,2;-- -&Submit=Submit</span>.</pre>

		<br />

		<h3>高水平</h3>
		<p>这与低水平非常相似，但是这次攻击者以不同的方式输入值。输入值通过会话变量使用另一个页面传输到易受攻击的查询，而不是直接获取请求。</p>
		<pre>扰流器: <span class="spoiler">ID: a' UNION SELECT "text1","text2";-- -&Submit=Submit</span>.</pre>

		<br />

		<h3>不可能的水平</h3>
		<p>查询现在是参数化查询（而不是动态查询）。这意味着查询是由开发人员定义的，并区分哪些部分是代码，其余部分是数据。</p>
	</div></td>
	</tr>
	</table>

	</div>

	<br />

	<p>参考文献: <?php echo dvwaExternalLinkUrlGet( 'https://www.owasp.org/index.php/SQL_Injection' ); ?></p>
</div>
