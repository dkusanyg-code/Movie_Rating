"""Movie Rater: a Drafter website for rating movies by category.

The user scores a movie from 1 to 10 in six categories. The site averages
the scores, gives a verdict, and keeps a list of every movie rated.
"""
from drafter import *
from bakery import assert_equal
from dataclasses import dataclass

set_website_title("Movie Rater")
set_site_information(
    author="Drew Keefe",
    description="Rate movies by story, acting, visuals, sound, pacing, "
                "and enjoyment, then keep a list of what is worth watching.",
    sources=["LLM helped write this code"],
    planning=[],  # Copy of CS1 Final Project 0_ Pick a Problem.pdf, Copy of CS1 Final Project 1_ Design.pdf
        links=[]      # TODO: add your GitHub repository link here
)

# Global constants (allowed by the project rules)
GENRES = ["Action", "Comedy", "Drama", "Horror", "Sci-Fi", "Romance", "Other"]
SCORES = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10"]
CATEGORY_NAMES = ["Story", "Acting", "Visuals", "Sound", "Pacing",
                  "Enjoyment"]


#Dataclasses
@dataclass
class Movie:
    """A single rated movie with its six category scores."""
    title: str
    genre: str
    overall_rating: float
    verdict: str
    story: int
    acting: int
    visuals: int
    sound: int
    pacing: int
    enjoyment: int


@dataclass
class State:
    """Everything the site remembers between pages."""
    movies: list[Movie]
    filter_genre: str
    average_rating: float
    top_movie: str


# ---------- Helper functions ----------
def get_verdict(rating: float) -> str:
    """Return a short message for an overall rating out of 10."""
    if rating >= 8:
        return "Must Watch"
    elif rating >= 6:
        return "Decent"
    else:
        return "Skip It"


def calculate_overall(scores: list[int]) -> float:
    """Average a list of scores, rounded to one decimal place."""
    return round(sum(scores) / len(scores), 1)


def calculate_average(movies: list[Movie]) -> float:
    """Return the average overall rating of all movies (0.0 if none)."""
    if len(movies) == 0:
        return 0.0
    total = 0.0
    for movie in movies:
        total = total + movie.overall_rating
    return round(total / len(movies), 1)


def find_top_title(movies: list[Movie]) -> str:
    """Return the title of the highest-rated movie ('None yet' if empty)."""
    if len(movies) == 0:
        return "None yet"
    best = movies[0]
    for movie in movies:
        if movie.overall_rating > best.overall_rating:
            best = movie
    return best.title


def movie_matches_filter(movie: Movie, genre: str) -> bool:
    """Return True if the movie should be shown for the chosen genre."""
    if genre == "All":
        return True
    return movie.genre == genre


def get_scores(movie: Movie) -> list[int]:
    """Return a movie's six scores in the same order as CATEGORY_NAMES."""
    return [movie.story, movie.acting, movie.visuals,
            movie.sound, movie.pacing, movie.enjoyment]


def find_best_index(scores: list[int]) -> int:
    """Return the position of the highest score in the list."""
    best_index = 0
    for i in range(len(scores)):
        if scores[i] > scores[best_index]:
            best_index = i
    return best_index


def find_worst_index(scores: list[int]) -> int:
    """Return the position of the lowest score in the list."""
    worst_index = 0
    for i in range(len(scores)):
        if scores[i] < scores[worst_index]:
            worst_index = i
    return worst_index


def build_score_lines(movie: Movie) -> list[str]:
    """Return one text line per category, like 'Story: 7/10'."""
    scores = get_scores(movie)
    lines = []
    for i in range(len(scores)):
        lines.append(f"{CATEGORY_NAMES[i]}: {scores[i]}/10")
    return lines


def build_movie_rows(state: State) -> list[str]:
    """Return a text line for each movie that matches the genre filter."""
    rows = []
    for movie in state.movies:
        if movie_matches_filter(movie, state.filter_genre):
            rows.append(f"{movie.title} ({movie.genre}) - "
                        f"{movie.overall_rating}/10 - {movie.verdict}")
    return rows


