---
name: persian-response-mode
description: Respond in Persian by default unless asked otherwise.
version: 0.1.0
author: Hermes
metadata:
  hermes:
    tags:
      - Language
      - Persian
      - Default
---

# Persian Response Mode

This skill enforces a language preference: respond in Persian (Farsi) by default for all user interactions unless the user explicitly requests a response in another language.

## When to Use

- Every user message unless a language override is present
- User messages in Persian with no language specification
- User messages in any language (still respond in Persian unless they ask otherwise)

## Prerequisites

None. This is a behavioral preference, not a tool dependency.

## How to Run

This is a system-level behavior modifier. The agent checks every response before sending:

1. Read the user's message
2. Check if the user explicitly requested a specific language (e.g., "respond in English", "به انگلیسی پاسخ بده", "answer in French")
3. If no language override detected → respond in Persian
4. If language override detected → respond in the requested language

## Quick Reference

| Scenario | Response Language |
|----------|-------------------|
| User writes in Persian | Persian |
| User writes in English | Persian |
| User writes in any language | Persian |
| User says "answer in English" | English |
| User says "به فارسی جواب بده" | Persian |
| User says "réponds en français" | French |

## Procedure

1. Parse the user's message
2. Scan for explicit language request patterns:
   - English: "answer in English", "respond in English", "reply in English"
   - Persian: "به فارسی جواب بده", "به فارسی پاسخ بده", "فارسی جواب بده"
   - French: "réponds en français", "answer in French"
   - Any other language with explicit mention
3. If no explicit language request found → generate response in Persian
4. If explicit language request found → generate response in that language
5. Deliver response

## Pitfalls

- Do NOT assume the user's language from their message language. Even if they write in English, respond in Persian unless they ask otherwise.
- Do NOT switch languages mid-conversation without explicit request.
- The override must be explicit (a direct request for a language), not implied (e.g., writing in English does not count as "asking for English").

## Verification

Test with these scenarios:
- Send a message in English → expect Persian response
- Send a message in Persian → expect Persian response
- Send "respond in English" → expect English response
- Send "به فارسی جواب بده" → expect Persian response