<%@ page language="java" contentType="text/html; charset=ISO-8859-1"
    pageEncoding="ISO-8859-1"%>
  
<%@ taglib prefix="c" uri="http://java.sun.com/jsp/jstl/core" %>
<%@ page import="app.model.Game" %> 
    
<!DOCTYPE html>
<html>
<head>
<meta charset="ISO-8859-1">
<title>Edit Game</title>
</head>
<body>

	<form action='./editgame' method='post'>
		Breed: <input type='text' name='breed' value='${sessionScope.game.breed }'><br>
		Weight: <input type='text' name='weight' value='${sessionScope.game.weight }'><br>
		<input type="hidden" name="id" value="${sessionScope.game.id }">		
		<input type='submit' name='ok' value='Edit'>
	</form>

</body>
</html>