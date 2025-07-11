package app;

import java.io.IOException;
import java.io.PrintWriter;

import javax.servlet.annotation.WebServlet;
import javax.servlet.http.Cookie;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import javax.servlet.http.HttpSession;

@WebServlet(
	    name = "ReadCookieServlet",
	    urlPatterns = {"/read"}
	)
public class ReadCookieServlet extends HttpServlet {
	@Override
	  public void doGet(HttpServletRequest request, HttpServletResponse response) 
	      throws IOException {
		
		Cookie[] cookies = request.getCookies();

	    response.setContentType("text/html");
	    response.setCharacterEncoding("UTF-8");
	    PrintWriter out = response.getWriter();

	    out.println("<p>");
	    
	    if ( cookies != null ) {
	    	for (int i = 0; i < cookies.length; i++) {
	    		String name = cookies[i].getName();
	    		String value = cookies[i].getValue();

	    		out.println("name: " + name + "; value: " + value);
	    	}
	    } else {
	    	out.println("no cookies");
	    }
	    
	    
	    out.println("</p>");	 
	    
	    
	    HttpSession session = request.getSession(false);
	    
	    if ( session != null && session.getAttribute("mysessiondata") != null ) {
	    	out.println("<p>value from session: " + session.getAttribute("mysessiondata").toString() + "</p>");
	    }	    
	    
	    out.close();

	  }
}
