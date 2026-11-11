<div class="body_padded">
	<h1>帮助-客户端javascript</h1>

	<div id="code" style="padding: 3px; border: 2px #C0C0C0 solid;>">
		<h3>关于</h3>
		<p>本节中的攻击旨在帮助您了解浏览器中如何使用JavaScript以及如何操作它。这些攻击可以通过分析网络流量来进行，但这不是重点，而且可能会更加困难。</p>

		<hr />
		
		<h3>目标</h3>
		<p>只需提交短语“成功”即可赢得级别。显然，这并不容易，每个级别实现不同的保护机制，页面中包含的javascript必须进行分析，然后进行操作以绕过保护。</p>

		<hr />
		<h3>低水平</h3>
		<p>所有的javascript都包含在页面中。读取源代码，找出生成与短语匹配所需的令牌所使用的函数，然后手动调用该函数。 </p>
		<pre>扰流器: <span class="spoiler">将短语更改为success，然后使用函数generate_token（）更新令牌。</span></pre>

		<p><br /></p>

		<h3>中水平</h3>
		<p>
			 javascript已经被分解成自己的文件，然后最小化。您需要查看包含文件的源文件，然后计算出它在做什么。火狐和Chrome都有一个漂亮的打印功能，它试图以可读的方式反向压缩和显示代码。 
		</p>
		<pre>扰流器: <span class="spoiler"> 文件使用setTimeout函数运行生成令牌的do-elsesometing函数。</span></pre>

		<p><br /></p>

		<h3>高水平</h3>
		<p>
			 至少有一个引擎混淆了javascript。您将需要逐步通过这些代码来确定什么有用，什么是垃圾，以及完成任务需要什么。 
		</p>
		<pre>扰流器: <span class="spoiler"> 如果有用的话，已经使用了两个封隔器，第一个封隔器来自  <a href="https://www.danstools.com/javascript-obfuscate/index.php">丹的工具</a> 第二个是 <a href="https://javascriptobfuscator.herokuapp.com/">JavaScript  混淆工具 </a>.</span></pre>
		<pre>扰流器 2: <span class="spoiler"> 这个deobfuscation工具在这个代码上似乎最有效。  <a href="http://deobfuscatejavascript.com/">解除混淆 javascript</a>.</span></pre>
		<pre>扰流器 3: <span class="spoiler"> 这是一种方法…通过deobfuscation应用程序运行模糊JS，拦截模糊JS的响应并在可读版本中交换。计算出流程，您将看到三个需要按顺序调用的函数。使用正确的参数在正确的时间调用函数。 </pre>

		<p><br /></p>

		<h3>不可能的水平</h3>
		<p>您永远不能信任用户，必须假设发送给用户的任何代码都可以被操作或绕过，因此没有不可能的水平。</p>

	</div>

	<br />

	<p>参考文献:</p>
	<ul>
		<li><?php echo dvwaExternalLinkUrlGet( 'https://www.youtube.com/watch?v=8UqHCrGdxOM' )?></li>
		<li><?php echo dvwaExternalLinkUrlGet( 'https://www.w3schools.com/js/' )?></li>
		<li><?php echo dvwaExternalLinkUrlGet( 'https://www.youtube.com/watch?v=cs7EQdWO5o0&index=17&list=WL' )?></li>
		<li><?php echo dvwaExternalLinkUrlGet( 'https://www.youtube.com/playlist?list=PLC9K7uaDMdAUNktlDTxsmj6rJBf4Q9TR5' )?></li>
	</ul>
</div>
