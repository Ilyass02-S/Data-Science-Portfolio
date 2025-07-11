<%@ page import = "team10.UserDao" %>
<%@ page import = "team10.User" %>

<%-- 
// String email = (String) request.getSession().getAttribute("email");
// System.out.println(email);
// if (email == null) response.sendRedirect("homepage.jsp");
// // get the User from the database that has the email=email
// // SELECT * FROM users WHERE email = ?
// User user = UserDao.getUser(email);
--%>
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
<link rel="stylesheet" href="/homepage.css" />
<link rel="stylesheet" href="/candidates.css" />
</head>
<body>
	<%@ include file="header.html"%>
	<div class="container">
		<div class="content">
			<div class="candidate">
				<div class="pic"></div>
				<a href="profile.jsp">
					<div class="profilname">mehdi lmontadar
				</a>
			</div>
		</div>
		<div class="candidate">
			<div class="pic"></div>
			<a href="profile.jsp">
				<div class="profilname"> ilyass lmanhous
			</a>
		</div>
	</div>
	<div class="candidate">
		<div class="pic"></div>
		<a href="profile.jsp">
			<div class="profilname"> yasser l9hba
		</a>
	</div>
	</div>
	</div>
	</div>
	<%@ include file="footer.html"%>