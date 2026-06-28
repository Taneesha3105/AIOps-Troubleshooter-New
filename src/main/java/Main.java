import static spark.Spark.*;

public class Main {

    public static void main(String[] args) {

        String portStr = System.getenv("PORT");
        port(portStr == null ? 8080 : Integer.parseInt(portStr));

        get("/", (req, res) -> "AIOps Troubleshooter Running");

        get("/add", (req, res) -> {
            int a = Integer.parseInt(req.queryParams("a"));
            int b = Integer.parseInt(req.queryParams("b"));
            return String.valueOf(a + b)
        });
    }
}