def get_visible_titles(state: State) -> list[str]:
    """Return the titles of movies that match the genre filter."""
    titles = []
    for movie in state.movies:
        if movie_matches_filter(movie, state.filter_genre):
            titles.append(movie.title)
    return titles


# Routes
@route
def index(state: State) -> Page:
    """Start page: Drafter always begins on 'index', so show home."""
    return home(state)


@route
def home(state: State) -> Page:
    """Home page with buttons to the main parts of the site."""
    return Page(state, [
        Header("Movie Rater"),
        "Rate movies by category and keep a list of what's worth watching.",
        LineBreak(),
        Button("Rate a Movie", rate_movie),
        Button("View Rated Movies", movie_list),
        Button("View Stats", stats),
    ])


@route
def rate_movie(state: State) -> Page:
    """Form page where the user enters a title, genre, and six scores."""
    return Page(state, [
        Header("Rate a Movie"),
        "Movie title:",
        TextBox("title", ""),
        "Genre:",
        SelectBox("genre", GENRES, "Action"),
        "Score each category from 1 (awful) to 10 (masterpiece). "
        "5 = average.",
        LineBreak(),
        "Story:",
        SelectBox("story", SCORES, "5"),
        "Acting:",
        SelectBox("acting", SCORES, "5"),
        "Visuals:",
        SelectBox("visuals", SCORES, "5"),
        "Sound:",
        SelectBox("sound", SCORES, "5"),
        "Pacing:",
        SelectBox("pacing", SCORES, "5"),
        "Enjoyment:",
        SelectBox("enjoyment", SCORES, "5"),
        LineBreak(),
        Button("Submit", submit_rating),
        Button("Back Home", home),
    ])


@route
def submit_rating(state: State, title: str, genre: str, story: str,
                  acting: str, visuals: str, sound: str, pacing: str,
                  enjoyment: str) -> Page:
    """Save the new movie, update the stats, and show the result page."""
    if title.strip() == "":
        return Page(state, [
            Header("Oops!"),
            "Please enter a movie title.",
            Button("Back to Rating Form", rate_movie),
        ])

    # SelectBox answers are text, so turn them into integers
    scores = [int(story), int(acting), int(visuals),
              int(sound), int(pacing), int(enjoyment)]
    overall = calculate_overall(scores)

    new_movie = Movie(title.strip(), genre, overall, get_verdict(overall),
                      scores[0], scores[1], scores[2],
                      scores[3], scores[4], scores[5])
    state.movies.append(new_movie)
    state.average_rating = calculate_average(state.movies)
    state.top_movie = find_top_title(state.movies)
    return result(state)


@route
def result(state: State) -> Page:
    """Show the overall rating, verdict, and scores of the latest movie."""
    movie = state.movies[-1]
    scores = get_scores(movie)
    best = find_best_index(scores)
    worst = find_worst_index(scores)

    content = [
        Header("Result"),
        f"{movie.title} ({movie.genre})",
        f"Overall rating: {movie.overall_rating} / 10",
        f"Verdict: {movie.verdict}",
        LineBreak(),
    ]
    content = content + build_score_lines(movie)
    content.append(LineBreak())
    content.append(f"Biggest Strength: {CATEGORY_NAMES[best]} "
                   f"({scores[best]}/10)")
    content.append(f"Main Weakness: {CATEGORY_NAMES[worst]} "
                   f"({scores[worst]}/10)")
    content.append(LineBreak())
    content.append(Button("Back Home", home))
    return Page(state, content)


@route
def movie_list(state: State) -> Page:
    """Show every movie that matches the genre filter, with delete option."""
    content = [
        Header("Rated Movies"),
        "Filter by genre:",
        SelectBox("filter_genre", ["All"] + GENRES, state.filter_genre),
        Button("Apply Filter", set_filter),
        LineBreak(),
    ]

    rows = build_movie_rows(state)
    titles = get_visible_titles(state)
    if len(rows) == 0:
        content.append("No movies to show.")
    else:
        content = content + rows
        content.append(LineBreak())
        content.append("Delete a movie:")
        content.append(SelectBox("title", titles, titles[0]))
        content.append(Button("Delete Movie", delete_movie))

    content.append(LineBreak())
    content.append(Button("Back Home", home))
    return Page(state, content)


