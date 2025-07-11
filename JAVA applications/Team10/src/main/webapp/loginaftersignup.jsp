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
    <link rel="stylesheet" href="/signup.css" />
    <%@ include file="header.html"%>
    <body>
    <div class="login-html">
            <input id="tab-1" type="radio" name="tab" class="sign-in" checked><label
                for="tab-1" class="tab">Sign In</label> <input id="tab-2"
                type="radio" name="tab" class="sign-up"><label for="tab-2"
                class="tab">Sign Up</label>
            <div class="login-form">
                <form class="sign-in-htm" action="/login" method="post">
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
   
    </body>