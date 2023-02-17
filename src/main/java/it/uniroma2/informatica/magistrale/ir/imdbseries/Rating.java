package it.uniroma2.informatica.magistrale.ir.imdbseries;

/**
 * Classe che gestisce il rating di un docID
 */
public class Rating {
    // Rating
    private double avgStars;
    // No of votes
    private int n;

    public Rating() {
        this.avgStars = 0;
        this.n = 0;
    }

    public double getAvgStars(){
        return this.avgStars;
    }

    /**
     * Aggiunge una nuova valutazione
     * 
     * @param stars valutazione
     * @return nuovo rating
     */
    public double addRating(double stars) {
        this.avgStars = (this.avgStars * this.n + stars) / ++this.n;
        return this.avgStars;
    }
}
