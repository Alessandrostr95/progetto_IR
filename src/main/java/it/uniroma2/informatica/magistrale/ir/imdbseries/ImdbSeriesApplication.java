package it.uniroma2.informatica.magistrale.ir.imdbseries;

import org.apache.solr.client.solrj.SolrClient;
import org.apache.solr.client.solrj.SolrQuery;
import org.apache.solr.client.solrj.SolrServerException;
import org.apache.solr.client.solrj.impl.HttpSolrClient;
import org.apache.solr.client.solrj.response.QueryResponse;
import org.apache.solr.common.SolrDocument;
import org.apache.solr.common.SolrDocumentList;
import org.json.JSONException;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.client.RestTemplate;
import org.json.JSONObject;

import java.io.IOException;
import java.util.*;
import java.util.Map.Entry;

@SpringBootApplication
@RestController
public class ImdbSeriesApplication {

	static String SOLR_URL = "http://localhost:8983/solr";
	static String FLASK_URL = "http://localhost:5000/rf_score";
	static String SOLR_COLLECTION = "imdb_series";
	private final SolrClient solrClient = getClient();
	private final Map<Integer, Rating> rating = new HashMap<>();

	public static void main(String[] args) {
		SpringApplication.run(ImdbSeriesApplication.class, args);
	}

	/**
	 * Metodo di prova per i parametri della query
	 */
	@CrossOrigin(origins = "*")
	@GetMapping("/query")
	public String hello(
			@RequestParam(value = "desc", defaultValue = "") String desc,
			@RequestParam(value = "title", required = false) String title,
			@RequestParam(value = "genre") String[] genre) {
		JSONObject jsonObject = new JSONObject();
		try {
			jsonObject
					.put("title", title)
					.put("desc", desc)
					.put("genre", genre);
		} catch (JSONException e) {
			throw new RuntimeException(e);
		}

		return jsonObject.toString();
	}

	/**
	 * Given <b>multivalued</b> field values (as {@code List<String>}) and an operator (as {@code String})
	 * returns a concatenation of values separated by operator.<br><br>
	 *
	 * <b>Example</b>:
	 * <ul>
	 *     <li>
	 *         {@code values = ["Comedy", "Action"], operator = "AND"} will return the string {@code "(\"Comedy\" AND \"Action\")"}
	 *     </li>
	 *     <li>
	 *         {@code values = ["Comedy"], operator = "AND"} will return the string {@code "\"Comedy\""}
	 * 		</li>
	 * </ul>
	 *
	 * @param values
	 * @param operator
	 * @return {@code String}
	 */
	private String processMultivaluedField(ArrayList<String> values, String operator) {
		values.replaceAll(s -> {
			if (!(s.startsWith("\"") || s.endsWith("\""))) {
				return "\"" + s + "\"";
			}
			return s;
		});
		String values_field = String.join(" " + operator + " ", values);
		if (values.size() > 1) {
			values_field = "(" + values_field + ")";
		}
		return values_field;
	}

	/**
	 * Given a <b>map of query fields</b> it <b>process</b> a solr query string.
	 *
	 * @param fields
	 * @return {@code String}
	 */
	@SuppressWarnings("unchecked")
	private String buildQuery(Map<String, Object> fields) {
		if (fields == null) {
			return "*:*";
		}

		final String title = (String) fields.getOrDefault(QueryParam.TITLE.toString(), "*");
		final String overview = (String) fields.getOrDefault(QueryParam.OVERVIEW.toString(), "*");
		final Map<String, Object> genre = (Map<String, Object>) fields.getOrDefault(QueryParam.GENRE.toString(), null);
		final Map<String, Object> actors = (Map<String, Object>) fields.getOrDefault(QueryParam.ACTORS.toString(), null);

		String query = "";

		query += QueryParam.TITLE + ":" + (title == "*" ? title : "\"" + title + "\"");
		query += " " + QueryParam.OVERVIEW + ":" + (overview == "*" ? overview : "\"" + overview + "\"");

		if (genre != null) {
			ArrayList<String> genre_list = (ArrayList<String>) genre.get(QueryParam.VALUES.toString());
			if (genre_list.size() > 0) {
				final String genre_operator = (String) genre.getOrDefault(QueryParam.OP.toString(), "OR");
				query += " " + QueryParam.GENRE + ":" + processMultivaluedField(genre_list, genre_operator);
			}
		}

		if (actors != null) {
			ArrayList<String> actors_list = (ArrayList<String>) actors.get(QueryParam.VALUES.toString());
			if (actors_list.size() > 0) {
				final String actors_operator = (String) actors.getOrDefault(QueryParam.OP.toString(), "OR");
				query += " " + QueryParam.ACTORS + ":" + processMultivaluedField(actors_list, actors_operator);
			}
		}

		System.out.println(query);
		return query;
	}

