package it.uniroma2.informatica.magistrale.ir.imdbseries;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestParam;

@SpringBootApplication
@RestController
public class ImdbSeriesApplication {

	public static void main(String[] args) {
		SpringApplication.run(ImdbSeriesApplication.class, args);
	}

	@GetMapping("/hello")
	public String hello(@RequestParam(value = "name", defaultValue = "world") String name) {
		return String.format("<h1>Hello %s!</h1>", name);
	}

	@GetMapping("/")
	public String home() {
		return "<h1>Home Page</h1>";
	}
}
