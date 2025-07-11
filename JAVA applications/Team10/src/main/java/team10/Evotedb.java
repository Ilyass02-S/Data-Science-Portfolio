package team10;

import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.util.ArrayList;
import java.util.List;


public class Evotedb {

		
	public static Connection getConnection()  {
	    Connection conn = null;  
	    
	    
	    try {

			Class.forName("com.mysql.jdbc.Driver");
			
			
			conn=java.sql.DriverManager.getConnection("jdbc:mysql://localhost:3306/evote", "yasser", "YasserHajji2002");

		} catch (ClassNotFoundException | SQLException zab) {
			zab.printStackTrace();
		}  
	    return conn;
	    
		
		
		
	}
	
	public static List<User> getUser() {
	    List<User> list= new ArrayList<User>();

		String query="SELECT * FROM candidates ";
		Connection conn=Evotedb.getConnection();

		PreparedStatement statement;
		try {

			statement = conn.prepareStatement(query);
		    ResultSet result;
			result=statement.executeQuery(query);



		    while(result.next()) {
		    	
		    	User U =new User();

		    	
		    	U.setFullname(result.getString(1));
		    	U.setPassword(result.getString(3));
		    	U.setEmail(result.getString(2));
		
		        list.add(U);

		    }

			conn.close();

		} catch (SQLException zab) {
			zab.printStackTrace();
		}

			return list;
	}
	


}
