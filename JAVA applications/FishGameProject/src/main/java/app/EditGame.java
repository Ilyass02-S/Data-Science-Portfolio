package app;

import java.io.IOException;
import java.io.PrintWriter;
import java.util.ArrayList;

import javax.servlet.RequestDispatcher;
import javax.servlet.ServletException;
import javax.servlet.annotation.WebServlet;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import javax.servlet.http.HttpSession;

import app.dao.Dao;
import app.model.Game;

@WebServlet(
		name = "EditGame",
		urlPatterns = {"/editgame"}
		)
public class EditGame extends HttpServlet {
	
	@Override
	public void doGet(HttpServletRequest request, HttpServletResponse response) 
			throws IOException, ServletException {
		
		
		// if sessions does not exist, create new one
		HttpSession session = request.getSession();
		
		String idValue = request.getParameter("id");
		
		if ( idValue != null ) {
			try {
				int id = Integer.parseInt(idValue);
				
				Dao dao = new Dao();
				Game game = dao.getGameInfo(id);
				
				session.setAttribute("game", game);
				
				RequestDispatcher rd = request.getRequestDispatcher("jsp/editform.jsp");
				rd.forward(request, response);
				
			} catch (Exception e) {
				e.printStackTrace();
			}
		} else {
			// Back to list
			response.sendRedirect("/showdata");
			
		}
	
	}
	
	@Override
	public void doPost(HttpServletRequest request, HttpServletResponse response) 
			throws IOException, ServletException {
	
		
		// Create connection
		Dao dao=new Dao();
		Game game = readGame(request);
		
		dao.updateGame(game);
		
		dao.close();
		
		// Back to list after actions
		//RequestDispatcher rd = request.getRequestDispatcher("/showdata");
		//rd.forward(request, response);
		response.sendRedirect("/showdata");
	}
	
	private Game readGame(HttpServletRequest request) {
		// TODO Auto-generated method stub
		Game game=new Game();
		game.setBreed(request.getParameter("breed"));
		game.setWeight(request.getParameter("weight"));
		game.setId(Integer.parseInt(request.getParameter("id")));
		return game;
	}
}
