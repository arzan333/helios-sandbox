package com.helios.billing;

import org.junit.jupiter.api.Test;

import java.util.List;
import java.util.Map;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;

class JsonTest {

    @Test
    void readsNestedObjectsAndArrays() {
        Map<String, Object> parsed = Json.parseObject(
                "{\"a\":1,\"b\":{\"c\":\"d\"},\"e\":[1,2,3]}");
        assertEquals(1L, parsed.get("a"));
        assertEquals("d", ((Map<?, ?>) parsed.get("b")).get("c"));
        assertEquals(3, ((List<?>) parsed.get("e")).size());
    }

    @Test
    void handlesEscapedCharactersInStrings() {
        Map<String, Object> parsed = Json.parseObject("{\"a\":\"line\\nbreak \\\"quoted\\\"\"}");
        assertEquals("line\nbreak \"quoted\"", parsed.get("a"));
    }

    @Test
    void escapesOnTheWayOut() {
        assertEquals("say \\\"hi\\\"", Json.escape("say \"hi\""));
        assertEquals("a\\nb", Json.escape("a\nb"));
    }

    @Test
    void acceptsDecimalWhereWholeNumberExpected() {
        Map<String, Object> parsed = Json.parseObject("{\"n\":42.0}");
        assertEquals(42L, Json.requireLong(parsed, "n"));
    }

    @Test
    void rejectsATopLevelArray() {
        assertThrows(IllegalArgumentException.class, () -> Json.parseObject("[1,2]"));
    }

    @Test
    void rejectsMissingRequiredFields() {
        Map<String, Object> parsed = Json.parseObject("{}");
        assertThrows(IllegalArgumentException.class, () -> Json.requireString(parsed, "sku"));
        assertThrows(IllegalArgumentException.class, () -> Json.requireLong(parsed, "quantity"));
    }
}
