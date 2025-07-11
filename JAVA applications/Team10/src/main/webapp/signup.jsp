<!DOCTYPE html>
<html lang="en">

<head>
<meta charset="UTF-8" />
<meta http-equiv="X-UA-Compatible" content="IE=edge" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<title>EVOTE</title>
<link rel="preconnect" href="https://fonts.googleapis.com" />
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
<link
	href="https://fonts.googleapis.com/css2?family=Poppins&family=Spartan:wght@500&display=swap"
	rel="stylesheet" />
<link rel="stylesheet" href="/signup.css" />
</head>


<body>
	<%@ include file="header.html"%>
	<div class="login-wrap">
		<div class="login-html">
			<input id="tab-1" type="radio" name="tab" class="sign-in" checked><label
				for="tab-1" class="tab">Sign In</label> <input id="tab-2"
				type="radio" name="tab" class="sign-up"><label for="tab-2"
				class="tab">Sign Up</label>
			<div class="login-form">
				<form class="sign-in-htm" action="/login" method="post" onsubmit="return formvalidation()">
					<div class="group">
						<label for="user" class="label">Email</label> <input id="mail"
							type="text" class="input" name="email">
					</div>
					<div class="group">
						<label for="pass" class="label">Password</label> <input id="pas"
							type="password" class="input" name="password">
					</div>
					<div class="group">
						<input id="check" type="checkbox" class="check" checked> <label
							for="check"><span class="icon"></span> Keep me Signed in</label>
					</div>
					<div class="group">
						<input type="submit" class="button" value="submit">
					</div>
					<div class="hr"></div>

				</form>
				<form class="sign-up-htm" action="/signup" method="post" onsubmit="return formvalidation()">
					<div class="group">
						<label for="user" class="label">Full name</label> <input id="user"
							type="text" class="input" name="fullname">
					</div>
					<div class="group">
						<label for="pass" class="label">Email Address</label> <input
							id="pass" type="text" class="input" name="email">
					</div>
					<div class="group">
						<label for="pass" class="label">Password</label> <input id="pass"
							type="password" class="input" name="password">
					</div>
					<div class="group">
						<label for="pass" class="label">Phone</label> <input id="phone"
							type="text" class="input" name="phone">
					</div>
					<div class="group">
						<label for="pass" class="label">Profession</label> <input
							id="profession" type="text" class="input" name="profession">
					</div>
					<div class="group">
						<input type="submit" class="button" value="submit" />
					</div>

					<div class="hr"></div>
					<div class="foot-lnk">
						<span>Already Member?</span>
					</div>
				</form>
			</div>
		</div>
	</div>

</body>
<script>
 
            // checkinputs function
 
        function formvalidation() {
        var fullname = document.forms["login-html"]["fullname"];
        var phone = document.forms["login-html"]["phone"];
        var email = document.forms["login-html"]["email"];
        var password = document.forms["login-html"]["password"];
        var profession = document.forms["login-html"]["profession"];
        
  
        if (fullname.value == "") {
            window.alert("Please enter your Full Name.");
            fullname.focus();
            return false;
        }
  
        if (phone.value == "") {
            window.alert("Please enter your phone.");
            phone.focus();
            return false;
        }
  
        if (email.value == "") {
            window.alert("Please enter a valid E-mail address.");
            email.focus();
            return false;
        }
  
  
        if (password.value == "") {
            window.alert("Please enter your password");
            password.focus();
            return false;
        }
 
        if (profession.value == "") {
            window.alert("Please confirm your profession");
            profession.focus();
            return false;
    
    }
</script>

</html>