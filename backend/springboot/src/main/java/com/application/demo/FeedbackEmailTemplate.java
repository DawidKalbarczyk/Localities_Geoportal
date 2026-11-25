package com.application.demo;

import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.util.Map;
import java.util.Objects;
import java.util.regex.Matcher;
import java.util.regex.Pattern;
import org.springframework.core.io.ClassPathResource;
import org.springframework.web.util.HtmlUtils;

final class FeedbackEmailTemplate {
    private static final Pattern PLACEHOLDER = Pattern.compile("\\{\\{(subject|email|url|message)\\}\\}");

    private FeedbackEmailTemplate() {}

    static String render(FeedbackData feedback) throws IOException {
        String template = new ClassPathResource("templates/mail/feedback.html")
            .getContentAsString(StandardCharsets.UTF_8);
        Map<String, String> fields = Map.of(
            "subject", escape(feedback.subject()),
            "email", escape(feedback.email()),
            "url", escape(feedback.url()),
            "message", escape(feedback.message()).replace("\r\n", "\n").replace('\r', '\n').replace("\n", "<br>")
        );

        // Replace once so placeholders inside user input remain literal text.
        return PLACEHOLDER.matcher(template)
            .replaceAll(match -> Matcher.quoteReplacement(fields.get(match.group(1))));
    }

    private static String escape(String value) {
        return HtmlUtils.htmlEscape(Objects.toString(value, ""), StandardCharsets.UTF_8.name());
    }
}
