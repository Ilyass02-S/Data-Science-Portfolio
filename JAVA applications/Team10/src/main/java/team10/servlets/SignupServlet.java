package team10.servlets;

import javax.servlet.http.HttpServlet;

import java.io.IOException;
import java.io.PrintWriter;
import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.SQLException;

import javax.servlet.ServletException;
import javax.servlet.annotation.WebServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

@WebServlet(name = "Signup", urlPatterns = { "/signup" })
public class SignupServlet extends HttpServlet {
	private static final long serialVersionUID = 1L;

	public void doPost(HttpServletRequest request, HttpServletResponse response) throws IOException, ServletException {
		Connection conn;
		response.setContentType("text/html");
		response.setCharacterEncoding("UTF-8");
		PrintWriter out;
		out = response.getWriter();

		
		String Pwd = request.getParameter("password");
		String email = request.getParameter("email");
		String fullname = request.getParameter("fullname");
		String phone = request.getParameter("phone");
		String profession =request.getParameter("profession");

		try {

			Class.forName("com.mysql.cj.jdbc.Driver").newInstance();

			conn = java.sql.DriverManager.getConnection("jdbc:mysql://127.0.0.1:3306/evote", "yasser", "YasserHajji2002");

			String query = "INSERT INTO candidates(fullname,email,Pwd,phone,profession) " + "values(?,?,?,?,?);";
			PreparedStatement pstmt = conn.prepareStatement(query);
			pstmt.setString(1, fullname);
			pstmt.setString(2, email);
			pstmt.setString(3, Pwd);
			pstmt.setString(4, phone);
			pstmt.setString(5,profession);

			int x = pstmt.executeUpdate();

			if (x == 1) {
				response.sendRedirect("/loginaftersignup.jsp");
			}

		} catch (InstantiationException | IllegalAccessException | ClassNotFoundException | SQLException e) {
			e.printStackTrace();
		}
		out.close();

	}

	public static long getSerialversionuid() {
		return serialVersionUID;
	}

}