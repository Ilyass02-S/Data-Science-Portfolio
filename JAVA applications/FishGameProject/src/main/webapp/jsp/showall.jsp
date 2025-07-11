<%@ page language="java" contentType="text/html; charset=ISO-8859-1"
    pageEncoding="ISO-8859-1"%>

<%@ taglib prefix="c" uri="http://java.sun.com/jsp/jstl/core" %>

<%@ page import="java.util.ArrayList" %>
<%@ page import="app.model.Game" %>


<!DOCTYPE html>
<html>
<head>
<meta charset="ISO-8859-1">
<title>All datatable rows</title>
</head>
<body>

<table>
<tr>
	<th>ID</th>
	<th>Breed</th>
	<th>Weight</th>
	<th>Actions</th>
</tr>
<c:forEach var="game" items="${sessionScope.allgames }">
	<tr>
		<td>${game.id }</td>
		<td>${game.breed }</td>
		<td>${game.weight }</td>
		<td>
			<a href="/editgame?id=${game.id }">Edit</a>
		</td>
	</tr>
</c:forEach>
</table>

</body>
</html>