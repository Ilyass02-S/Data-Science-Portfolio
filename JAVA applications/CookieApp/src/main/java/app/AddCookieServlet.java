package app;

import java.io.IOException;
import java.io.PrintWriter;
import java.net.URLEncoder;

import javax.servlet.annotation.WebServlet;
import javax.servlet.http.Cookie;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import javax.servlet.http.HttpSession;

@WebServlet(
	    name = "AddCookieServlet",
	    urlPatterns = {"/add"}
	)
public class AddCookieServlet extends HttpServlet {
	@Override
	  public void doGet(HttpServletRequest request, HttpServletResponse response) 
	      throws IOException {
		String data = "mydata";
		Cookie cookie = new Cookie("MyCookie", data);
		
		HttpSession session = request.getSession();
		session.setAttribute("mysessiondata", "mydata");
			
		response.addCookie(cookie);
	    response.setContentType("text/html");
	    response.setCharacterEncoding("UTF-8");
	    PrintWriter out = response.getWriter();

	    out.print("<p>Cookie is set to " + data + "</p>");
	    
	    /*
	    out.println("<a href=\"" + response.encodeURL("./read?param1=" + URLEncoder.encode("value", "UTF-8")
	    	+ "&param2=" + URLEncoder.encode("value", "UTF-8")
	    	+ "&jsessionid=" + URLEncoder.encode(session.getId(), "UTF-8")
	    		) 
	    
	    + "\">Read Page</a>");
	    */
	    out.close();
	  }
}
