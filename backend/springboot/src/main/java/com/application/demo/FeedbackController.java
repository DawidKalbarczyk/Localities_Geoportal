package com.application.demo;

import java.nio.charset.StandardCharsets;
import jakarta.mail.internet.MimeMessage;
import org.springframework.mail.javamail.JavaMailSender;
import org.springframework.mail.javamail.MimeMessageHelper;
import org.springframework.web.bind.annotation.*;

record FeedbackData(
    String subject,
    String email,
    String url,
    String message
) {}

@RestController
@RequestMapping("/feedback")
public class FeedbackController {
    private final JavaMailSender mailSender;

    public FeedbackController(JavaMailSender mailSender) {
        this.mailSender = mailSender;
    }

    @PostMapping("/send-email")
    public boolean sendFeedbackEmail(@RequestBody FeedbackData feedbackData) {
        try {
            MimeMessage mail = mailSender.createMimeMessage();
            MimeMessageHelper helper = new MimeMessageHelper(mail, true, StandardCharsets.UTF_8.name());

            helper.setFrom("k_kalbarczyk@o2.pl");
            helper.setTo("k_kalbarczyk@o2.pl");
            helper.setReplyTo(feedbackData.email());
            helper.setSubject("[Feedback] " + feedbackData.subject());
            helper.setText(
                "NEW BUG REPORT\n\n"
                + "Subject: " + feedbackData.subject() + "\n"
                + "Contact email: " + feedbackData.email() + "\n"
                + "Page URL: " + feedbackData.url() + "\n"
                + "Message:\n" + feedbackData.message() + "\n\n"
                + "Reply to this email to contact the person who submitted the report.\n",
                FeedbackEmailTemplate.render(feedbackData)
            );

            mailSender.send(mail);
        } catch (Exception e) {
            e.printStackTrace();
            return false;
        }
        return true;
    }
}
