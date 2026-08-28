package com.helios.billing;

import java.util.List;
import java.util.Map;

/**
 * Works out what an order costs.
 *
 * <p>All money is in pence as a whole number. Nothing here uses floating point, because
 * rounding differences between Shop, OrderCore and Billing are a defect class this
 * training environment deliberately avoids having by accident.
 */
public final class InvoiceCalculator {

    /** UK standard rate, expressed as a whole percentage. */
    public static final int TAX_RATE_PERCENT = 20;

    private InvoiceCalculator() {
    }

    /** A single order line as it arrives from OrderCore. */
    public static final class Line {
        public final String sku;
        public final long quantity;
        public final long unitPricePence;

        public Line(String sku, long quantity, long unitPricePence) {
            if (sku == null || sku.isEmpty()) {
                throw new IllegalArgumentException("sku is required");
            }
            if (quantity <= 0) {
                throw new IllegalArgumentException("quantity must be greater than zero");
            }
            if (unitPricePence < 0) {
                throw new IllegalArgumentException("unitPricePence cannot be negative");
            }
            this.sku = sku;
            this.quantity = quantity;
            this.unitPricePence = unitPricePence;
        }

        public long totalPence() {
            return quantity * unitPricePence;
        }

        static Line fromMap(Map<String, Object> raw) {
            return new Line(
                    Json.requireString(raw, "sku"),
                    Json.requireLong(raw, "quantity"),
                    Json.requireLong(raw, "unitPricePence"));
        }
    }

    /** The calculated result returned to OrderCore. */
    public static final class Invoice {
        public final String orderId;
        public final String currency;
        public final long subtotalPence;
        public final long taxPence;
        public final long totalPence;

        Invoice(String orderId, String currency, long subtotalPence, long taxPence, long totalPence) {
            this.orderId = orderId;
            this.currency = currency;
            this.subtotalPence = subtotalPence;
            this.taxPence = taxPence;
            this.totalPence = totalPence;
        }

        public String toJson() {
            return "{"
                    + "\"orderId\":\"" + Json.escape(orderId) + "\","
                    + "\"currency\":\"" + Json.escape(currency) + "\","
                    + "\"subtotalPence\":" + subtotalPence + ","
                    + "\"taxPence\":" + taxPence + ","
                    + "\"totalPence\":" + totalPence
                    + "}";
        }
    }

    public static Invoice calculate(String orderId, String currency, List<Line> lines) {
        if (lines == null || lines.isEmpty()) {
            throw new IllegalArgumentException("at least one line is required");
        }
        long subtotal = 0;
        for (Line line : lines) {
            subtotal += line.totalPence();
        }
        long tax = roundHalfUp(subtotal * TAX_RATE_PERCENT, 100);
        return new Invoice(orderId, currency, subtotal, tax, subtotal + tax);
    }

    /** Integer division that rounds halves away from zero, so 2.5 becomes 3. */
    static long roundHalfUp(long numerator, long denominator) {
        if (denominator == 0) {
            throw new IllegalArgumentException("denominator cannot be zero");
        }
        return (numerator + denominator / 2) / denominator;
    }
}