@route
def set_filter(state: State, filter_genre: str) -> Page:
    """Save the chosen genre filter and show the movie list again."""
    state.filter_genre = filter_genre
    return movie_list(state)


@route
def delete_movie(state: State, title: str) -> Page:
    """Delete the first movie with this title and update the stats."""
    for movie in state.movies:
        if movie.title == title:
            state.movies.remove(movie)
            break
    state.average_rating = calculate_average(state.movies)
    state.top_movie = find_top_title(state.movies)
    return movie_list(state)


@route
def stats(state: State) -> Page:
    """Show total movies, average rating, and the top-rated movie."""
    return Page(state, [
        Header("Stats"),
        f"Total movies rated: {len(state.movies)}",
        f"Average rating: {state.average_rating} / 10",
        f"Top-rated movie: {state.top_movie}",
        LineBreak(),
        Button("Back Home", home),
    ])


# Unit tests 
def make_state() -> State:
    """Return a fresh, empty State for testing."""
    return State([], "All", 0.0, "None yet")


def make_movie(title: str, genre: str, rating: float) -> Movie:
    """Return a Movie with every score set to 5, for testing."""
    return Movie(title, genre, rating, get_verdict(rating),
                 5, 5, 5, 5, 5, 5)


def test_helpers() -> None:
    """Test the helper functions."""
    assert_equal(get_verdict(9.0), "Must Watch")
    assert_equal(get_verdict(7.0), "Decent")
    assert_equal(get_verdict(3.0), "Skip It")
    assert_equal(calculate_overall([10, 10, 10, 10, 10, 10]), 10.0)
    assert_equal(calculate_overall([1, 2, 3, 4, 5, 6]), 3.5)
    assert_equal(calculate_average([]), 0.0)
    two_movies = [make_movie("A", "Action", 10.0),
                  make_movie("B", "Drama", 5.0)]
    assert_equal(calculate_average(two_movies), 7.5)
    assert_equal(find_top_title([]), "None yet")
    assert_equal(find_top_title(two_movies), "A")
    assert_equal(movie_matches_filter(two_movies[0], "All"), True)
    assert_equal(movie_matches_filter(two_movies[0], "Action"), True)
    assert_equal(movie_matches_filter(two_movies[0], "Drama"), False)
    assert_equal(find_best_index([3, 9, 1, 4, 4, 4]), 1)
    assert_equal(find_worst_index([3, 9, 1, 4, 4, 4]), 2)
    assert_equal(build_score_lines(two_movies[0])[0], "Story: 5/10")


def test_routes() -> None:
    """Test each route (checks the state or that a Page comes back)."""
    state = make_state()
    assert_equal(isinstance(index(state), Page), True)
    assert_equal(isinstance(home(state), Page), True)
    assert_equal(isinstance(rate_movie(state), Page), True)
    assert_equal(isinstance(stats(state), Page), True)
    assert_equal(isinstance(movie_list(state), Page), True)

    # submit_rating with an empty title should not add a movie
    submit_rating(state, "  ", "Action", "5", "5", "5", "5", "5", "5")
    assert_equal(len(state.movies), 0)

    # submit_rating with a real title adds a movie and updates stats
    page = submit_rating(state, "Dune", "Sci-Fi",
                         "10", "10", "10", "10", "10", "10")
    assert_equal(isinstance(page, Page), True)
    assert_equal(len(state.movies), 1)
    assert_equal(state.movies[0].verdict, "Must Watch")
    assert_equal(state.average_rating, 10.0)
    assert_equal(state.top_movie, "Dune")

    # result shows the latest movie
    assert_equal(isinstance(result(state), Page), True)

    # set_filter changes the filter
    set_filter(state, "Comedy")
    assert_equal(state.filter_genre, "Comedy")

    # delete_movie removes the movie and resets the stats
    delete_movie(state, "Dune")
    assert_equal(len(state.movies), 0)
    assert_equal(state.average_rating, 0.0)
    assert_equal(state.top_movie, "None yet")


def run_tests() -> None:
    """Run all unit tests."""
    test_helpers()
    test_routes()


run_tests()

#Start the site
start_server(State([], "All", 0.0, "None yet"))

