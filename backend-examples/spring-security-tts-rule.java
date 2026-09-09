/*
 * Add the marked requestMatcher to the EXISTING Spring SecurityFilterChain.
 * Do not create a second filter chain just for this file.
 */

import org.springframework.http.HttpMethod;

http.authorizeHttpRequests(authorize -> authorize
    .requestMatchers(HttpMethod.GET, "/api/tts").permitAll()
    // Keep the backend's existing authorization rules below this line.
    .anyRequest().authenticated()
);

/*
 * For legacy Spring Security configurations, the equivalent is:
 *
 * http.authorizeRequests()
 *     .antMatchers("/api/tts").permitAll()
 *     .anyRequest().authenticated();
 */
