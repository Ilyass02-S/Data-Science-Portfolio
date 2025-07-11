package team10;

import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;

public class UserDao {
	
	public static User getUser(String email) throws ClassNotFoundException, SQLException {
		String jdbcURL = "jdbc:mysql://localhost:3306/evote";
		String dbUser = "yasser";
		String dbPassword = "YasserHajji2002";

		Class.forName("com.mysql.jdbc.Driver");
		Connection connection = DriverManager.getConnection(jdbcURL, dbUser, dbPassword);
		String sql = "SELECT * FROM candidates WHERE email = ?";
		PreparedStatement statement = connection.prepareStatement(sql);
		statement.setString(1, email);

		ResultSet result = statement.executeQuery();
		
		result.next();
		
		User user = new User();
		user.setEmail(result.getString("email"));
		user.setPassword(result.getString("Pwd"));
		user.setphone(result.getString("phone"));
		user.setprofession(result.getString("profession"));
		user.setFullname(result.getString("fullname"));
		
		return user;
	}
	
}