package com.helios.billing;

import com.sun.net.httpserver.HttpExchange;
import com.sun.net.httpserver.HttpServer;

import java.io.IOException;
import java.io.OutputStream;
import java.net.InetSocketAddress;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;

/**
 * The Helios Billing service.
 *
 * <p>Two endpoints, no framework, no dependencies. Start it with:
 * <pre>
 *   mvn -q compile exec:java   (or)   java -jar target/billing-1.0.0.jar
 * </pre>
 *
 * <p>OrderCore calls POST /invoice. If this service is not running, OrderCore falls back
 * to a local calculation and marks the result, so the Shop UI keeps working.
 */
public final class BillingServer {

    public static final int DEFAULT_PORT = 8081;

    private final HttpServer server;

    public BillingServer(int port) throws IOException {
        this.server = HttpServer.create(new InetSocketAddress(port), 0);
        this.server.createContext("/health", this::handleHealth);
        this.server.createContext("/invoice", this::handleInvoice);
        this.server.setExecutor(null);
    }

    public void start() {
        server.start();
    }

    public void stop() {
        server.stop(0);
    }

    public int port() {
        return server.getAddress().getPort();
    }

    private void handleHealth(HttpExchange exchange) throws IOException {
        if (!"GET".equals(exchange.getRequestMethod())) {
            respond(exchange, 405, "{\"error\":\"method not allowed\"}");
            return;
        }
        respond(exchange, 200, "{\"status\":\"ok\",\"service\":\"billing\"}");
    }

    private void handleInvoice(HttpExchange exchange) throws IOException {
        if (!"POST".equals(exchange.getRequestMethod())) {
            respond(exchange, 405, "{\"error\":\"method not allowed\"}");
            return;
        }
        String body = new String(exchange.getRequestBody().readAllBytes(), StandardCharsets.UTF_8);
        try {
            respond(exchange, 200, invoiceFromRequest(body).toJson());
        } catch (IllegalArgumentException exc) {
            respond(exchange, 400, "{\"error\":\"" + Json.escape(String.valueOf(exc.getMessage())) + "\"}");
        } catch (RuntimeException exc) {
            respond(exchange, 500, "{\"error\":\"internal error\"}");
        }
    }

    /** Package private so tests can exercise the contract without opening a socket. */
    static InvoiceCalculator.Invoice invoiceFromRequest(String body) {
        Map<String, Object> request = Json.parseObject(body);
        String orderId = Json.requireString(request, "orderId");
        String currency = request.containsKey("currency")
                ? Json.requireString(request, "currency")
                : "GBP";

        Object rawLines = request.get("lines");
        if (!(rawLines instanceof List) || ((List<?>) rawLines).isEmpty()) {
            throw new IllegalArgumentException("lines must be a non-empty array");
        }
        List<InvoiceCalculator.Line> lines = new ArrayList<>();
        for (Object item : (List<?>) rawLines) {
            if (!(item instanceof Map)) {
                throw new IllegalArgumentException("each line must be an object");
            }
            @SuppressWarnings("unchecked")
            Map<String, Object> lineMap = (Map<String, Object>) item;
            lines.add(InvoiceCalculator.Line.fromMap(lineMap));
        }
        return InvoiceCalculator.calculate(orderId, currency, lines);
    }

    private void respond(HttpExchange exchange, int status, String json) throws IOException {
        byte[] payload = json.getBytes(StandardCharsets.UTF_8);
        exchange.getResponseHeaders().add("Content-Type", "application/json");
        exchange.sendResponseHeaders(status, payload.length);
        try (OutputStream out = exchange.getResponseBody()) {
            out.write(payload);
        }
    }

    public static void main(String[] args) throws IOException {
        int port = DEFAULT_PORT;
        if (args.length > 0) {
            port = Integer.parseInt(args[0]);
        }
        BillingServer service = new BillingServer(port);
        service.start();
        System.out.println("Helios Billing listening on http://localhost:" + port);
        System.out.println("  GET  /health");
        System.out.println("  POST /invoice");
    }
}
