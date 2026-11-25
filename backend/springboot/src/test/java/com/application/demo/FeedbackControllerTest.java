package com.application.demo;

import static org.junit.jupiter.api.Assertions.*;

import java.io.ByteArrayInputStream;
import java.io.ByteArrayOutputStream;
import java.util.Properties;
import jakarta.mail.Multipart;
import jakarta.mail.Part;
import jakarta.mail.Session;
import jakarta.mail.internet.MimeMessage;
import org.junit.jupiter.api.Test;
import org.springframework.mail.javamail.JavaMailSenderImpl;

class FeedbackControllerTest {
    @Test
    void sendsUtf8HtmlAndPlainTextWithReplyTo() throws Exception {
        Session session = Session.getInstance(new Properties());
        MimeMessage[] sent = new MimeMessage[1];
        JavaMailSenderImpl sender = new JavaMailSenderImpl() {
            @Override
            public void send(MimeMessage message) {
                sent[0] = message;
            }
        };
        FeedbackData feedback = new FeedbackData(
            "Błąd mapy & wyszukiwania", "tester@example.com", "/mapa?x=1&y=2",
            "Nie działa <przycisk>.\r\nZażółć gęślą jaźń."
        );

        assertTrue(new FeedbackController(sender).sendFeedbackEmail(feedback));
        assertNotNull(sent[0]);

        // Read the serialized email, including MIME content types and character encoding.
        ByteArrayOutputStream bytes = new ByteArrayOutputStream();
        sent[0].writeTo(bytes);
        MimeMessage received = new MimeMessage(session, new ByteArrayInputStream(bytes.toByteArray()));
        assertEquals("[Feedback] " + feedback.subject(), received.getSubject());
        assertEquals(feedback.email(), received.getReplyTo()[0].toString());
        String html = body(received, "text/html");
        String plain = body(received, "text/plain");
        assertNotNull(html);
        assertNotNull(plain);
        assertTrue(html.contains("Błąd mapy &amp; wyszukiwania"));
        assertTrue(html.contains("/mapa?x=1&amp;y=2"));
        assertTrue(html.contains("Nie działa &lt;przycisk&gt;.<br>Zażółć gęślą jaźń."));
        assertTrue(plain.contains(feedback.message()));
        assertFalse(html.contains("<przycisk>"));
    }

    @Test
    void treatsUserMarkupAndPlaceholderSyntaxAsLiteralText() throws Exception {
        String html = FeedbackEmailTemplate.render(new FeedbackData(
            "{{message}}", "tester@example.com", "{{subject}}",
            "<script>alert(1)</script>\n{{subject}} $5 \\"
        ));

        assertFalse(html.contains("<script>"));
        assertTrue(html.contains("&lt;script&gt;alert(1)&lt;/script&gt;<br>{{subject}} $5 \\"));
        assertTrue(html.contains(">{{message}}</h2>"));
    }

    private static String body(Part part, String contentType) throws Exception {
        if (part.isMimeType(contentType)) {
            return (String) part.getContent();
        }
        if (part.getContent() instanceof Multipart multipart) {
            for (int index = 0; index < multipart.getCount(); index++) {
                String text = body(multipart.getBodyPart(index), contentType);
                if (text != null) {
                    return text;
                }
            }
        }
        return null;
    }
}
