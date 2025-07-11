<!DOCTYPE html>
<html lang="en">

<head>
<meta charset="UTF-8" />
<meta http-equiv="X-UA-Compatible" content="IE=edge" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<title>EVOTE</title>
<link rel="preconnect" href="https://fonts.googleapis.com" />
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
<link href="https://fonts.googleapis.com/icon?family=Material+Icons"
	rel="stylesheet" />
<link
	href="https://fonts.googleapis.com/css2?family=Poppins&family=Spartan:wght@500&display=swap"
	rel="stylesheet" />
	<link rel="stylesheet" href="/index.css" />
	
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
</style>
</head>
<%@ include file="headerlogin.html"%>
<body>
	
	<form action='./EVOTE' method='post'>
		<div class="main-container">
			<div class="content1">
				<div class="title1">Why you should Vote!</div>
				<div class="img1">
					<div class="img1txt">You have the power to decide on the
						quality of life you want for yourself and future generations.
						Voting is your chance to stand up for the issues you care about
						like public transportation, raising minimum wage, or funding local
						schools. This is your life: take the time to help decide what’s
						best.</div>
				</div>
			</div>
			<div class="content2">
				<div class="img2">
					<div class="img2txt">Do you want to make a positive impact?
						Voting gives you that chance! Support the candidates and ballot
						measures that can help your community, state, and even the nation
						for the greater good. Make your voice heard in these elections.</div>
				</div>
			</div>
		</div>
	</form>
	<%@ include file="footer.html"%>
</body>
</html>