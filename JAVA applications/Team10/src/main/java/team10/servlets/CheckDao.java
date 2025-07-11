package team10.servlets;

import java.sql.*;

// DAO = data access object
public class CheckDao {

	public static boolean checkLogin(String email, String password) throws SQLException, ClassNotFoundException {
		String jdbcURL = "jdbc:mysql://localhost:3306/evote";
		String dbUser = "yasser";
		String dbPassword = "YasserHajji2002";
		
		System.out.println(email);
		System.out.println(password);

		Class.forName("com.mysql.jdbc.Driver");
		Connection connection = DriverManager.getConnection(jdbcURL, dbUser, dbPassword);
		String sql = "SELECT * FROM candidates WHERE email = ? and Pwd = ?";
		PreparedStatement statement = connection.prepareStatement(sql);
		statement.setString(1, email);
		statement.setString(2, password);

		ResultSet result = statement.executeQuery();
		
		boolean found = result.next();
		
		System.out.println(result.getString(2));
		
		return found;
	}
}