
<%@ page language="java" contentType="text/html; charset=UTF-8"
	pageEncoding="UTF-8"%>
<!DOCTYPE html>
<html lang="en">

<head>
<meta charset="UTF-8">
<meta http-equiv="X-UA-Compatible" content="IE=edge">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Questions And Answers</title>
<style>
* {
	margin: 0;
	padding: 0;
	box-sizing: border-box;
	font-family: "Poppins", sans-serif;
}

.headercontainer {
	padding: 1.5em;
	color: snow;
	background-color: rgb(44, 44, 119);
	display: flex;
	flex-direction: row;
	justify-content: space-around;
}

.title {
	margin-top: 00.5em;
	font-size: larger;
	font-weight: bold;
	margin-right: auto;
}

.nav-content {
	display: flex;
	justify-content: space-around;
	flex-direction: row;
	margin: 0.5em;
	color: snow;
	text-decoration: none;
}

body {
	margin: 0;
	padding: 0px 10px;
}

.navbar {
	text-align: center;
	background-color: #746ee2;
	padding: 5px;
	color: white;
	font-family: sans-serif;
	z-index: 1000;
	left: 0;
	top: 0;
	overflow-y: auto;
	width: 100%;
	border-bottom: 2px solid;
}

li {
	display: inline-block;
	margin: 10px;
	font-size: 16px;
	padding: 0px 40px;
}

.welcome {
	text-align: center;
	background-color: #DBE9EE;
	font-family: Arial;
	font-size: 20px;
	padding: 30px 20px;
	width: 100%;
	margin: 0;
	box-sizing: border-box;
}

li:hover {
	color: black;
}

S
.question {
	text-align: center;
	font-size: 20px;
	color: red;
}

.answer {
	text-align: right;
	display: inline-block;
	padding: 0px 150px;
	margin: 20px;
	border: 2px solid;
	height: 90px;
	color: #252b36;
	padding-top: 40px;
}

.answer:hover {
	color: white;
	background-color: #C0D6DF;
}

h4 {
	color: #0a009c;
	font-family: sans-serif;
	font-weight: 100;
}

h2 {
	font-family: sans-serif;
	font-size: 20px;
}

h3 {
	font-family: sans-serif;
	font-weight: 100;
}

h1 {
	color: #466995;
}

h1:hover {
	color: grey;
}

body {
	background-image: url(/imagesweb/Section\ 4_Reasons\ To\ Vote_Blog.jpg);
	background-size: cover;
}
</style>

<%@ include file="headerlogin.html"%>
<body>

	<div class="welcome">

		<h1>WELCOME TO THE ELECTION QUESTIONS</h1>
		<p>We're looking forward to getting your answers so we can make
			sure our election and services are the best they can be!</p>
	</div>

	<div class=question>
		<h4>Question1</h4>
		<h2>Do you agree or disagree, Finland joins NATO</h2>
	</div>

	<div class="answer">
		<h3>Totally Disagree</h3>
	</div>
	<div class="answer">
		<h3>Partially Disagree</h3>
	</div>
	<div class="answer">
		<h3>NUETRAL</h3>
	</div>
	<div class="answer">
		<h3>Partially Agree</h3>
	</div>
	<div class="answer">
		<h3>Totally Agree</h3>
	</div>

	<div class="question">
		<h4>Question2</h4>
		<h2>Do you agree or disagree that the government should be used
			to equal the distribution of income in society</h2>
	</div>

	<div class="answer">
		<h3>Totally Disagree</h3>
	</div>
	<div class="answer">
		<h3>Partially Disagree</h3>
	</div>
	<div class="answer">
		<h3>NUETRAL</h3>
	</div>
	<div class="answer">
		<h3>Partially Agree</h3>
	</div>
	<div class="answer">
		<h3>Totally Agree</h3>
	</div>

	<div class="question">
		<h4>Question3</h4>
		<h2>Do you think that it is desireble or undesireble, that
			Ukraine applies for membership in the European Union?</h2>
	</div>
	<div class="answer">
		<h3>Totally Disagree</h3>
	</div>
	<div class="answer">
		<h3>Partially Disagree</h3>
	</div>
	<div class="answer">
		<h3>NUETRAL</h3>
	</div>
	<div class="answer">
		<h3>Partially Agree</h3>
	</div>
	<div class="answer">
		<h3>Totally Agree</h3>
	</div>

	<div class="question">
		<h4>Question4</h4>
		<h2>Do you think the existing government is going in the right
			direction to benefit the people of the country?</h2>
	</div>

	<div class="answer">
		<h3>Totally Disagree</h3>
	</div>
	<div class="answer">
		<h3>Partially Disagree</h3>
	</div>
	<div class="answer">
		<h3>NUETRAL</h3>
	</div>
	<div class="answer">
		<h3>Partially Agree</h3>
	</div>
	<div class="answer">
		<h3>Totally Agree</h3>
	</div>

	<div class="question">
		<h4>Question5</h4>
		<h2>How likely are you to vote in the coming elections?</h2>
	</div>

	<div class="answer">
		<h3>Totally Disagree</h3>
	</div>
	<div class="answer">
		<h3>Partially Disagree</h3>
	</div>
	<div class="answer">
		<h3>NUETRAL</h3>
	</div>
	<div class="answer">
		<h3>Partially Agree</h3>
	</div>
	<div class="answer">
		<h3>Totally Agree</h3>
	</div>

	<div class="question">
		<h4>Question6</h4>
		<h2>In your opinion, do you think gun control laws and
			regulations should be changed?</h2>
	</div>
	<div class="answer">
		<h3>Totally Disagree</h3>
	</div>
	<div class="answer">
		<h3>Partially Disagree</h3>
	</div>
	<div class="answer">
		<h3>NUETRAL</h3>
	</div>
	<div class="answer">
		<h3>Partially Agree</h3>
	</div>
	<div class="answer">
		<h3>Totally Agree</h3>
	</div>



</body>