	/**
	 * Main api that <b>build</b> and <b>submit</b> a query solr.
	 * @param payload
	 * @return
	 */
	@CrossOrigin(origins = "*")
	@PostMapping("/")
	@SuppressWarnings("unchecked")
	public List<SolrDocument> onQuery(@RequestBody Map<String, Object> payload) {
		final Map<String, Object> fields = (Map<String, Object>) payload.getOrDefault(QueryParam.FIELDS.toString(),
				null);

		final SolrQuery query = new SolrQuery();
		String query_string = buildQuery(fields);

		final Map<String, Object> boost = (Map<String, Object>) fields.getOrDefault(QueryParam.BOOST.toString(), null);
		if (boost != null) {
			query.setParam(QueryParam.DEF_TYPE.toString(), QueryParam.EDISMAX.toString());
			final boolean imdb_rating = (boolean) boost.getOrDefault(QueryParam.IMDB_RATING.toString(), true);
			final boolean no_of_votes = (boolean) boost.getOrDefault(QueryParam.VOTES.toString(), false);

			final ArrayList<String> bf = new ArrayList<String>();
			if (imdb_rating) {
				bf.add(QueryParam.IMDB_RATING.toString());
			}
			if (no_of_votes) {
				bf.add(QueryParam.VOTES.toString());
			}
			query.setParam("bf", String.join(" ", bf));

			// Add stars boost
			final boolean avgStars = (boolean) boost.getOrDefault(QueryParam.STARS.toString(), false);
			if (avgStars) {
				query_string += "docID:(";
				for (Entry<Integer, Rating> entry : this.rating.entrySet())
					query_string += entry.getKey() + "^" + entry.getValue().getAvgStars() + " ";
				query_string += ")";
			}
		}
		query.setQuery(query_string);
		query.setRows(Integer.MAX_VALUE);

		final QueryResponse response;
		try {
			response = solrClient.query(SOLR_COLLECTION, query);
		} catch (SolrServerException e) {
			// TODO: handle SolrServerException
			throw new RuntimeException(e);
		} catch (IOException e) {
			// TODO: handle IOException
			throw new RuntimeException(e);
		}

		final SolrDocumentList documents = response.getResults();
		final List<SolrDocument> result = new LinkedList<SolrDocument>();
		for (SolrDocument document : documents) {
			result.add(document);
		}

		return result;
	}

	/**
	 * Read old query and relevant and non relevants docID and returns a new ranking
	 * with rocchio algorithm.
	 * 
	 * @param payload json req
	 * @return new documents ranking
	 */
	@SuppressWarnings("unchecked")
	@CrossOrigin(origins = "*")
	@PostMapping("/rf")
	public List<SolrDocument> relevanceFeedback(@RequestBody Map<String, Object> payload) {
		System.out.println("New relevance feedback request:");
		System.out.println(payload);
		payload.put("k", 10); // By default, returns first k top score documents

		// Make new rf_score request to Flask 
		RestTemplate restTemplate = new RestTemplate();
		Map<String, Double> rfScore = restTemplate.postForObject(FLASK_URL, payload, HashMap.class);

		// Build new solr query with relevance feedback score
		final SolrQuery query = new SolrQuery();
		String query_string = buildQuery((Map<String, Object>) payload.get(QueryParam.FIELDS.toString()));

		// Adding score boost for query string
		query_string += " " + QueryParam.ID + ":(";
		for (Entry<String, Double> entry : rfScore.entrySet()) {
			query_string += entry.getKey() + "^" + (entry.getValue() * 10) + " ";
		}
		query_string += ")";

		query.setQuery(query_string);
		query.setRows(Integer.MAX_VALUE);

		final QueryResponse response;
		try {
			response = solrClient.query(SOLR_COLLECTION, query);
		} catch (SolrServerException e) {
			// TODO: handle SolrServerException
			throw new RuntimeException(e);
		} catch (IOException e) {
			// TODO: handle IOException
			throw new RuntimeException(e);
		}

		final SolrDocumentList documents = response.getResults();
		final List<SolrDocument> result = new LinkedList<SolrDocument>();
		for (SolrDocument document : documents) {
			result.add(document);
		}

		return result;
	}

	/**
	 * Read and update series rating
	 * 
	 * @param payload json req
	 * @return json res
	 */
	@CrossOrigin(origins = "*")
	@GetMapping("/rating")
	public Map<String, Object> updateRating(
			@RequestParam(value = "docID", defaultValue = "") int docID,
			@RequestParam(value = "stars", required = true) int stars) {
		final Map<String, Object> res = new HashMap<>();
		System.out.println("New rating request: \ndocID: " + docID + "\nstars:" + stars);
		this.rating.putIfAbsent(docID, new Rating());
		this.rating.get(docID).addRating(stars);
		res.put("status", 200);
		res.put(QueryParam.ID.toString(), docID);
		res.put(QueryParam.STARS.toString(), this.rating.get(docID).getAvgStars());
		return res;
	}

	/**
	 * Get average stars of a serie keyed by docID
	 * @param docID of the serie
	 * @return <docID, avgStars> couple
	 */
	@CrossOrigin(origins = "*")
	@GetMapping("/docID/{docID}/stars")
	public Map<Integer, Double> getAvgStars(@PathVariable int docID){
		return Collections.singletonMap(docID, this.rating.get(docID) != null ? this.rating.get(docID).getAvgStars() : 0);
	}

	private SolrClient getClient() {
		return new HttpSolrClient.Builder(SOLR_URL)
				.withConnectionTimeout(10000)
				.withSocketTimeout(60000)
				.build();
	}
}
