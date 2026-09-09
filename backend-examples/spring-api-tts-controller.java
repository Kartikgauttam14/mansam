/*
 * Copy this class into the existing Spring Boot backend and change the package
 * name to match that backend. This is a controller, not a separate server.
 */
package com.example.mansam.api;

import java.io.IOException;
import java.util.Locale;

import org.springframework.http.CacheControl;
import org.springframework.http.HttpHeaders;
import org.springframework.http.HttpStatus;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import software.amazon.awssdk.auth.credentials.DefaultCredentialsProvider;
import software.amazon.awssdk.core.ResponseInputStream;
import software.amazon.awssdk.regions.Region;
import software.amazon.awssdk.services.polly.PollyClient;
import software.amazon.awssdk.services.polly.model.Engine;
import software.amazon.awssdk.services.polly.model.OutputFormat;
import software.amazon.awssdk.services.polly.model.SynthesizeSpeechRequest;
import software.amazon.awssdk.services.polly.model.SynthesizeSpeechResponse;
import software.amazon.awssdk.services.polly.model.VoiceId;

@RestController
public class TtsController {
    private static final int MAX_TEXT_LENGTH = 1400;

    private final PollyClient polly = PollyClient.builder()
        .region(Region.of(System.getenv().getOrDefault("AWS_REGION", "me-south-1")))
        .credentialsProvider(DefaultCredentialsProvider.create())
        .build();

    @GetMapping(value = "/api/tts", produces = "audio/mpeg")
    public ResponseEntity<byte[]> synthesize(
        @RequestParam("q") String text,
        @RequestParam(value = "tl", defaultValue = "ar") String language
    ) throws IOException {
        String cleanText = text == null ? "" : text.trim();

        if (cleanText.isEmpty()) {
            return ResponseEntity.badRequest().build();
        }
        if (cleanText.length() > MAX_TEXT_LENGTH) {
            return ResponseEntity.status(HttpStatus.PAYLOAD_TOO_LARGE).build();
        }

        boolean isArabic = language.toLowerCase(Locale.ROOT).startsWith("ar");
        SynthesizeSpeechRequest request = SynthesizeSpeechRequest.builder()
            .text(cleanText)
            .outputFormat(OutputFormat.MP3)
            .voiceId(isArabic ? VoiceId.ZEINA : VoiceId.JOANNA)
            .engine(Engine.STANDARD)
            .build();

        try (ResponseInputStream<SynthesizeSpeechResponse> audio = polly.synthesizeSpeech(request)) {
            byte[] mp3 = audio.readAllBytes();

            return ResponseEntity.ok()
                .contentType(MediaType.valueOf("audio/mpeg"))
                .cacheControl(CacheControl.maxAge(java.time.Duration.ofDays(1)).cachePublic())
                .header(HttpHeaders.CONTENT_LENGTH, String.valueOf(mp3.length))
                .body(mp3);
        }
    }
}
