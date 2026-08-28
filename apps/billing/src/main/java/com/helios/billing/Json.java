package com.helios.billing;

import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

/**
 * A very small JSON reader and writer.
 *
 * <p>Billing exchanges one flat request and one flat response with OrderCore, so a full
 * JSON library would be more code to install than to replace. This handles objects,
 * arrays, strings and whole numbers, which is everything the contract uses. It is not a
 * general purpose parser and is not meant to become one.
 */
final class Json {

    private final String text;
    private int pos;

    private Json(String text) {
        this.text = text;
    }

    static Map<String, Object> parseObject(String text) {
        Json parser = new Json(text);
        parser.skipWhitespace();
        Object value = parser.readValue();
        if (!(value instanceof Map)) {
            throw new IllegalArgumentException("Expected a JSON object at the top level");
        }
        @SuppressWarnings("unchecked")
        Map<String, Object> result = (Map<String, Object>) value;
        return result;
    }

    private Object readValue() {
        skipWhitespace();
        if (pos >= text.length()) {
            throw new IllegalArgumentException("Unexpected end of input");
        }
        char c = text.charAt(pos);
        switch (c) {
            case '{':
                return readObject();
            case '[':
                return readArray();
            case '"':
                return readString();
            case 't':
                expect("true");
                return Boolean.TRUE;
            case 'f':
                expect("false");
                return Boolean.FALSE;
            case 'n':
                expect("null");
                return null;
            default:
                return readNumber();
        }
    }

    private Map<String, Object> readObject() {
        Map<String, Object> map = new LinkedHashMap<>();
        pos++; // consume {
        skipWhitespace();
        if (peek() == '}') {
            pos++;
            return map;
        }
        while (true) {
            skipWhitespace();
            String key = readString();
            skipWhitespace();
            if (peek() != ':') {
                throw new IllegalArgumentException("Expected ':' after key " + key);
            }
            pos++;
            map.put(key, readValue());
            skipWhitespace();
            char next = peek();
            pos++;
            if (next == '}') {
                return map;
            }
            if (next != ',') {
                throw new IllegalArgumentException("Expected ',' or '}' in object");
            }
        }
    }

    private List<Object> readArray() {
        List<Object> list = new ArrayList<>();
        pos++; // consume [
        skipWhitespace();
        if (peek() == ']') {
            pos++;
            return list;
        }
        while (true) {
            list.add(readValue());
            skipWhitespace();
            char next = peek();
            pos++;
            if (next == ']') {
                return list;
            }
            if (next != ',') {
                throw new IllegalArgumentException("Expected ',' or ']' in array");
            }
        }
    }

    private String readString() {
        if (peek() != '"') {
            throw new IllegalArgumentException("Expected a string at position " + pos);
        }
        pos++;
        StringBuilder sb = new StringBuilder();
        while (pos < text.length()) {
            char c = text.charAt(pos++);
            if (c == '"') {
                return sb.toString();
            }
            if (c == '\\') {
                char escaped = text.charAt(pos++);
                switch (escaped) {
                    case 'n': sb.append('\n'); break;
                    case 't': sb.append('\t'); break;
                    case 'r': sb.append('\r'); break;
                    case 'b': sb.append('\b'); break;
                    case 'f': sb.append('\f'); break;
                    case 'u':
                        sb.append((char) Integer.parseInt(text.substring(pos, pos + 4), 16));
                        pos += 4;
                        break;
                    default: sb.append(escaped);
                }
            } else {
                sb.append(c);
            }
        }
        throw new IllegalArgumentException("Unterminated string");
    }

    private Object readNumber() {
        int start = pos;
        while (pos < text.length() && "-+.eE0123456789".indexOf(text.charAt(pos)) >= 0) {
            pos++;
        }
        String raw = text.substring(start, pos);
        if (raw.isEmpty()) {
            throw new IllegalArgumentException("Expected a number at position " + start);
        }
        if (raw.contains(".") || raw.contains("e") || raw.contains("E")) {
            return Double.parseDouble(raw);
        }
        return Long.parseLong(raw);
    }

    private void expect(String literal) {
        if (!text.startsWith(literal, pos)) {
            throw new IllegalArgumentException("Expected " + literal + " at position " + pos);
        }
        pos += literal.length();
    }

    private char peek() {
        if (pos >= text.length()) {
            throw new IllegalArgumentException("Unexpected end of input");
        }
        return text.charAt(pos);
    }

    private void skipWhitespace() {
        while (pos < text.length() && Character.isWhitespace(text.charAt(pos))) {
            pos++;
        }
    }

    // ---------- writing ----------

    static String escape(String value) {
        StringBuilder sb = new StringBuilder();
        for (char c : value.toCharArray()) {
            switch (c) {
                case '"': sb.append("\\\""); break;
                case '\\': sb.append("\\\\"); break;
                case '\n': sb.append("\\n"); break;
                case '\r': sb.append("\\r"); break;
                case '\t': sb.append("\\t"); break;
                default:
                    if (c < 0x20) {
                        sb.append(String.format("\\u%04x", (int) c));
                    } else {
                        sb.append(c);
                    }
            }
        }
        return sb.toString();
    }

    /** Reads a required whole number, accepting either integer or decimal input. */
    static long requireLong(Map<String, Object> source, String key) {
        Object value = source.get(key);
        if (value == null) {
            throw new IllegalArgumentException("Missing field: " + key);
        }
        if (value instanceof Long) {
            return (Long) value;
        }
        if (value instanceof Double) {
            return Math.round((Double) value);
        }
        throw new IllegalArgumentException("Field " + key + " must be a number");
    }

    static String requireString(Map<String, Object> source, String key) {
        Object value = source.get(key);
        if (!(value instanceof String) || ((String) value).isEmpty()) {
            throw new IllegalArgumentException("Missing field: " + key);
        }
        return (String) value;
    }
}
