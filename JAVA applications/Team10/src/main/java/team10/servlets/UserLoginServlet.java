package team10.servlets;

import java.io.*;
import java.sql.SQLException;
 
import javax.servlet.*;
import javax.servlet.annotation.WebServlet;
import javax.servlet.http.*;
 
@WebServlet("/login")
public class UserLoginServlet extends HttpServlet {
    private static final long serialVersionUID = 1L;
 
    public UserLoginServlet() {
        super();
    }
 
    protected void doPost(HttpServletRequest request, HttpServletResponse response)
            throws ServletException, IOException {
        String email = request.getParameter("email");
        String password = request.getParameter("password");
         
        try {
            boolean userExists = CheckDao.checkLogin(email, password);
             
            if (userExists) {
                HttpSession session = request.getSession();
                session.setAttribute("email", email);
                response.sendRedirect("homepage.jsp");
            } else {
            	response.sendRedirect("signup.jsp");
            }
             
        } catch (SQLException | ClassNotFoundException ex) {
            throw new ServletException(ex);
        }
    }
}