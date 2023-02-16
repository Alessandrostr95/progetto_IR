package it.uniroma2.informatica.magistrale.ir.imdbseries;

public enum QueryParam {
    POSTER_LINK("Poster_Link"),
    TITLE("Series_Title"),
    GENRE("Genre"),
    IMDB_RATING("IMDB_Rating"),
    OVERVIEW("Overview"),
    ACTORS("Actors"),
    VOTES("No_of_Votes"),
    ID("docID"),
    FIELDS("fields"),
    OP("op"),
    VALUES("values"),
    BOOST("boost"),
    DEF_TYPE("defType"),
    EDISMAX("edismax");


    private String literalForm;
    QueryParam(String literalForm) {
        this.literalForm = literalForm;
    }

    public String toString() {
        return this.literalForm;
    }
}
