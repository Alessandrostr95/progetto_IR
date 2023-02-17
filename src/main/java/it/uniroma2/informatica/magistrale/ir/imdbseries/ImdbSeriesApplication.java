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

import org.json.JSONObject;

import java.io.IOException;
import java.util.*;


@SpringBootApplication
@RestController
public class ImdbSeriesApplication {

	static String SOLR_URL = "http://localhost:8983/solr";
	static String SOLR_COLLECTION = "imdb_series";

	public static void main(String[] args) {
		SpringApplication.run(ImdbSeriesApplication.class, args);
	}

	/**
	 * Metodo di prova per i parametri della query
	 * */
	@CrossOrigin(origins = "*")
	@GetMapping("/query")
	public String hello(
			@RequestParam(value = "desc", defaultValue = "") String desc,
			@RequestParam(value = "title", required = false) String title,
			@RequestParam(value = "genre") String[] genre
		) {
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
		return  values_field;
	}

	private String buildQuery(Map<String, Object> fields) {
		if (fields == null) {
			return "*:*";
		}

		final String title = (String) fields.getOrDefault(QueryParam.TITLE.toString(), "*");
		final String overview = (String) fields.getOrDefault(QueryParam.OVERVIEW.toString(), "*");
		final Map<String, Object> genre = (Map<String, Object>) fields.getOrDefault(QueryParam.GENRE.toString(), null);
		final Map<String, Object> actors = (Map<String, Object>) fields.getOrDefault(QueryParam.ACTORS.toString(), null);

		String query = "";

		query += QueryParam.TITLE + ":" + (title == "*" ? title : "\"" +  title + "\"");
		query += " " + QueryParam.OVERVIEW + ":" + (overview == "*" ? overview : "\"" +  overview + "\"");

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

		// TODO: indagare perché lo stampa due volte (i.e. perché la funzione viene chiamata due volte).
		System.out.println(query);
		return query;
	}

	@CrossOrigin(origins = "*")
	@PostMapping("/")
	public List<SolrDocument> onQuery(@RequestBody Map<String, Object> payload) {
		final Map<String, Object> fields = (Map<String, Object> ) payload.getOrDefault(QueryParam.FIELDS.toString(), null);

		final SolrClient solrClient = getClient();

		final SolrQuery query = new SolrQuery();
		final String query_string = buildQuery(fields);
		query.setQuery(query_string);
		query.setRows(Integer.MAX_VALUE);

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
		}

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

	private SolrClient getClient() {
		return new HttpSolrClient.Builder(SOLR_URL)
				.withConnectionTimeout(10000)
				.withSocketTimeout(60000)
				.build();
	}
}
