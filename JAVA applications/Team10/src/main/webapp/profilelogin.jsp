<%@ page import = "team10.UserDao" %>
<%@ page import = "team10.User" %>

<%
String email = (String) request.getSession().getAttribute("email");
System.out.println(email);
if (email == null) response.sendRedirect("homepage.jsp");
// get the User from the database that has the email=email
// SELECT * FROM users WHERE email = ?
User user = UserDao.getUser(email);
%>

<!DOCTYPE html>
<html lang="en">

<head>
<meta charset="UTF-8">
<meta http-equiv="X-UA-Compatible" content="IE=edge">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Profile Page</title>
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

</body>

</html>
<link
	href="//maxcdn.bootstrapcdn.com/bootstrap/4.1.1/css/bootstrap.min.css"
	rel="stylesheet" id="bootstrap-css">
<script
	src="//maxcdn.bootstrapcdn.com/bootstrap/4.1.1/js/bootstrap.min.js"></script>
<script
	src="//cdnjs.cloudflare.com/ajax/libs/jquery/3.2.1/jquery.min.js"></script>
<!------ Include the above in your HEAD tag ---------->


<style>
body {
	background: -webkit-linear-gradient(left, #3931af, #9da4d7);
}

.emp-profile {
	padding: 3%;
	margin-top: 3%;
	margin-bottom: 29%;
	border-radius: 0.5rem;
	background: #fff;
	max-width: 60%;
	height: 50%;
}

.profile-img {
	text-align: center;
}

.profile-img img {
	width: 70%;
	height: 100%;
}

.profile-img .file {
	position: relative;
	overflow: hidden;
	margin-top: -20%;
	width: 70%;
	border: none;
	border-radius: 0;
	font-size: 15px;
	background: #212529b8;
}

.profile-img .file input {
	position: absolute;
	opacity: 0;
	right: 0;
	top: 0;
}

.profile-head h5 {
	color: #333;
}

.profile-head h6 {
	color: #0062cc;
}

.profile-edit-btn {
	border: none;
	border-radius: 1.5rem;
	width: 95%;
	padding: 2%;
	font-weight: 600;
	color: #6c757d;
	cursor: pointer;
}

.proile-rating {
	font-size: 12px;
	color: #818182;
	margin-top: 5%;
}

.proile-rating span {
	color: #495057;
	font-size: 15px;
	font-weight: 600;
}

.profile-head .nav-tabs {
	margin-bottom: 5%;
}

.profile-head .nav-tabs .nav-link {
	font-weight: 600;
	border: none;
}

.profile-head .nav-tabs .nav-link.active {
	border: none;
	border-bottom: 2px solid #0062cc;
}

.profile-work {
	padding: 15%;
	margin-top: -15%;
}

.profile-work p {
	font-size: 12px;
	color: #818182;
	font-weight: 600;
	margin-top: 10%;
}

.profile-work a {
	text-decoration: none;
	color: #495057;
	font-weight: 600;
	font-size: 14px;
}

.profile-work ul {
	list-style: none;
}

.profile-tab label {
	font-weight: 600;
}

.profile-tab p {
	font-weight: 600;
	color: #0062cc;
}
</style>

<div class="container emp-profile">
	<form method="post">
		<div class="row">
			
			<div class="col-md-6">
				<div class="profile-head">
					<h5><% out.print(user.getFullname()); %></h5>
					<h6>Election Candidate</h6>

					<ul class="nav nav-tabs" id="myTab" role="tablist">
						<li class="nav-item"><a class="nav-link active" id="home-tab"
							data-toggle="tab" href="#home" role="tab" aria-controls="home"
							aria-selected="true">About</a></li>

					</ul>
				</div>
			</div>
			<div class="col-md-2">
				<input type="submit" class="profile-edit-btn" name="btnAddMore"
					value="Edit Profile" />
			</div>
		</div>
		<div class="row">
			<div class="col-md-4">
				<div class="profile-work">
					<p>Profile</p>
					<a href="questions.jsp"> Answer Questions</a><br />

				</div>
			</div>
			<div class="col-md-8">
				<div class="tab-content profile-tab" id="myTabContent">
					<div class="tab-pane fade show active" id="home" role="tabpanel"
						aria-labelledby="home-tab">
						<div class="row">
							<div class="col-md-6">
								<label>Name</label>
							</div>
							<div class="col-md-6">
								<p><% out.print(user.getFullname()); %></p>
							</div>
						</div>
						<div class="row">
							<div class="col-md-6">
								<label>Email</label>
							</div>
							<div class="col-md-6">
								<p><% out.print(user.getEmail()); %></p>
							</div>
						</div>
						<div class="row">
							<div class="col-md-6">
								<label>Phone</label>
							</div>
							<div class="col-md-6">
								<p><% out.print(user.getphone()); %></p>
							</div>
						</div>
						<div class="row">
							<div class="col-md-6">
								<label>Profession</label>
							</div>
							<div class="col-md-6">
								<p><% out.print(user.getprofession()); %></p>
							</div>
						</div>
					</div>