package com.helios.billing;

import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

/**
 * Contract tests. These lock down the exact field names OrderCore sends and expects.
 * If Week 3 changes the contract, these fail first - which is the intended lesson.
 */
class BillingServerTest {

    private static final String REQUEST = "{"
            + "\"orderId\":\"ORD-1002\","
            + "\"currency\":\"GBP\","
            + "\"lines\":[{\"sku\":\"HG-SOAP-250\",\"quantity\":100,\"unitPricePence\":189}]"
            + "}";

    @Test
    void parsesTheOrderCoreRequestShape() {
        InvoiceCalculator.Invoice invoice = BillingServer.invoiceFromRequest(REQUEST);
        assertEquals("ORD-1002", invoice.orderId);
        assertEquals("GBP", invoice.currency);
        assertEquals(18900, invoice.subtotalPence);
    }

    @Test
    void producesTheResponseShapeOrderCoreExpects() {
        String json = BillingServer.invoiceFromRequest(REQUEST).toJson();
        assertTrue(json.contains("\"orderId\":\"ORD-1002\""));
        assertTrue(json.contains("\"subtotalPence\":18900"));
        assertTrue(json.contains("\"taxPence\":3780"));
        assertTrue(json.contains("\"totalPence\":22680"));
        assertTrue(json.contains("\"currency\":\"GBP\""));
    }

    @Test
    void currencyDefaultsToGbpWhenOmitted() {
        String request = "{\"orderId\":\"ORD-1\",\"lines\":"
                + "[{\"sku\":\"A\",\"quantity\":1,\"unitPricePence\":100}]}";
        assertEquals("GBP", BillingServer.invoiceFromRequest(request).currency);
    }

    @Test
    void missingOrderIdIsRejected() {
        String request = "{\"lines\":[{\"sku\":\"A\",\"quantity\":1,\"unitPricePence\":100}]}";
        assertThrows(IllegalArgumentException.class,
                () -> BillingServer.invoiceFromRequest(request));
    }

    @Test
    void missingLinesIsRejected() {
        assertThrows(IllegalArgumentException.class,
                () -> BillingServer.invoiceFromRequest("{\"orderId\":\"ORD-1\"}"));
    }

    @Test
    void malformedJsonIsRejected() {
        assertThrows(IllegalArgumentException.class,
                () -> BillingServer.invoiceFromRequest("{\"orderId\":"));
    }
}
