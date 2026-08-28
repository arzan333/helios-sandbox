package com.helios.billing;

import org.junit.jupiter.api.Test;

import java.util.List;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;

class InvoiceCalculatorTest {

    @Test
    void subtotalIsQuantityTimesUnitPrice() {
        InvoiceCalculator.Invoice invoice = InvoiceCalculator.calculate(
                "ORD-1002", "GBP",
                List.of(new InvoiceCalculator.Line("HG-SOAP-250", 100, 189)));
        assertEquals(18900, invoice.subtotalPence);
    }

    @Test
    void taxIsTwentyPercentOfSubtotal() {
        InvoiceCalculator.Invoice invoice = InvoiceCalculator.calculate(
                "ORD-1002", "GBP",
                List.of(new InvoiceCalculator.Line("HG-SOAP-250", 100, 189)));
        assertEquals(3780, invoice.taxPence);
        assertEquals(22680, invoice.totalPence);
    }

    @Test
    void multipleLinesAreSummed() {
        InvoiceCalculator.Invoice invoice = InvoiceCalculator.calculate(
                "ORD-1001", "GBP",
                List.of(
                        new InvoiceCalculator.Line("HG-CLEAN-500", 24, 249),
                        new InvoiceCalculator.Line("HG-CLOTH-10", 6, 899)));
        assertEquals(5976 + 5394, invoice.subtotalPence);
    }

    @Test
    void taxRoundsHalvesUp() {
        // subtotal 1 penny -> tax is 0.2 pence -> rounds to 0
        assertEquals(0, InvoiceCalculator.roundHalfUp(1 * 20, 100));
        // subtotal 3 pence -> 0.6 -> rounds to 1
        assertEquals(1, InvoiceCalculator.roundHalfUp(3 * 20, 100));
        // exact half rounds away from zero
        assertEquals(3, InvoiceCalculator.roundHalfUp(250, 100));
    }

    @Test
    void emptyLinesAreRejected() {
        assertThrows(IllegalArgumentException.class,
                () -> InvoiceCalculator.calculate("ORD-1", "GBP", List.of()));
    }

    @Test
    void zeroQuantityIsRejected() {
        assertThrows(IllegalArgumentException.class,
                () -> new InvoiceCalculator.Line("HG-SOAP-250", 0, 189));
    }

    @Test
    void negativePriceIsRejected() {
        assertThrows(IllegalArgumentException.class,
                () -> new InvoiceCalculator.Line("HG-SOAP-250", 1, -5));
    }
}
