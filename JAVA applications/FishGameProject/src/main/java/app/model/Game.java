package app.model;

import java.io.Serializable;

public class Game implements Serializable{
	private int id;
	private String breed;
	private float weight;


	public int getId() {
		return id;
	}
	public void setId(int id) {
		this.id = id;
	}
	public String getBreed() {
		return breed;
	}
	public void setBreed(String breed) {
		this.breed = breed;
	}
	public float getWeight() {
		return weight;
	}
	public void setWeight(float weight) {
		this.weight = weight;
	}
	public void setWeight(String s) {
		try {
			this.weight=Float.parseFloat(s);
		}
		catch(NumberFormatException e) {
			this.weight=0;
		}
	}
	public String toString() {
		return id+" "+breed+" ("+weight+")";
	}
}
