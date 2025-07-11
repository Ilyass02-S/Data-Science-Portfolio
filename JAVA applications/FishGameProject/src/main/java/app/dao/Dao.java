package app.dao;

import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.Statement;
import java.util.ArrayList;

import app.model.Game;

public class Dao {

	private Connection conn;

	// When new instance is created, also DB-connection is created
	public Dao() {
		try {
			Class.forName("com.mysql.jdbc.Driver").newInstance();
			conn=java.sql.DriverManager.getConnection("jdbc:mysql://localhost:3306/gamedb", "appuser", "kukkuu");
		} catch (SQLException | InstantiationException | IllegalAccessException | ClassNotFoundException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
	}

	// Manually close DB-connection for releasing resource
	public void close() {
		try {
			conn.close();
		} catch (SQLException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
	}

	public int saveGame(Game game) {
		Statement stmt=null;
		int count=0;
		try {
			stmt = conn.createStatement();
			count=stmt.executeUpdate("insert into gametable(breed, weight) values('"+game.getBreed()+"', "+game.getWeight()+")");
		} catch (SQLException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
		return count;
	}
	
	public ArrayList<Game> readAllGame() {
		ArrayList<Game> list=new ArrayList<>();
		Statement stmt=null;
		int count=0;
		try {
			stmt = conn.createStatement();
			ResultSet rs=stmt.executeQuery("select * from gametable");
			while (rs.next()) {
				Game game=new Game();
				game.setId(rs.getInt("id"));
				game.setBreed(rs.getString("breed"));
				game.setWeight(rs.getFloat("weight"));
				list.add(game);
			}
		} catch (SQLException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
		return list;
	}
	
	public int updateGame(Game game) {
		int count = 0;
		String sql = "update gametable set breed = ?, weight = ? where id = ?";
		try {
			PreparedStatement stmt = conn.prepareStatement(sql);
			
			stmt.setString(1, game.getBreed());
			stmt.setFloat(2, game.getWeight());
			
			stmt.setInt(3, game.getId());
			
			count = stmt.executeUpdate();
		} catch (SQLException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
		return count;
	}
	
	public Game getGameInfo(int id) {
		Game result = null;
		String sql = "select * from gametable where id = ?";
		try {
			PreparedStatement stmt = conn.prepareStatement(sql);
						
			stmt.setInt(1, id);
			
			ResultSet resultset = stmt.executeQuery();
			
			if (resultset.next()) {
				result = new Game();
				result.setId(resultset.getInt("id"));
				result.setBreed(resultset.getString("breed"));
				result.setWeight(resultset.getFloat("weight"));
			}
		} catch (SQLException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
		return result;
	}
}
