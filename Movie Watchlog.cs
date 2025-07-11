using System;
using System.Collections.Generic;
using System.IO;

class Movie
{
    public string Name { get; set; }
    public int Length { get; set; }
    public int Year { get; set; }

    public Movie(string name, int length, int year)
    {
        Name = name;
        Length = length;
        Year = year;
    }
}

class MovieWatchLogApp
{
    private List<Movie> watchLog = new List<Movie>();

    public void ShowMenu()
    {
        Console.WriteLine("Movie Watch Log");
        Console.WriteLine("===============");
        Console.WriteLine("1) Add a Movie");
        Console.WriteLine("2) Delete a Movie");
        Console.WriteLine("3) Show Report");
        Console.WriteLine("4) Load Database");
        Console.WriteLine("5) Save Database");
        Console.WriteLine("6) Quit");
    }

    public void Run()
    {
        while (true)
        {
            ShowMenu();
            string input = Console.ReadLine();

            switch (input)
            {
                case "1":
                    AddMovie();
                    break;
                case "2":
                    DeleteMovie();
                    break;
                case "3":
                    ShowReport();
                    break;
                case "4":
                    LoadDatabase();
                    break;
                case "5":
                    SaveDatabase();
                    break;
                case "6":
                    Console.WriteLine("Exiting Movie Watch Log. Goodbye!");
                    return;
                default:
                    Console.WriteLine("Unknown command. Please enter a valid option (1-6).");
                    break;
            }
        }
    }

    private void AddMovie()
    {
        Console.WriteLine("Enter the movie details:");
        Console.Write("Name: ");
        string name = Console.ReadLine();
        Console.Write("Length (in minutes): ");
        int length=Convert.ToInt32 (Console.ReadLine());
        Console.Write("Year: ");
        int year=Convert.ToInt32 (Console.ReadLine());
        Movie movie = new Movie(name, length, year);
        watchLog.Add(movie);
        Console.WriteLine("Movie added to the watch log.");
    }

    private void DeleteMovie()
    {
        Console.WriteLine("Enter the name of the movie to delete:");
        string name = Console.ReadLine();
        Movie movieToRemove = watchLog.Find(m => m.Name.Equals(name, StringComparison.OrdinalIgnoreCase));

        if (movieToRemove != null)
        {
            watchLog.Remove(movieToRemove);
            Console.WriteLine("Movie deleted from the watch log.");
        }
    }

    private void ShowReport()
    {
        Console.WriteLine("Movie Watch Log Report:");
        foreach (var movie in watchLog)
        {
            Console.WriteLine("Name:"+movie.Name+", Length:"+movie.Length+" min, Year: "+movie.Year);
        }
    }

    private void LoadDatabase()
    {
        Console.WriteLine("Enter the name of the database file to load:");
        string fileName = Console.ReadLine();
        if (File.Exists(fileName))
        {
            watchLog.Clear();
            string[] lines = File.ReadAllLines(fileName);
            foreach (string line in lines)
            {
                string[] parts = line.Split(',');
                if (parts.Length == 3 && int.TryParse(parts[1], out int length) && int.TryParse(parts[2], out int year))
                {
                    Movie movie = new Movie(parts[0], length, year);
                    watchLog.Add(movie);
                }
            }
            Console.WriteLine("Database loaded successfully.");
        }
    }

    private void SaveDatabase()
    {
        Console.WriteLine("Enter the name of the database file to save:");
        string fileName = Console.ReadLine();
            using (StreamWriter writer = new StreamWriter(fileName))
            {
                foreach (var movie in watchLog)
                {
                    writer.WriteLine($"{movie.Name},{movie.Length},{movie.Year}");
                }
            }
            Console.WriteLine("Database saved successfully.");
    }
}

class Program
{
    static void Main()
    {
        MovieWatchLogApp app = new MovieWatchLogApp();
        app.Run();
    }
}